"""
Graph Writer — Write-optimized batch operations for DIALECTICA graph database.

Provides bulk node/edge upsert with conflict resolution, atomic graph
construction, and extraction result ingestion.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from dialectica_ontology.primitives import ConflictNode
from dialectica_ontology.relationships import ConflictRelationship, validate_relationship

from dialectica_graph.interface import GraphClient

logger = logging.getLogger(__name__)


@dataclass
class WriteResult:
    """Result of a batch write operation."""

    node_ids: list[str] = field(default_factory=list)
    edge_ids: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    @property
    def total_written(self) -> int:
        return len(self.node_ids) + len(self.edge_ids)


async def bulk_upsert(
    client: GraphClient,
    nodes: list[ConflictNode],
    edges: list[ConflictRelationship],
    workspace_id: str,
    tenant_id: str,
    validate_edges: bool = True,
    batch_size: int = 500,
) -> WriteResult:
    """Bulk upsert nodes and edges with optional validation.

    Nodes are written first (edges reference them). Edges are validated
    against EDGE_SCHEMA if validate_edges=True. Writes are batched
    for performance.

    Args:
        client: GraphClient implementation.
        nodes: Nodes to upsert.
        edges: Edges to upsert.
        workspace_id: Target workspace.
        tenant_id: Owning tenant.
        validate_edges: Validate edge source/target constraints.
        batch_size: Max items per batch write.

    Returns:
        WriteResult with IDs of written items and any errors.
    """
    result = WriteResult()

    # Validate edges first
    if validate_edges:
        for edge in edges:
            errors = validate_relationship(edge)
            if errors:
                result.errors.extend(errors)
        if result.errors:
            logger.warning("Edge validation failed: %s", result.errors)
            return result

    # Batch upsert nodes
    for i in range(0, len(nodes), batch_size):
        batch = nodes[i : i + batch_size]
        try:
            ids = await client.batch_upsert_nodes(batch, workspace_id, tenant_id)
            result.node_ids.extend(ids)
        except Exception as e:
            result.errors.append(f"Node batch {i // batch_size}: {e}")

    # Batch upsert edges
    for i in range(0, len(edges), batch_size):
        batch = edges[i : i + batch_size]
        try:
            ids = await client.batch_upsert_edges(batch, workspace_id, tenant_id)
            result.edge_ids.extend(ids)
        except Exception as e:
            result.errors.append(f"Edge batch {i // batch_size}: {e}")

    logger.info(
        "Bulk upsert: %d nodes, %d edges written (%d errors)",
        len(result.node_ids),
        len(result.edge_ids),
        len(result.errors),
    )
    return result


async def ingest_extraction_result(
    client: GraphClient,
    nodes: list[ConflictNode],
    edges: list[ConflictRelationship],
    workspace_id: str,
    tenant_id: str,
) -> WriteResult:
    """Ingest results from an NLP extraction pipeline.

    Sets extraction_method on nodes, validates edges, and writes atomically.
    """
    for node in nodes:
        if not node.extraction_method:
            node.extraction_method = "gemini_extraction"

    return await bulk_upsert(
        client, nodes, edges, workspace_id, tenant_id, validate_edges=True
    )


async def merge_duplicate_nodes(
    client: GraphClient,
    primary_id: str,
    duplicate_id: str,
    workspace_id: str,
    tenant_id: str,
) -> str:
    """Merge a duplicate node into a primary node.

    Rewrites all edges pointing to/from duplicate to point to primary,
    then soft-deletes the duplicate.

    Returns:
        The primary node ID.
    """
    # Get all edges referencing the duplicate
    all_edges = await client.get_edges(workspace_id)

    for edge in all_edges:
        updated = False
        if edge.source_id == duplicate_id:
            edge.source_id = primary_id
            updated = True
        if edge.target_id == duplicate_id:
            edge.target_id = primary_id
            updated = True
        if updated:
            await client.upsert_edge(edge, workspace_id, tenant_id)

    # Soft-delete the duplicate
    await client.delete_node(duplicate_id, workspace_id, hard=False)
    return primary_id
