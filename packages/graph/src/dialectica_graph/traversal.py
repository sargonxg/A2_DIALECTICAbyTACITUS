"""
Graph Traversal — Traversal algorithms for DIALECTICA conflict graphs.

Provides BFS, DFS, shortest path, and all-paths-between-actors algorithms
that operate through the GraphClient interface.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from dialectica_ontology.primitives import ConflictNode
from dialectica_ontology.relationships import ConflictRelationship

from dialectica_graph.interface import GraphClient


@dataclass
class PathResult:
    """A path through the graph."""

    nodes: list[ConflictNode] = field(default_factory=list)
    edges: list[ConflictRelationship] = field(default_factory=list)

    @property
    def length(self) -> int:
        return len(self.edges)


@dataclass
class TraversalResult:
    """Result of a graph traversal."""

    visited: list[ConflictNode] = field(default_factory=list)
    edges_traversed: list[ConflictRelationship] = field(default_factory=list)
    paths: list[PathResult] = field(default_factory=list)


async def bfs(
    client: GraphClient,
    start_id: str,
    workspace_id: str,
    max_depth: int = 3,
    edge_types: list[str] | None = None,
) -> TraversalResult:
    """Breadth-first traversal from a starting node.

    Args:
        client: GraphClient implementation.
        start_id: Starting node ID.
        workspace_id: Workspace scope.
        max_depth: Maximum traversal depth.
        edge_types: Optional filter on edge types to follow.

    Returns:
        TraversalResult with visited nodes and edges in BFS order.
    """
    result = TraversalResult()
    visited: set[str] = set()
    queue: deque[tuple[str, int]] = deque([(start_id, 0)])

    all_edges = await client.get_edges(workspace_id, edge_type=None)
    # Build adjacency index
    adjacency: dict[str, list[ConflictRelationship]] = {}
    for edge in all_edges:
        if edge_types and edge.type not in edge_types:
            continue
        adjacency.setdefault(edge.source_id, []).append(edge)
        adjacency.setdefault(edge.target_id, []).append(edge)

    while queue:
        node_id, depth = queue.popleft()
        if node_id in visited:
            continue
        visited.add(node_id)

        node = await client.get_node(node_id, workspace_id)
        if node:
            result.visited.append(node)

        if depth >= max_depth:
            continue

        for edge in adjacency.get(node_id, []):
            neighbor_id = edge.target_id if edge.source_id == node_id else edge.source_id
            if neighbor_id not in visited:
                result.edges_traversed.append(edge)
                queue.append((neighbor_id, depth + 1))

    return result


async def dfs(
    client: GraphClient,
    start_id: str,
    workspace_id: str,
    max_depth: int = 3,
    edge_types: list[str] | None = None,
) -> TraversalResult:
    """Depth-first traversal from a starting node."""
    result = TraversalResult()
    visited: set[str] = set()

    all_edges = await client.get_edges(workspace_id)
    adjacency: dict[str, list[ConflictRelationship]] = {}
    for edge in all_edges:
        if edge_types and edge.type not in edge_types:
            continue
        adjacency.setdefault(edge.source_id, []).append(edge)
        adjacency.setdefault(edge.target_id, []).append(edge)

    stack: list[tuple[str, int]] = [(start_id, 0)]

    while stack:
        node_id, depth = stack.pop()
        if node_id in visited:
            continue
        visited.add(node_id)

        node = await client.get_node(node_id, workspace_id)
        if node:
            result.visited.append(node)

        if depth >= max_depth:
            continue

        for edge in adjacency.get(node_id, []):
            neighbor_id = edge.target_id if edge.source_id == node_id else edge.source_id
            if neighbor_id not in visited:
                result.edges_traversed.append(edge)
                stack.append((neighbor_id, depth + 1))

    return result


async def shortest_path(
    client: GraphClient,
    start_id: str,
    end_id: str,
    workspace_id: str,
    max_depth: int = 10,
    edge_types: list[str] | None = None,
) -> PathResult | None:
    """Find shortest path between two nodes using BFS.

    Returns None if no path exists within max_depth.
    """
    if start_id == end_id:
        node = await client.get_node(start_id, workspace_id)
        return PathResult(nodes=[node] if node else [])

    all_edges = await client.get_edges(workspace_id)
    adjacency: dict[str, list[tuple[str, ConflictRelationship]]] = {}
    for edge in all_edges:
        if edge_types and edge.type not in edge_types:
            continue
        adjacency.setdefault(edge.source_id, []).append((edge.target_id, edge))
        adjacency.setdefault(edge.target_id, []).append((edge.source_id, edge))

    visited: set[str] = {start_id}
    # Queue: (current_node_id, path_of_node_ids, path_of_edges)
    queue: deque[tuple[str, list[str], list[ConflictRelationship]]] = deque(
        [(start_id, [start_id], [])]
    )

    while queue:
        current, path_ids, path_edges = queue.popleft()
        if len(path_edges) >= max_depth:
            continue

        for neighbor_id, edge in adjacency.get(current, []):
            if neighbor_id in visited:
                continue
            new_path_ids = path_ids + [neighbor_id]
            new_path_edges = path_edges + [edge]

            if neighbor_id == end_id:
                # Found shortest path — resolve nodes
                nodes = []
                for nid in new_path_ids:
                    node = await client.get_node(nid, workspace_id)
                    if node:
                        nodes.append(node)
                return PathResult(nodes=nodes, edges=new_path_edges)

            visited.add(neighbor_id)
            queue.append((neighbor_id, new_path_ids, new_path_edges))

    return None


async def all_paths_between_actors(
    client: GraphClient,
    actor_a_id: str,
    actor_b_id: str,
    workspace_id: str,
    max_depth: int = 4,
) -> list[PathResult]:
    """Find all paths between two actors up to max_depth.

    Uses DFS with backtracking. Useful for analyzing how two actors
    are connected through conflicts, events, and other nodes.
    """
    all_edges = await client.get_edges(workspace_id)
    adjacency: dict[str, list[tuple[str, ConflictRelationship]]] = {}
    for edge in all_edges:
        adjacency.setdefault(edge.source_id, []).append((edge.target_id, edge))
        adjacency.setdefault(edge.target_id, []).append((edge.source_id, edge))

    results: list[PathResult] = []

    def _dfs_paths(
        current: str,
        target: str,
        visited: set[str],
        path_ids: list[str],
        path_edges: list[ConflictRelationship],
    ) -> None:
        if current == target:
            results.append(PathResult(
                nodes=[],  # Resolved after DFS
                edges=list(path_edges),
            ))
            # Store node IDs in metadata for later resolution
            results[-1]._path_ids = list(path_ids)  # type: ignore[attr-defined]
            return

        if len(path_edges) >= max_depth:
            return

        for neighbor_id, edge in adjacency.get(current, []):
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                path_ids.append(neighbor_id)
                path_edges.append(edge)
                _dfs_paths(neighbor_id, target, visited, path_ids, path_edges)
                path_edges.pop()
                path_ids.pop()
                visited.discard(neighbor_id)

    _dfs_paths(actor_a_id, actor_b_id, {actor_a_id}, [actor_a_id], [])

    # Resolve node IDs to actual nodes
    node_cache: dict[str, ConflictNode] = {}
    for path in results:
        path_ids = getattr(path, "_path_ids", [])
        for nid in path_ids:
            if nid not in node_cache:
                node = await client.get_node(nid, workspace_id)
                if node:
                    node_cache[nid] = node
        path.nodes = [node_cache[nid] for nid in path_ids if nid in node_cache]

    return results
