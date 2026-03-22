"""
Neo4j Graph Client — GraphClient implementation for Neo4j Aura / FalkorDB.

Uses:
  - neo4j Python driver (async Bolt protocol)
  - Cypher queries
  - db.index.vector.queryNodes() for vector search
  - MATCH path = (n)-[*1..N]->(m) for traversal
  - MERGE for upserts

Multi-tenant: All Cypher queries include {tenant_id: $tid} property filter.
Supports both Neo4j Aura and self-hosted FalkorDB (Cypher-compatible).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from neo4j import AsyncGraphDatabase, AsyncSession

from dialectica_graph.interface import GraphClient
from dialectica_graph.models import (
    ActorNetworkResult,
    EscalationResult,
    EscalationTrajectoryPoint,
    ScoredNode,
    SubgraphResult,
    WorkspaceStats,
)
from dialectica_ontology.primitives import NODE_TYPES, ConflictNode
from dialectica_ontology.relationships import ConflictRelationship, EdgeType

logger = logging.getLogger(__name__)

VECTOR_INDEX_NAME = "node_embedding_index"
VECTOR_DIMENSIONS = 768


def _node_to_props(node: ConflictNode, workspace_id: str, tenant_id: str) -> dict:
    """Serialize a ConflictNode to Neo4j property dict."""
    data = node.model_dump(exclude={"embedding", "metadata"})
    # Convert datetimes to ISO strings for Neo4j
    for k, v in list(data.items()):
        if isinstance(v, datetime):
            data[k] = v.isoformat()
        elif v is None:
            del data[k]
    data["workspace_id"] = workspace_id
    data["tenant_id"] = tenant_id
    if node.metadata:
        data["metadata_json"] = json.dumps(node.metadata)
    return data


def _record_to_node(record: dict) -> ConflictNode:
    """Deserialize a Neo4j record to a ConflictNode."""
    label = record.get("label", "")
    cls = NODE_TYPES.get(label, ConflictNode)
    props = dict(record)
    if "metadata_json" in props:
        props["metadata"] = json.loads(props.pop("metadata_json"))
    return cls.model_validate(props)


def _edge_to_props(edge: ConflictRelationship, workspace_id: str, tenant_id: str) -> dict:
    """Serialize a ConflictRelationship to Neo4j property dict."""
    return {
        "id": edge.id,
        "type": str(edge.type),
        "source_id": edge.source_id,
        "target_id": edge.target_id,
        "source_label": edge.source_label,
        "target_label": edge.target_label,
        "workspace_id": workspace_id,
        "tenant_id": tenant_id,
        "properties_json": json.dumps(edge.properties) if edge.properties else "{}",
        "weight": edge.weight,
        "confidence": edge.confidence,
        "temporal_start": edge.temporal_start.isoformat() if edge.temporal_start else None,
        "temporal_end": edge.temporal_end.isoformat() if edge.temporal_end else None,
        "source_text": edge.source_text,
    }


def _record_to_edge(record: dict) -> ConflictRelationship:
    """Deserialize a Neo4j record to a ConflictRelationship."""
    props_json = record.get("properties_json", "{}")
    properties = json.loads(props_json) if isinstance(props_json, str) else {}
    return ConflictRelationship(
        id=record["id"],
        type=EdgeType(record["type"]),
        source_id=record["source_id"],
        target_id=record["target_id"],
        source_label=record.get("source_label", ""),
        target_label=record.get("target_label", ""),
        workspace_id=record.get("workspace_id", ""),
        tenant_id=record.get("tenant_id", ""),
        properties=properties,
        weight=record.get("weight", 1.0),
        confidence=record.get("confidence", 1.0),
        source_text=record.get("source_text"),
    )


class Neo4jGraphClient(GraphClient):
    """Neo4j / FalkorDB implementation of GraphClient.

    Args:
        uri: Bolt URI (e.g., bolt://localhost:7687 or neo4j+s://xxx.databases.neo4j.io).
        username: Auth username.
        password: Auth password.
        database: Neo4j database name (default: neo4j).
    """

    def __init__(
        self,
        uri: str,
        username: str = "neo4j",
        password: str = "dialectica-dev",
        database: str = "neo4j",
    ) -> None:
        self._driver = AsyncGraphDatabase.driver(uri, auth=(username, password))
        self._database = database

    def _session(self) -> AsyncSession:
        return self._driver.session(database=self._database)

    # ── Schema Management ──────────────────────────────────────────────────

    async def initialize_schema(self) -> None:
        """Create constraints, indexes, and vector index in Neo4j."""
        node_labels = list(NODE_TYPES.keys())
        async with self._session() as session:
            # Uniqueness constraints for each node label
            for label in node_labels:
                await session.run(
                    f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE"
                )

            # Composite index on workspace_id + tenant_id for multi-tenant queries
            await session.run(
                "CREATE INDEX IF NOT EXISTS FOR (n:ConflictNode) ON (n.workspace_id, n.tenant_id)"
            )

            # Vector index for embedding search
            try:
                await session.run(
                    f"CREATE VECTOR INDEX {VECTOR_INDEX_NAME} IF NOT EXISTS "
                    f"FOR (n:ConflictNode) ON (n.embedding) "
                    f"OPTIONS {{indexConfig: {{`vector.dimensions`: {VECTOR_DIMENSIONS}, "
                    f"`vector.similarity_function`: 'cosine'}}}}"
                )
            except Exception:
                logger.warning("Vector index creation failed (may not be supported)")

        logger.info("Neo4j schema initialization complete")

    # ── Node CRUD ──────────────────────────────────────────────────────────

    async def upsert_node(self, node: ConflictNode, workspace_id: str, tenant_id: str) -> str:
        props = _node_to_props(node, workspace_id, tenant_id)
        label = node.label or "ConflictNode"
        cypher = (
            f"MERGE (n:{label} {{id: $id}}) "
            f"SET n += $props, n:ConflictNode, n.updated_at = datetime() "
        )
        # Handle embedding separately (as list property)
        if node.embedding:
            cypher += ", n.embedding = $embedding "

        params: dict[str, Any] = {"id": node.id, "props": props}
        if node.embedding:
            params["embedding"] = node.embedding

        async with self._session() as session:
            await session.run(cypher, params)
        return node.id

    async def delete_node(self, node_id: str, workspace_id: str, hard: bool = False) -> bool:
        async with self._session() as session:
            if hard:
                await session.run(
                    "MATCH (n:ConflictNode {id: $nid, workspace_id: $ws}) DETACH DELETE n",
                    {"nid": node_id, "ws": workspace_id},
                )
            else:
                await session.run(
                    "MATCH (n:ConflictNode {id: $nid, workspace_id: $ws}) "
                    "SET n.deleted_at = datetime(), n.updated_at = datetime()",
                    {"nid": node_id, "ws": workspace_id},
                )
        return True

    async def get_node(self, node_id: str, workspace_id: str) -> ConflictNode | None:
        cypher = (
            "MATCH (n:ConflictNode {id: $nid, workspace_id: $ws}) "
            "WHERE n.deleted_at IS NULL "
            "RETURN properties(n) AS props"
        )
        async with self._session() as session:
            result = await session.run(cypher, {"nid": node_id, "ws": workspace_id})
            record = await result.single()

        if record is None:
            return None
        return _record_to_node(record["props"])

    async def get_nodes(
        self,
        workspace_id: str,
        label: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ConflictNode]:
        match = f"(n:{label})" if label else "(n:ConflictNode)"
        cypher = (
            f"MATCH {match} "
            f"WHERE n.workspace_id = $ws AND n.deleted_at IS NULL "
            f"RETURN properties(n) AS props "
            f"ORDER BY n.created_at DESC "
            f"SKIP $offset LIMIT $limit"
        )
        async with self._session() as session:
            result = await session.run(
                cypher, {"ws": workspace_id, "offset": offset, "limit": limit}
            )
            records = await result.data()

        return [_record_to_node(r["props"]) for r in records]

    # ── Edge CRUD ──────────────────────────────────────────────────────────

    async def upsert_edge(
        self, edge: ConflictRelationship, workspace_id: str, tenant_id: str
    ) -> str:
        props = _edge_to_props(edge, workspace_id, tenant_id)
        edge_type = str(edge.type)
        cypher = (
            "MATCH (s:ConflictNode {id: $src_id, workspace_id: $ws}) "
            "MATCH (t:ConflictNode {id: $tgt_id, workspace_id: $ws}) "
            f"MERGE (s)-[r:{edge_type} {{id: $eid}}]->(t) "
            "SET r += $props"
        )
        async with self._session() as session:
            await session.run(
                cypher,
                {
                    "src_id": edge.source_id,
                    "tgt_id": edge.target_id,
                    "ws": workspace_id,
                    "eid": edge.id,
                    "props": props,
                },
            )
        return edge.id

    async def get_edges(
        self,
        workspace_id: str,
        edge_type: str | None = None,
    ) -> list[ConflictRelationship]:
        if edge_type:
            cypher = (
                f"MATCH (s)-[r:{edge_type}]->(t) "
                f"WHERE r.workspace_id = $ws "
                f"RETURN properties(r) AS props ORDER BY r.created_at DESC"
            )
        else:
            cypher = (
                "MATCH (s)-[r]->(t) "
                "WHERE r.workspace_id = $ws AND r.type IS NOT NULL "
                "RETURN properties(r) AS props ORDER BY r.created_at DESC"
            )

        async with self._session() as session:
            result = await session.run(cypher, {"ws": workspace_id})
            records = await result.data()

        return [_record_to_edge(r["props"]) for r in records]

    # ── Traversal ──────────────────────────────────────────────────────────

    async def traverse(
        self,
        start_id: str,
        workspace_id: str,
        hops: int = 2,
        edge_types: list[str] | None = None,
    ) -> SubgraphResult:
        if edge_types:
            rel_pattern = "|".join(f":{et}" for et in edge_types)
            rel = f"[r{rel_pattern}*1..{hops}]"
        else:
            rel = f"[r*1..{hops}]"

        cypher = (
            f"MATCH path = (start:ConflictNode {{id: $sid, workspace_id: $ws}})-{rel}-(end) "
            f"WHERE end.deleted_at IS NULL "
            f"UNWIND nodes(path) AS n "
            f"UNWIND relationships(path) AS e "
            f"RETURN DISTINCT properties(n) AS node_props, properties(e) AS edge_props"
        )
        seen_nodes: dict[str, ConflictNode] = {}
        seen_edges: dict[str, ConflictRelationship] = {}

        async with self._session() as session:
            result = await session.run(cypher, {"sid": start_id, "ws": workspace_id})
            records = await result.data()

        for rec in records:
            np = rec.get("node_props", {})
            ep = rec.get("edge_props", {})
            if np and np.get("id") and np["id"] not in seen_nodes:
                seen_nodes[np["id"]] = _record_to_node(np)
            if ep and ep.get("id") and ep["id"] not in seen_edges:
                seen_edges[ep["id"]] = _record_to_edge(ep)

        return SubgraphResult(
            nodes=list(seen_nodes.values()),
            edges=list(seen_edges.values()),
            metadata={"start_id": start_id, "hops": hops},
        )

    # ── Vector Search ──────────────────────────────────────────────────────

    async def vector_search(
        self,
        embedding: list[float],
        workspace_id: str,
        label: str | None = None,
        top_k: int = 10,
    ) -> list[ScoredNode]:
        # Use Neo4j vector index procedure
        cypher = (
            f"CALL db.index.vector.queryNodes('{VECTOR_INDEX_NAME}', $k, $emb) "
            "YIELD node, score "
            "WHERE node.workspace_id = $ws AND node.deleted_at IS NULL "
        )
        if label:
            cypher += "AND node.label = $lbl "
        cypher += "RETURN properties(node) AS props, score ORDER BY score DESC"

        params: dict[str, Any] = {"k": top_k, "emb": embedding, "ws": workspace_id}
        if label:
            params["lbl"] = label

        async with self._session() as session:
            result = await session.run(cypher, params)
            records = await result.data()

        return [
            ScoredNode(
                node=_record_to_node(r["props"]),
                score=r["score"],
                distance=1.0 - r["score"],
            )
            for r in records
        ]

    # ── Raw Query ──────────────────────────────────────────────────────────

    async def execute_query(self, query: str, params: dict | None = None) -> list[dict]:
        async with self._session() as session:
            result = await session.run(query, params or {})
            return await result.data()

    # ── Analytics ──────────────────────────────────────────────────────────

    async def get_workspace_stats(self, workspace_id: str) -> WorkspaceStats:
        stats = WorkspaceStats()

        node_cypher = (
            "MATCH (n:ConflictNode {workspace_id: $ws}) "
            "WHERE n.deleted_at IS NULL "
            "RETURN n.label AS label, count(*) AS cnt"
        )
        edge_cypher = (
            "MATCH ()-[r]->() WHERE r.workspace_id = $ws AND r.type IS NOT NULL "
            "RETURN r.type AS type, count(*) AS cnt"
        )

        async with self._session() as session:
            node_result = await session.run(node_cypher, {"ws": workspace_id})
            for record in await node_result.data():
                stats.node_counts_by_label[record["label"]] = record["cnt"]
                stats.total_nodes += record["cnt"]

            edge_result = await session.run(edge_cypher, {"ws": workspace_id})
            for record in await edge_result.data():
                stats.edge_counts_by_type[record["type"]] = record["cnt"]
                stats.total_edges += record["cnt"]

        stats.compute_density()
        return stats

    async def get_actor_network(self, actor_id: str, workspace_id: str) -> ActorNetworkResult:
        actor = await self.get_node(actor_id, workspace_id)
        if actor is None:
            raise ValueError(f"Actor {actor_id} not found")

        result = ActorNetworkResult(actor=actor)

        # Allies
        ally_cypher = (
            "MATCH (a:Actor {id: $aid, workspace_id: $ws})-[r:ALLIED_WITH]-(b:Actor) "
            "WHERE b.deleted_at IS NULL "
            "RETURN properties(b) AS props, properties(r) AS edge_props"
        )
        async with self._session() as session:
            ally_result = await session.run(ally_cypher, {"aid": actor_id, "ws": workspace_id})
            for rec in await ally_result.data():
                result.allies.append(_record_to_node(rec["props"]))
                result.connections.append(_record_to_edge(rec["edge_props"]))

        # Opponents
        opp_cypher = (
            "MATCH (a:Actor {id: $aid, workspace_id: $ws})-[r:OPPOSED_TO]-(b:Actor) "
            "WHERE b.deleted_at IS NULL "
            "RETURN properties(b) AS props, properties(r) AS edge_props"
        )
        async with self._session() as session:
            opp_result = await session.run(opp_cypher, {"aid": actor_id, "ws": workspace_id})
            for rec in await opp_result.data():
                result.opponents.append(_record_to_node(rec["props"]))
                result.connections.append(_record_to_edge(rec["edge_props"]))

        # Degree centrality
        degree_cypher = (
            "MATCH (a:Actor {id: $aid, workspace_id: $ws})-[r]-() RETURN count(r) AS degree"
        )
        total_cypher = (
            "MATCH (n:Actor {workspace_id: $ws}) "
            "WHERE n.deleted_at IS NULL RETURN count(n) AS total"
        )
        async with self._session() as session:
            deg = await session.run(degree_cypher, {"aid": actor_id, "ws": workspace_id})
            deg_data = await deg.single()
            tot = await session.run(total_cypher, {"ws": workspace_id})
            tot_data = await tot.single()

        degree = deg_data["degree"] if deg_data else 0
        total = tot_data["total"] if tot_data else 0
        result.centrality_scores["degree"] = degree / (total - 1) if total > 1 else 0.0

        return result

    async def get_timeline(
        self,
        workspace_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ConflictNode]:
        cypher = "MATCH (n:Event {workspace_id: $ws}) WHERE n.deleted_at IS NULL "
        params: dict[str, Any] = {"ws": workspace_id}

        if start:
            cypher += "AND n.occurred_at >= $start_ts "
            params["start_ts"] = start.isoformat()
        if end:
            cypher += "AND n.occurred_at <= $end_ts "
            params["end_ts"] = end.isoformat()

        cypher += "RETURN properties(n) AS props ORDER BY n.occurred_at ASC"

        async with self._session() as session:
            result = await session.run(cypher, params)
            records = await result.data()

        return [_record_to_node(r["props"]) for r in records]

    async def get_escalation_trajectory(self, workspace_id: str) -> EscalationResult:
        cypher = (
            "MATCH (n:Conflict {workspace_id: $ws}) "
            "WHERE n.deleted_at IS NULL AND n.glasl_stage IS NOT NULL "
            "RETURN properties(n) AS props ORDER BY n.created_at ASC"
        )
        async with self._session() as session:
            result = await session.run(cypher, {"ws": workspace_id})
            records = await result.data()

        trajectory: list[EscalationTrajectoryPoint] = []
        for rec in records:
            props = rec["props"]
            trajectory.append(
                EscalationTrajectoryPoint(
                    timestamp=datetime.fromisoformat(props["created_at"])
                    if isinstance(props.get("created_at"), str)
                    else datetime.utcnow(),
                    glasl_stage=int(props["glasl_stage"]),
                    evidence=props.get("name", props.get("id", "")),
                )
            )

        esc = EscalationResult(trajectory=trajectory)
        if trajectory:
            esc.current_stage = trajectory[-1].glasl_stage
            if len(trajectory) >= 2:
                delta = trajectory[-1].glasl_stage - trajectory[0].glasl_stage
                dt = (trajectory[-1].timestamp - trajectory[0].timestamp).days / 30.0
                esc.velocity = delta / dt if dt > 0 else 0.0
                esc.direction = (
                    "escalating" if delta > 0 else ("de-escalating" if delta < 0 else "stable")
                )

        return esc

    # ── Batch Operations ───────────────────────────────────────────────────

    async def batch_upsert_nodes(
        self,
        nodes: list[ConflictNode],
        workspace_id: str,
        tenant_id: str,
    ) -> list[str]:
        ids = []
        for node in nodes:
            nid = await self.upsert_node(node, workspace_id, tenant_id)
            ids.append(nid)
        return ids

    async def batch_upsert_edges(
        self,
        edges: list[ConflictRelationship],
        workspace_id: str,
        tenant_id: str,
    ) -> list[str]:
        ids = []
        for edge in edges:
            eid = await self.upsert_edge(edge, workspace_id, tenant_id)
            ids.append(eid)
        return ids

    # ── Lifecycle ──────────────────────────────────────────────────────────

    async def close(self) -> None:
        await self._driver.close()
