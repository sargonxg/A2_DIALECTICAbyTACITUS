"""
Graph Reader — Read-optimized query builders for DIALECTICA graph database.

Provides subgraph assembly, timeline queries, and filtered reads
that work with both Spanner and Neo4j backends via the GraphClient interface.
"""

from __future__ import annotations

from datetime import datetime

from dialectica_graph.interface import GraphClient
from dialectica_graph.models import SubgraphResult
from dialectica_ontology.primitives import ConflictNode
from dialectica_ontology.relationships import ConflictRelationship


async def get_subgraph_for_conflict(
    client: GraphClient,
    conflict_id: str,
    workspace_id: str,
    hops: int = 2,
) -> SubgraphResult:
    """Assemble a complete subgraph around a conflict node.

    Traverses from the conflict node to collect parties, events, issues,
    interests, processes, outcomes, and their relationships.
    """
    return await client.traverse(
        start_id=conflict_id,
        workspace_id=workspace_id,
        hops=hops,
    )


async def get_actor_conflicts(
    client: GraphClient,
    actor_id: str,
    workspace_id: str,
) -> SubgraphResult:
    """Get all conflicts an actor is party to, with related edges."""
    return await client.traverse(
        start_id=actor_id,
        workspace_id=workspace_id,
        hops=2,
        edge_types=["PARTY_TO", "PARTICIPATES_IN"],
    )


async def get_event_chain(
    client: GraphClient,
    event_id: str,
    workspace_id: str,
    depth: int = 5,
) -> SubgraphResult:
    """Follow causal chains from an event (CAUSED edges)."""
    return await client.traverse(
        start_id=event_id,
        workspace_id=workspace_id,
        hops=depth,
        edge_types=["CAUSED"],
    )


async def get_timeline_with_context(
    client: GraphClient,
    workspace_id: str,
    start: datetime | None = None,
    end: datetime | None = None,
) -> tuple[list[ConflictNode], list[ConflictRelationship]]:
    """Get timeline events with their connected edges (participants, locations)."""
    events = await client.get_timeline(workspace_id, start=start, end=end)
    edges: list[ConflictRelationship] = []

    # Collect edges for each event
    all_edges = await client.get_edges(workspace_id)
    event_ids = {e.id for e in events}
    for edge in all_edges:
        if edge.source_id in event_ids or edge.target_id in event_ids:
            edges.append(edge)

    return events, edges


async def get_narrative_landscape(
    client: GraphClient,
    workspace_id: str,
) -> SubgraphResult:
    """Get all narratives and their connections to actors and conflicts."""
    narratives = await client.get_nodes(workspace_id, label="Narrative")
    all_edges = await client.get_edges(workspace_id)

    narrative_ids = {n.id for n in narratives}
    relevant_edges = [
        e for e in all_edges if e.source_id in narrative_ids or e.target_id in narrative_ids
    ]
    connected_ids = set()
    for e in relevant_edges:
        connected_ids.add(e.source_id)
        connected_ids.add(e.target_id)
    connected_ids -= narrative_ids

    connected_nodes: list[ConflictNode] = []
    for nid in connected_ids:
        node = await client.get_node(nid, workspace_id)
        if node:
            connected_nodes.append(node)

    return SubgraphResult(
        nodes=list(narratives) + connected_nodes,
        edges=relevant_edges,
        metadata={"query_type": "narrative_landscape"},
    )
