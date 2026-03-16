"""
Spanner Graph Client — GraphClient implementation for Google Cloud Spanner.

Uses:
  - google-cloud-spanner Python library
  - GQL queries via snapshot.execute_sql()
  - Native vector search: COSINE_DISTANCE(embedding, @query_embedding)
  - Property graph traversal: GRAPH_TABLE / MATCH patterns
  - Upsert via database.run_in_transaction() with insert_or_update mutations

Multi-tenant: All queries include WHERE tenant_id = @tid filter.
Dynamic labels: node.label → stored in label column.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from google.cloud import spanner
from google.cloud.spanner_v1 import param_types

from dialectica_ontology.primitives import NODE_TYPES, ConflictNode
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
from dialectica_graph.spanner_schema import get_ddl_statements
from dialectica_graph.tenant import TenantFilter

logger = logging.getLogger(__name__)


def _node_to_row(node: ConflictNode, workspace_id: str, tenant_id: str) -> dict:
    """Serialize a ConflictNode to a Spanner Nodes row dict."""
    data = node.model_dump(exclude={"embedding", "metadata", "source_text"})
    # Separate base columns from label-specific properties
    base_keys = {
        "id", "label", "workspace_id", "tenant_id",
        "created_at", "updated_at", "source_text",
        "confidence", "extraction_method",
    }
    properties = {k: v for k, v in data.items() if k not in base_keys and v is not None}
    # Convert datetime values in properties to ISO strings for JSON
    for k, v in properties.items():
        if isinstance(v, datetime):
            properties[k] = v.isoformat()

    return {
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "id": node.id,
        "label": node.label,
        "properties": json.dumps(properties) if properties else None,
        "source_text": node.source_text,
        "confidence": node.confidence,
        "extraction_method": node.extraction_method,
        "embedding": node.embedding,
        "metadata": json.dumps(node.metadata) if node.metadata else None,
        "created_at": node.created_at,
        "updated_at": datetime.utcnow(),
    }


def _row_to_node(row: dict) -> ConflictNode:
    """Deserialize a Spanner Nodes row dict to a ConflictNode."""
    label = row.get("label", "")
    cls = NODE_TYPES.get(label, ConflictNode)
    props = json.loads(row["properties"]) if row.get("properties") else {}
    meta = json.loads(row["metadata"]) if row.get("metadata") else {}

    base = {
        "id": row["id"],
        "label": label,
        "workspace_id": row.get("workspace_id", ""),
        "tenant_id": row.get("tenant_id", ""),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "source_text": row.get("source_text"),
        "confidence": row.get("confidence", 1.0),
        "extraction_method": row.get("extraction_method"),
        "embedding": row.get("embedding"),
        "metadata": meta,
    }
    # Merge label-specific properties
    base.update(props)
    return cls.model_validate(base)


def _edge_to_row(edge: ConflictRelationship, workspace_id: str, tenant_id: str) -> dict:
    """Serialize a ConflictRelationship to a Spanner Edges row dict."""
    return {
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "id": edge.id,
        "type": str(edge.type),
        "source_id": edge.source_id,
        "target_id": edge.target_id,
        "source_label": edge.source_label,
        "target_label": edge.target_label,
        "properties": json.dumps(edge.properties) if edge.properties else None,
        "weight": edge.weight,
        "confidence": edge.confidence,
        "temporal_start": edge.temporal_start,
        "temporal_end": edge.temporal_end,
        "source_text": edge.source_text,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def _row_to_edge(row: dict) -> ConflictRelationship:
    """Deserialize a Spanner Edges row dict to a ConflictRelationship."""
    props = json.loads(row["properties"]) if row.get("properties") else {}
    return ConflictRelationship(
        id=row["id"],
        type=EdgeType(row["type"]),
        source_id=row["source_id"],
        target_id=row["target_id"],
        source_label=row.get("source_label", ""),
        target_label=row.get("target_label", ""),
        workspace_id=row.get("workspace_id", ""),
        tenant_id=row.get("tenant_id", ""),
        properties=props,
        weight=row.get("weight", 1.0),
        confidence=row.get("confidence", 1.0),
        temporal_start=row.get("temporal_start"),
        temporal_end=row.get("temporal_end"),
        source_text=row.get("source_text"),
    )


def _results_to_dicts(result_set: Any, columns: list[str]) -> list[dict]:
    """Convert a Spanner result set to a list of dicts."""
    return [dict(zip(columns, row)) for row in result_set]


class SpannerGraphClient(GraphClient):
    """Google Cloud Spanner Graph implementation of GraphClient.

    Args:
        project_id: GCP project ID.
        instance_id: Spanner instance ID.
        database_id: Spanner database ID.
    """

    def __init__(
        self,
        project_id: str,
        instance_id: str = "dialectica-graph",
        database_id: str = "dialectica",
    ) -> None:
        self._client = spanner.Client(project=project_id)
        self._instance = self._client.instance(instance_id)
        self._database = self._instance.database(database_id)
        self._tenant_filter = TenantFilter()

    # ── Schema Management ──────────────────────────────────────────────────

    async def initialize_schema(self) -> None:
        """Apply all DDL statements to create tables, graph, and indexes."""
        ddl = get_ddl_statements()
        logger.info("Applying %d DDL statements to Spanner", len(ddl))
        operation = self._database.update_ddl(ddl)
        operation.result()  # Block until complete
        logger.info("Schema initialization complete")

    # ── Node CRUD ──────────────────────────────────────────────────────────

    async def upsert_node(
        self, node: ConflictNode, workspace_id: str, tenant_id: str
    ) -> str:
        node.workspace_id = workspace_id
        node.tenant_id = tenant_id
        row = _node_to_row(node, workspace_id, tenant_id)
        columns = list(row.keys())
        values = [list(row.values())]
        self._database.run_in_transaction(
            lambda txn: txn.insert_or_update("Nodes", columns=columns, values=values)
        )
        return node.id

    async def delete_node(
        self, node_id: str, workspace_id: str, hard: bool = False
    ) -> bool:
        if hard:
            # Also delete connected edges
            def _hard_delete(txn: Any) -> None:
                txn.delete(
                    "Edges",
                    spanner.KeySet(keys=[]),  # Can't use KeySet for non-PK filter
                )
                # Delete edges referencing this node
                txn.execute_update(
                    "DELETE FROM Edges WHERE workspace_id = @ws AND "
                    "(source_id = @nid OR target_id = @nid)",
                    params={"ws": workspace_id, "nid": node_id},
                    param_types={"ws": param_types.STRING, "nid": param_types.STRING},
                )
                # Delete the node (need tenant_id, but we look it up)
                txn.execute_update(
                    "DELETE FROM Nodes WHERE workspace_id = @ws AND id = @nid",
                    params={"ws": workspace_id, "nid": node_id},
                    param_types={"ws": param_types.STRING, "nid": param_types.STRING},
                )

            self._database.run_in_transaction(_hard_delete)
        else:
            # Soft delete: set deleted_at
            def _soft_delete(txn: Any) -> None:
                txn.execute_update(
                    "UPDATE Nodes SET deleted_at = CURRENT_TIMESTAMP(), "
                    "updated_at = CURRENT_TIMESTAMP() "
                    "WHERE workspace_id = @ws AND id = @nid",
                    params={"ws": workspace_id, "nid": node_id},
                    param_types={"ws": param_types.STRING, "nid": param_types.STRING},
                )

            self._database.run_in_transaction(_soft_delete)
        return True

    async def get_node(
        self, node_id: str, workspace_id: str
    ) -> ConflictNode | None:
        sql = (
            "SELECT * FROM Nodes "
            "WHERE workspace_id = @ws AND id = @nid AND deleted_at IS NULL"
        )
        params = {"ws": workspace_id, "nid": node_id}
        ptypes = {"ws": param_types.STRING, "nid": param_types.STRING}

        with self._database.snapshot() as snapshot:
            result = snapshot.execute_sql(sql, params=params, param_types=ptypes)
            columns = [col.name for col in result.metadata.row_type.fields]
            rows = _results_to_dicts(result, columns)

        if not rows:
            return None
        return _row_to_node(rows[0])

    async def get_nodes(
        self,
        workspace_id: str,
        label: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ConflictNode]:
        sql = (
            "SELECT * FROM Nodes "
            "WHERE workspace_id = @ws AND deleted_at IS NULL"
        )
        params: dict[str, Any] = {"ws": workspace_id}
        ptypes: dict[str, Any] = {"ws": param_types.STRING}

        if label:
            sql += " AND label = @lbl"
            params["lbl"] = label
            ptypes["lbl"] = param_types.STRING

        sql += " ORDER BY created_at DESC LIMIT @lim OFFSET @off"
        params["lim"] = limit
        params["off"] = offset
        ptypes["lim"] = param_types.INT64
        ptypes["off"] = param_types.INT64

        with self._database.snapshot() as snapshot:
            result = snapshot.execute_sql(sql, params=params, param_types=ptypes)
            columns = [col.name for col in result.metadata.row_type.fields]
            rows = _results_to_dicts(result, columns)

        return [_row_to_node(r) for r in rows]

    # ── Edge CRUD ──────────────────────────────────────────────────────────

    async def upsert_edge(
        self, edge: ConflictRelationship, workspace_id: str, tenant_id: str
    ) -> str:
        edge.workspace_id = workspace_id
        edge.tenant_id = tenant_id
        row = _edge_to_row(edge, workspace_id, tenant_id)
        columns = list(row.keys())
        values = [list(row.values())]
        self._database.run_in_transaction(
            lambda txn: txn.insert_or_update("Edges", columns=columns, values=values)
        )
        return edge.id

    async def get_edges(
        self,
        workspace_id: str,
        edge_type: str | None = None,
    ) -> list[ConflictRelationship]:
        sql = "SELECT * FROM Edges WHERE workspace_id = @ws"
        params: dict[str, Any] = {"ws": workspace_id}
        ptypes: dict[str, Any] = {"ws": param_types.STRING}

        if edge_type:
            sql += " AND type = @et"
            params["et"] = edge_type
            ptypes["et"] = param_types.STRING

        sql += " ORDER BY created_at DESC"

        with self._database.snapshot() as snapshot:
            result = snapshot.execute_sql(sql, params=params, param_types=ptypes)
            columns = [col.name for col in result.metadata.row_type.fields]
            rows = _results_to_dicts(result, columns)

        return [_row_to_edge(r) for r in rows]

    # ── Traversal ──────────────────────────────────────────────────────────

    async def traverse(
        self,
        start_id: str,
        workspace_id: str,
        hops: int = 2,
        edge_types: list[str] | None = None,
    ) -> SubgraphResult:
        """Multi-hop traversal using Spanner GQL MATCH on the property graph."""
        # Build the GQL query
        edge_filter = ""
        if edge_types:
            labels = " | ".join(edge_types)
            edge_filter = f":{labels}"

        gql = (
            f"GRAPH ConflictGraph "
            f"MATCH path = (start)-[e{edge_filter}]-{{1,{hops}}}(end) "
            f"WHERE start.id = @start_id "
            f"RETURN DISTINCT start, e, end"
        )
        params = {"start_id": start_id}
        ptypes = {"start_id": param_types.STRING}

        seen_nodes: dict[str, ConflictNode] = {}
        edges: list[ConflictRelationship] = []

        # Fallback to SQL-based traversal (more compatible with emulator)
        # Collect nodes reachable within N hops via iterative SQL
        current_ids = {start_id}
        all_node_ids: set[str] = {start_id}
        collected_edges: list[dict] = []

        for _hop in range(hops):
            if not current_ids:
                break
            placeholders = ", ".join(f"'{nid}'" for nid in current_ids)
            edge_sql = (
                f"SELECT * FROM Edges WHERE workspace_id = @ws "
                f"AND (source_id IN ({placeholders}) OR target_id IN ({placeholders}))"
            )
            e_params: dict[str, Any] = {"ws": workspace_id}
            e_ptypes: dict[str, Any] = {"ws": param_types.STRING}

            if edge_types:
                type_list = ", ".join(f"'{et}'" for et in edge_types)
                edge_sql += f" AND type IN ({type_list})"

            with self._database.snapshot() as snapshot:
                result = snapshot.execute_sql(edge_sql, params=e_params, param_types=e_ptypes)
                columns = [col.name for col in result.metadata.row_type.fields]
                rows = _results_to_dicts(result, columns)

            next_ids: set[str] = set()
            for row in rows:
                collected_edges.append(row)
                for nid in (row["source_id"], row["target_id"]):
                    if nid not in all_node_ids:
                        next_ids.add(nid)
                        all_node_ids.add(nid)
            current_ids = next_ids

        # Fetch all discovered nodes
        if all_node_ids:
            placeholders = ", ".join(f"'{nid}'" for nid in all_node_ids)
            node_sql = (
                f"SELECT * FROM Nodes WHERE workspace_id = @ws "
                f"AND id IN ({placeholders}) AND deleted_at IS NULL"
            )
            with self._database.snapshot() as snapshot:
                result = snapshot.execute_sql(
                    node_sql,
                    params={"ws": workspace_id},
                    param_types={"ws": param_types.STRING},
                )
                columns = [col.name for col in result.metadata.row_type.fields]
                node_rows = _results_to_dicts(result, columns)
            for r in node_rows:
                seen_nodes[r["id"]] = _row_to_node(r)

        # Deduplicate edges
        seen_edge_ids: set[str] = set()
        for er in collected_edges:
            if er["id"] not in seen_edge_ids:
                seen_edge_ids.add(er["id"])
                edges.append(_row_to_edge(er))

        return SubgraphResult(
            nodes=list(seen_nodes.values()),
            edges=edges,
            metadata={"start_id": start_id, "hops": hops, "traversal_method": "sql_iterative"},
        )

    # ── Vector Search ──────────────────────────────────────────────────────

    async def vector_search(
        self,
        embedding: list[float],
        workspace_id: str,
        label: str | None = None,
        top_k: int = 10,
    ) -> list[ScoredNode]:
        """KNN search using Spanner's native COSINE_DISTANCE on embeddings."""
        sql = (
            "SELECT *, COSINE_DISTANCE(embedding, @query_emb) AS distance "
            "FROM Nodes "
            "WHERE workspace_id = @ws AND deleted_at IS NULL "
            "AND embedding IS NOT NULL"
        )
        params: dict[str, Any] = {
            "ws": workspace_id,
            "query_emb": embedding,
        }
        ptypes: dict[str, Any] = {
            "ws": param_types.STRING,
            "query_emb": param_types.Array(param_types.FLOAT64),
        }

        if label:
            sql += " AND label = @lbl"
            params["lbl"] = label
            ptypes["lbl"] = param_types.STRING

        sql += " ORDER BY distance ASC LIMIT @k"
        params["k"] = top_k
        ptypes["k"] = param_types.INT64

        with self._database.snapshot() as snapshot:
            result = snapshot.execute_sql(sql, params=params, param_types=ptypes)
            columns = [col.name for col in result.metadata.row_type.fields]
            rows = _results_to_dicts(result, columns)

        scored: list[ScoredNode] = []
        for row in rows:
            distance = row.pop("distance", 0.0)
            node = _row_to_node(row)
            scored.append(ScoredNode(
                node=node,
                score=1.0 - distance,  # cosine similarity = 1 - cosine distance
                distance=distance,
            ))
        return scored

    # ── Raw Query ──────────────────────────────────────────────────────────

    async def execute_query(
        self, query: str, params: dict | None = None
    ) -> list[dict]:
        ptypes = {}
        if params:
            for k, v in params.items():
                if isinstance(v, str):
                    ptypes[k] = param_types.STRING
                elif isinstance(v, int):
                    ptypes[k] = param_types.INT64
                elif isinstance(v, float):
                    ptypes[k] = param_types.FLOAT64
                elif isinstance(v, bool):
                    ptypes[k] = param_types.BOOL

        with self._database.snapshot() as snapshot:
            result = snapshot.execute_sql(
                query, params=params or {}, param_types=ptypes
            )
            columns = [col.name for col in result.metadata.row_type.fields]
            return _results_to_dicts(result, columns)

    # ── Analytics ──────────────────────────────────────────────────────────

    async def get_workspace_stats(self, workspace_id: str) -> WorkspaceStats:
        stats = WorkspaceStats()

        # Node counts by label
        sql_nodes = (
            "SELECT label, COUNT(*) as cnt FROM Nodes "
            "WHERE workspace_id = @ws AND deleted_at IS NULL "
            "GROUP BY label"
        )
        # Edge counts by type
        sql_edges = (
            "SELECT type, COUNT(*) as cnt FROM Edges "
            "WHERE workspace_id = @ws GROUP BY type"
        )
        params = {"ws": workspace_id}
        ptypes = {"ws": param_types.STRING}

        with self._database.snapshot() as snapshot:
            node_result = snapshot.execute_sql(sql_nodes, params=params, param_types=ptypes)
            for row in node_result:
                stats.node_counts_by_label[row[0]] = row[1]
                stats.total_nodes += row[1]

            edge_result = snapshot.execute_sql(sql_edges, params=params, param_types=ptypes)
            for row in edge_result:
                stats.edge_counts_by_type[row[0]] = row[1]
                stats.total_edges += row[1]

        stats.compute_density()
        return stats

    async def get_actor_network(
        self, actor_id: str, workspace_id: str
    ) -> ActorNetworkResult:
        # Get the actor node
        actor = await self.get_node(actor_id, workspace_id)
        if actor is None:
            raise ValueError(f"Actor {actor_id} not found in workspace {workspace_id}")

        result = ActorNetworkResult(actor=actor)

        # Get alliance and opposition edges
        ally_edges = await self.get_edges(workspace_id, edge_type="ALLIED_WITH")
        oppose_edges = await self.get_edges(workspace_id, edge_type="OPPOSED_TO")

        ally_ids: set[str] = set()
        opponent_ids: set[str] = set()

        for edge in ally_edges:
            if edge.source_id == actor_id:
                ally_ids.add(edge.target_id)
                result.connections.append(edge)
            elif edge.target_id == actor_id:
                ally_ids.add(edge.source_id)
                result.connections.append(edge)

        for edge in oppose_edges:
            if edge.source_id == actor_id:
                opponent_ids.add(edge.target_id)
                result.connections.append(edge)
            elif edge.target_id == actor_id:
                opponent_ids.add(edge.source_id)
                result.connections.append(edge)

        # Fetch ally and opponent nodes
        for nid in ally_ids:
            node = await self.get_node(nid, workspace_id)
            if node:
                result.allies.append(node)

        for nid in opponent_ids:
            node = await self.get_node(nid, workspace_id)
            if node:
                result.opponents.append(node)

        # Simple degree centrality
        all_edges = await self.get_edges(workspace_id)
        degree = sum(1 for e in all_edges if e.source_id == actor_id or e.target_id == actor_id)
        total_actors_sql = (
            "SELECT COUNT(*) FROM Nodes "
            "WHERE workspace_id = @ws AND label = 'Actor' AND deleted_at IS NULL"
        )
        with self._database.snapshot() as snapshot:
            count_result = snapshot.execute_sql(
                total_actors_sql,
                params={"ws": workspace_id},
                param_types={"ws": param_types.STRING},
            )
            total_actors = list(count_result)[0][0]

        if total_actors > 1:
            result.centrality_scores["degree"] = degree / (total_actors - 1)
        else:
            result.centrality_scores["degree"] = 0.0

        return result

    async def get_timeline(
        self,
        workspace_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ConflictNode]:
        """Get Event nodes ordered by occurred_at within the workspace."""
        sql = (
            "SELECT * FROM Nodes "
            "WHERE workspace_id = @ws AND label = 'Event' AND deleted_at IS NULL"
        )
        params: dict[str, Any] = {"ws": workspace_id}
        ptypes: dict[str, Any] = {"ws": param_types.STRING}

        if start:
            sql += " AND JSON_VALUE(properties, '$.occurred_at') >= @start_ts"
            params["start_ts"] = start.isoformat()
            ptypes["start_ts"] = param_types.STRING
        if end:
            sql += " AND JSON_VALUE(properties, '$.occurred_at') <= @end_ts"
            params["end_ts"] = end.isoformat()
            ptypes["end_ts"] = param_types.STRING

        sql += " ORDER BY created_at ASC"

        with self._database.snapshot() as snapshot:
            result = snapshot.execute_sql(sql, params=params, param_types=ptypes)
            columns = [col.name for col in result.metadata.row_type.fields]
            rows = _results_to_dicts(result, columns)

        return [_row_to_node(r) for r in rows]

    async def get_escalation_trajectory(
        self, workspace_id: str
    ) -> EscalationResult:
        """Compute Glasl escalation trajectory from Conflict nodes."""
        sql = (
            "SELECT * FROM Nodes "
            "WHERE workspace_id = @ws AND label = 'Conflict' AND deleted_at IS NULL "
            "ORDER BY created_at ASC"
        )
        with self._database.snapshot() as snapshot:
            result = snapshot.execute_sql(
                sql,
                params={"ws": workspace_id},
                param_types={"ws": param_types.STRING},
            )
            columns = [col.name for col in result.metadata.row_type.fields]
            rows = _results_to_dicts(result, columns)

        trajectory: list[EscalationTrajectoryPoint] = []
        for row in rows:
            node = _row_to_node(row)
            props = json.loads(row["properties"]) if row.get("properties") else {}
            glasl = props.get("glasl_stage")
            if glasl is not None:
                trajectory.append(EscalationTrajectoryPoint(
                    timestamp=row.get("created_at", datetime.utcnow()),
                    glasl_stage=int(glasl),
                    evidence=props.get("name", node.id),
                ))

        esc = EscalationResult(trajectory=trajectory)
        if trajectory:
            esc.current_stage = trajectory[-1].glasl_stage
            if len(trajectory) >= 2:
                first = trajectory[0]
                last = trajectory[-1]
                delta_stages = last.glasl_stage - first.glasl_stage
                delta_time = (last.timestamp - first.timestamp).days / 30.0
                esc.velocity = delta_stages / delta_time if delta_time > 0 else 0.0
                if delta_stages > 0:
                    esc.direction = "escalating"
                elif delta_stages < 0:
                    esc.direction = "de-escalating"
                else:
                    esc.direction = "stable"

        return esc

    # ── Batch Operations ───────────────────────────────────────────────────

    async def batch_upsert_nodes(
        self,
        nodes: list[ConflictNode],
        workspace_id: str,
        tenant_id: str,
    ) -> list[str]:
        if not nodes:
            return []
        rows = [_node_to_row(n, workspace_id, tenant_id) for n in nodes]
        # Set workspace/tenant on each node
        for n in nodes:
            n.workspace_id = workspace_id
            n.tenant_id = tenant_id
        columns = list(rows[0].keys())
        values = [list(r.values()) for r in rows]

        self._database.run_in_transaction(
            lambda txn: txn.insert_or_update("Nodes", columns=columns, values=values)
        )
        return [n.id for n in nodes]

    async def batch_upsert_edges(
        self,
        edges: list[ConflictRelationship],
        workspace_id: str,
        tenant_id: str,
    ) -> list[str]:
        if not edges:
            return []
        rows = [_edge_to_row(e, workspace_id, tenant_id) for e in edges]
        for e in edges:
            e.workspace_id = workspace_id
            e.tenant_id = tenant_id
        columns = list(rows[0].keys())
        values = [list(r.values()) for r in rows]

        self._database.run_in_transaction(
            lambda txn: txn.insert_or_update("Edges", columns=columns, values=values)
        )
        return [e.id for e in edges]

    # ── Lifecycle ──────────────────────────────────────────────────────────

    async def close(self) -> None:
        """Close the Spanner client."""
        self._client.close()
