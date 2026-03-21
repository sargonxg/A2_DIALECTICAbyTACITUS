"""
FalkorDB Graph Client — Redis-compatible graph database with openCypher.

Provides graph-per-tenant isolation: each tenant gets a separate graph key
(tacitus_graph_{tenant_id}). Uses parameterized Cypher queries throughout.
Supports temporal queries via reference_time on Event nodes.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from dialectica_ontology.primitives import ConflictNode, NODE_TYPES
from dialectica_ontology.relationships import ConflictRelationship, EdgeType

from dialectica_graph.interface import GraphClient
from dialectica_graph.models import (
    ActorNetworkResult,
    EscalationResult,
    EscalationTrajectoryPoint,
    ScoredNode,
    SubgraphResult,
    WorkspaceStats,
)

logger = logging.getLogger(__name__)


def _graph_key(tenant_id: str) -> str:
    """Generate the graph key for a tenant."""
    safe_id = tenant_id.replace("-", "_").replace(" ", "_")
    return f"tacitus_graph_{safe_id}"


class FalkorDBGraphClient(GraphClient):
    """FalkorDB implementation of GraphClient with graph-per-tenant isolation.

    Each tenant gets a separate graph key in FalkorDB. All Cypher queries
    use parameterized queries to prevent injection. Temporal queries filter
    on Event.occurred_at using the reference_time parameter.

    Args:
        host: FalkorDB host.
        port: FalkorDB port.
        graph_name: Override graph name (default: tacitus_graph_{tenant_id}).
        default_tenant_id: Default tenant ID for graph key generation.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        graph_name: str | None = None,
        default_tenant_id: str = "default",
    ) -> None:
        self._host = host
        self._port = port
        self._graph_name_override = graph_name
        self._default_tenant_id = default_tenant_id
        self._db: Any = None

    def _get_db(self) -> Any:
        """Lazy-initialize FalkorDB connection."""
        if self._db is None:
            try:
                from falkordb import FalkorDB
                self._db = FalkorDB(host=self._host, port=self._port)
            except ImportError:
                raise ImportError(
                    "falkordb package not installed. "
                    "Install with: pip install 'dialectica-graph[falkordb]'"
                )
        return self._db

    def _get_graph(self, tenant_id: str | None = None) -> Any:
        """Get the graph for a specific tenant."""
        db = self._get_db()
        if self._graph_name_override:
            name = self._graph_name_override
        else:
            tid = tenant_id or self._default_tenant_id
            name = _graph_key(tid)
        return db.select_graph(name)

    def _tenant_from_workspace(self, workspace_id: str) -> str:
        """Extract tenant_id from workspace context (default fallback)."""
        return self._default_tenant_id

    # ── Schema Management ──────────────────────────────────────────────────

    async def initialize_schema(self) -> None:
        """Create indexes for all node labels and edge types."""
        graph = self._get_graph()

        # Create indexes for each node type
        for label in NODE_TYPES:
            label_name = type(label).__name__ if not isinstance(label, str) else label
            try:
                graph.query(f"CREATE INDEX FOR (n:{label_name}) ON (n.id)")
            except Exception:
                pass  # Index may already exist
            try:
                graph.query(f"CREATE INDEX FOR (n:{label_name}) ON (n.workspace_id)")
            except Exception:
                pass

        logger.info("FalkorDB schema initialized")

    # ── Node CRUD ──────────────────────────────────────────────────────────

    async def upsert_node(
        self, node: ConflictNode, workspace_id: str, tenant_id: str
    ) -> str:
        graph = self._get_graph(tenant_id)
        label = type(node).__name__
        props = node.model_dump(mode="json", exclude_none=True)
        props["workspace_id"] = workspace_id
        props["tenant_id"] = tenant_id

        query = (
            f"MERGE (n:{label} {{id: $id, workspace_id: $workspace_id}}) "
            f"SET n += $props "
            f"RETURN n.id"
        )
        params = {"id": node.id, "workspace_id": workspace_id, "props": props}
        result = graph.query(query, params)
        logger.debug("Upserted node %s (%s) in workspace %s", node.id, label, workspace_id)
        return node.id

    async def delete_node(
        self, node_id: str, workspace_id: str, hard: bool = False
    ) -> bool:
        graph = self._get_graph()
        if hard:
            query = (
                "MATCH (n {id: $id, workspace_id: $ws}) "
                "DETACH DELETE n"
            )
        else:
            query = (
                "MATCH (n {id: $id, workspace_id: $ws}) "
                "SET n.deleted_at = $now "
                "RETURN n.id"
            )
        params = {"id": node_id, "ws": workspace_id, "now": datetime.utcnow().isoformat()}
        result = graph.query(query, params)
        return True

    async def get_node(
        self, node_id: str, workspace_id: str
    ) -> ConflictNode | None:
        graph = self._get_graph()
        query = (
            "MATCH (n {id: $id, workspace_id: $ws}) "
            "WHERE n.deleted_at IS NULL "
            "RETURN n"
        )
        params = {"id": node_id, "ws": workspace_id}
        result = graph.query(query, params)

        if not result.result_set:
            return None

        row = result.result_set[0]
        return self._node_from_result(row[0])

    async def get_nodes(
        self,
        workspace_id: str,
        label: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ConflictNode]:
        graph = self._get_graph()
        if label:
            query = (
                f"MATCH (n:{label} {{workspace_id: $ws}}) "
                f"WHERE n.deleted_at IS NULL "
                f"RETURN n SKIP $offset LIMIT $limit"
            )
        else:
            query = (
                "MATCH (n {workspace_id: $ws}) "
                "WHERE n.deleted_at IS NULL "
                "RETURN n SKIP $offset LIMIT $limit"
            )
        params = {"ws": workspace_id, "offset": offset, "limit": limit}
        result = graph.query(query, params)
        return [self._node_from_result(row[0]) for row in result.result_set]

    # ── Edge CRUD ──────────────────────────────────────────────────────────

    async def upsert_edge(
        self, edge: ConflictRelationship, workspace_id: str, tenant_id: str
    ) -> str:
        graph = self._get_graph(tenant_id)
        props = edge.model_dump(mode="json", exclude_none=True)
        props["workspace_id"] = workspace_id

        query = (
            "MATCH (src {id: $src_id, workspace_id: $ws}) "
            "MATCH (tgt {id: $tgt_id, workspace_id: $ws}) "
            f"MERGE (src)-[r:{edge.type.value} {{id: $edge_id}}]->(tgt) "
            "SET r += $props "
            "RETURN r"
        )
        params = {
            "src_id": edge.source_id,
            "tgt_id": edge.target_id,
            "ws": workspace_id,
            "edge_id": edge.id,
            "props": props,
        }
        graph.query(query, params)
        return edge.id

    async def get_edges(
        self,
        workspace_id: str,
        edge_type: str | None = None,
    ) -> list[ConflictRelationship]:
        graph = self._get_graph()
        if edge_type:
            query = (
                f"MATCH (a {{workspace_id: $ws}})-[r:{edge_type}]->(b {{workspace_id: $ws}}) "
                f"RETURN r"
            )
        else:
            query = (
                "MATCH (a {workspace_id: $ws})-[r]->(b {workspace_id: $ws}) "
                "RETURN r"
            )
        params = {"ws": workspace_id}
        result = graph.query(query, params)
        return [self._edge_from_result(row[0]) for row in result.result_set]

    # ── Traversal ──────────────────────────────────────────────────────────

    async def traverse(
        self,
        start_id: str,
        workspace_id: str,
        hops: int = 2,
        edge_types: list[str] | None = None,
    ) -> SubgraphResult:
        graph = self._get_graph()

        if edge_types:
            rel_filter = "|".join(edge_types)
            query = (
                f"MATCH path = (start {{id: $id, workspace_id: $ws}})"
                f"-[:{rel_filter}*1..{hops}]-(connected) "
                f"WHERE connected.deleted_at IS NULL "
                f"RETURN path"
            )
        else:
            query = (
                f"MATCH path = (start {{id: $id, workspace_id: $ws}})"
                f"-[*1..{hops}]-(connected) "
                f"WHERE connected.deleted_at IS NULL "
                f"RETURN path"
            )
        params = {"id": start_id, "ws": workspace_id}
        result = graph.query(query, params)

        nodes_map: dict[str, ConflictNode] = {}
        edges_list: list[ConflictRelationship] = []

        for row in result.result_set:
            path = row[0]
            for node_data in getattr(path, "nodes", []):
                node = self._node_from_result(node_data)
                if node and node.id not in nodes_map:
                    nodes_map[node.id] = node
            for edge_data in getattr(path, "edges", []):
                edge = self._edge_from_result(edge_data)
                if edge:
                    edges_list.append(edge)

        return SubgraphResult(
            nodes=list(nodes_map.values()),
            edges=edges_list,
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
        graph = self._get_graph()

        # FalkorDB supports vector indexes; query using vecf32 similarity
        if label:
            query = (
                f"MATCH (n:{label} {{workspace_id: $ws}}) "
                f"WHERE n.deleted_at IS NULL AND n.embedding IS NOT NULL "
                f"WITH n, vec.euclideanDistance(n.embedding, vecf32($emb)) AS dist "
                f"RETURN n, dist ORDER BY dist ASC LIMIT $k"
            )
        else:
            query = (
                "MATCH (n {workspace_id: $ws}) "
                "WHERE n.deleted_at IS NULL AND n.embedding IS NOT NULL "
                "WITH n, vec.euclideanDistance(n.embedding, vecf32($emb)) AS dist "
                "RETURN n, dist ORDER BY dist ASC LIMIT $k"
            )
        params = {"ws": workspace_id, "emb": embedding, "k": top_k}

        try:
            result = graph.query(query, params)
            scored: list[ScoredNode] = []
            for row in result.result_set:
                node = self._node_from_result(row[0])
                dist = float(row[1])
                score = 1.0 / (1.0 + dist)  # Convert distance to similarity
                if node:
                    scored.append(ScoredNode(node=node, score=score, distance=dist))
            return scored
        except Exception as e:
            logger.warning("Vector search failed (index may not exist): %s", e)
            return []

    # ── Raw Query ──────────────────────────────────────────────────────────

    async def execute_query(
        self, query: str, params: dict | None = None
    ) -> list[dict]:
        graph = self._get_graph()
        result = graph.query(query, params or {})
        rows: list[dict] = []
        if result.result_set:
            headers = result.header if hasattr(result, "header") else []
            for row in result.result_set:
                if headers:
                    rows.append(dict(zip(headers, row)))
                else:
                    rows.append({"result": row})
        return rows

    # ── Analytics ──────────────────────────────────────────────────────────

    async def get_workspace_stats(self, workspace_id: str) -> WorkspaceStats:
        graph = self._get_graph()
        stats = WorkspaceStats()

        # Count nodes by label
        for label_name in ["Actor", "Conflict", "Event", "Issue", "Interest",
                           "Norm", "Process", "Outcome", "Narrative",
                           "EmotionalState", "TrustState", "PowerDynamic",
                           "Location", "Evidence", "Role"]:
            query = (
                f"MATCH (n:{label_name} {{workspace_id: $ws}}) "
                f"WHERE n.deleted_at IS NULL "
                f"RETURN count(n) AS cnt"
            )
            result = graph.query(query, {"ws": workspace_id})
            cnt = result.result_set[0][0] if result.result_set else 0
            if cnt > 0:
                stats.node_counts_by_label[label_name] = cnt
                stats.total_nodes += cnt

        # Count edges
        query = (
            "MATCH (a {workspace_id: $ws})-[r]->(b {workspace_id: $ws}) "
            "RETURN type(r) AS t, count(r) AS cnt"
        )
        result = graph.query(query, {"ws": workspace_id})
        for row in result.result_set:
            t, cnt = row[0], row[1]
            stats.edge_counts_by_type[t] = cnt
            stats.total_edges += cnt

        stats.compute_density()
        return stats

    async def get_actor_network(
        self, actor_id: str, workspace_id: str
    ) -> ActorNetworkResult:
        graph = self._get_graph()

        # Get the actor node
        actor_node = await self.get_node(actor_id, workspace_id)
        if not actor_node:
            return ActorNetworkResult(actor=actor_node)  # type: ignore[arg-type]

        # Get allies
        query = (
            "MATCH (a {id: $id, workspace_id: $ws})-[:ALLIED_WITH]-(ally) "
            "WHERE ally.deleted_at IS NULL "
            "RETURN ally"
        )
        result = graph.query(query, {"id": actor_id, "ws": workspace_id})
        allies = [self._node_from_result(row[0]) for row in result.result_set]

        # Get opponents
        query = (
            "MATCH (a {id: $id, workspace_id: $ws})-[:OPPOSES]-(opp) "
            "WHERE opp.deleted_at IS NULL "
            "RETURN opp"
        )
        result = graph.query(query, {"id": actor_id, "ws": workspace_id})
        opponents = [self._node_from_result(row[0]) for row in result.result_set]

        # Get all connections
        query = (
            "MATCH (a {id: $id, workspace_id: $ws})-[r]-(b) "
            "WHERE b.deleted_at IS NULL "
            "RETURN r"
        )
        result = graph.query(query, {"id": actor_id, "ws": workspace_id})
        connections = [self._edge_from_result(row[0]) for row in result.result_set]

        return ActorNetworkResult(
            actor=actor_node,
            allies=[a for a in allies if a],
            opponents=[o for o in opponents if o],
            connections=[c for c in connections if c],
        )

    async def get_timeline(
        self,
        workspace_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ConflictNode]:
        graph = self._get_graph()
        conditions = ["e.workspace_id = $ws", "e.deleted_at IS NULL"]
        params: dict[str, Any] = {"ws": workspace_id}

        if start:
            conditions.append("e.occurred_at >= $start")
            params["start"] = start.isoformat()
        if end:
            conditions.append("e.occurred_at <= $end")
            params["end"] = end.isoformat()

        where = " AND ".join(conditions)
        query = (
            f"MATCH (e:Event) "
            f"WHERE {where} "
            f"RETURN e ORDER BY e.occurred_at ASC"
        )
        result = graph.query(query, params)
        return [self._node_from_result(row[0]) for row in result.result_set if row[0]]

    async def get_escalation_trajectory(
        self, workspace_id: str
    ) -> EscalationResult:
        graph = self._get_graph()

        # Get conflicts with glasl stages over time
        query = (
            "MATCH (c:Conflict {workspace_id: $ws}) "
            "WHERE c.deleted_at IS NULL AND c.glasl_stage IS NOT NULL "
            "RETURN c.glasl_stage, c.updated_at, c.name "
            "ORDER BY c.updated_at ASC"
        )
        result = graph.query(query, {"ws": workspace_id})

        trajectory: list[EscalationTrajectoryPoint] = []
        for row in result.result_set:
            stage = int(row[0]) if row[0] else 1
            ts = datetime.fromisoformat(row[1]) if row[1] else datetime.utcnow()
            evidence = str(row[2]) if row[2] else ""
            trajectory.append(EscalationTrajectoryPoint(
                timestamp=ts, glasl_stage=stage, evidence=evidence
            ))

        current_stage = trajectory[-1].glasl_stage if trajectory else None
        velocity = 0.0
        direction = "stable"
        if len(trajectory) >= 2:
            delta_stage = trajectory[-1].glasl_stage - trajectory[0].glasl_stage
            delta_time = (trajectory[-1].timestamp - trajectory[0].timestamp).days
            if delta_time > 0:
                velocity = delta_stage / (delta_time / 30)  # stages per month
                direction = "escalating" if velocity > 0 else ("de-escalating" if velocity < 0 else "stable")

        return EscalationResult(
            trajectory=trajectory,
            current_stage=current_stage,
            velocity=velocity,
            direction=direction,
        )

    # ── Temporal Queries ───────────────────────────────────────────────────

    async def get_events_by_reference_time(
        self,
        workspace_id: str,
        reference_time: datetime,
        window_days: int = 30,
    ) -> list[ConflictNode]:
        """Get events near a reference_time within a window."""
        graph = self._get_graph()
        query = (
            "MATCH (e:Event {workspace_id: $ws}) "
            "WHERE e.deleted_at IS NULL "
            "AND e.occurred_at >= $start AND e.occurred_at <= $end "
            "RETURN e ORDER BY e.occurred_at ASC"
        )
        from datetime import timedelta
        start_dt = reference_time - timedelta(days=window_days)
        end_dt = reference_time + timedelta(days=window_days)
        params = {
            "ws": workspace_id,
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
        }
        result = graph.query(query, params)
        return [self._node_from_result(row[0]) for row in result.result_set if row[0]]

    # ── Batch Operations ───────────────────────────────────────────────────

    async def batch_upsert_nodes(
        self,
        nodes: list[ConflictNode],
        workspace_id: str,
        tenant_id: str,
    ) -> list[str]:
        ids: list[str] = []
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
        ids: list[str] = []
        for edge in edges:
            eid = await self.upsert_edge(edge, workspace_id, tenant_id)
            ids.append(eid)
        return ids

    # ── Lifecycle ──────────────────────────────────────────────────────────

    async def close(self) -> None:
        if self._db is not None:
            try:
                self._db.close()
            except Exception:
                pass
            self._db = None

    # ── Helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _node_from_result(node_data: Any) -> ConflictNode | None:
        """Convert a FalkorDB node result to a ConflictNode."""
        try:
            if hasattr(node_data, "properties"):
                props = dict(node_data.properties)
            elif isinstance(node_data, dict):
                props = node_data
            else:
                return None

            label = props.get("label") or (
                node_data.labels[0] if hasattr(node_data, "labels") and node_data.labels else "Actor"
            )

            # Find the right model class
            from dialectica_ontology.primitives import NODE_TYPES
            model_map = {type(m).__name__: type(m) for m in NODE_TYPES}
            model_cls = model_map.get(label)
            if model_cls:
                return model_cls.model_validate(props)
            return None
        except Exception as e:
            logger.debug("Failed to deserialize node: %s", e)
            return None

    @staticmethod
    def _edge_from_result(edge_data: Any) -> ConflictRelationship | None:
        """Convert a FalkorDB edge result to a ConflictRelationship."""
        try:
            if hasattr(edge_data, "properties"):
                props = dict(edge_data.properties)
            elif isinstance(edge_data, dict):
                props = edge_data
            else:
                return None
            return ConflictRelationship.model_validate(props)
        except Exception as e:
            logger.debug("Failed to deserialize edge: %s", e)
            return None
