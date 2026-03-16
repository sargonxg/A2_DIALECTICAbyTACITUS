"""
Conflict GraphRAG Retriever — Hybrid vector + graph retrieval.

Pipeline: embed query -> vector search -> graph expansion -> rank -> return.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from dialectica_graph import GraphClient
from dialectica_ontology.primitives import ConflictNode
from dialectica_ontology.relationships import ConflictRelationship


@dataclass
class RetrievalResult:
    """Result of a hybrid retrieval operation."""
    query: str
    workspace_id: str
    nodes: list[ConflictNode] = field(default_factory=list)
    edges: list[ConflictRelationship] = field(default_factory=list)
    node_ids: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    coverage: dict[str, int] = field(default_factory=dict)
    retrieval_method: str = "hybrid"


class ConflictGraphRAGRetriever:
    """
    Hybrid vector + graph retriever for conflict knowledge graphs.

    Retrieval pipeline:
      1. Embed query via configured embedding function
      2. Vector search for top-k semantically similar nodes
      3. Graph expansion: traverse N hops from each seed node
      4. Temporal filtering (if date range provided)
      5. Rank by relevance score + confidence
    """

    def __init__(
        self,
        graph_client: GraphClient,
        embed_fn: object | None = None,
    ) -> None:
        self._gc = graph_client
        self._embed_fn = embed_fn

    async def retrieve(
        self,
        query: str,
        workspace_id: str,
        top_k: int = 20,
        hops: int = 2,
        node_types: list[str] | None = None,
        confidence_threshold: float = 0.3,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> RetrievalResult:
        """
        Execute hybrid retrieval.

        Args:
            query: Natural language query
            workspace_id: Workspace to search
            top_k: Maximum nodes to return from vector search
            hops: Graph expansion depth
            node_types: Filter to specific node labels
            confidence_threshold: Minimum extraction confidence
            date_from / date_to: Optional temporal filter
        """
        result = RetrievalResult(query=query, workspace_id=workspace_id)
        all_nodes: dict[str, ConflictNode] = {}
        all_edges: dict[str, ConflictRelationship] = {}
        scores: dict[str, float] = {}

        # Step 1: Vector search if embeddings available
        seed_ids: list[str] = []
        try:
            if hasattr(self._gc, "vector_search"):
                vector_results = await self._gc.vector_search(
                    query_text=query,
                    workspace_id=workspace_id,
                    top_k=min(top_k, 10),
                    node_types=node_types,
                )
                for scored_node in vector_results:
                    node = getattr(scored_node, "node", None)
                    score = getattr(scored_node, "score", 0.5)
                    if node and float(getattr(node, "confidence", 1.0)) >= confidence_threshold:
                        seed_ids.append(node.id)
                        all_nodes[node.id] = node
                        scores[node.id] = float(score)
        except Exception:
            pass  # Fall back to keyword search

        # Step 2: Fallback — keyword match on node names if no vector results
        if not seed_ids:
            all_graph_nodes = await self._gc.get_nodes(workspace_id, limit=200)
            query_lower = query.lower()
            for node in all_graph_nodes:
                name = getattr(node, "name", "") or ""
                desc = getattr(node, "description", "") or ""
                if query_lower in name.lower() or query_lower in desc.lower():
                    seed_ids.append(node.id)
                    all_nodes[node.id] = node
                    scores[node.id] = 0.6
                if len(seed_ids) >= top_k:
                    break

        # Step 3: If still no seeds, load most recently updated nodes
        if not seed_ids:
            fallback_nodes = await self._gc.get_nodes(workspace_id, limit=top_k)
            for node in fallback_nodes:
                if node.id not in all_nodes:
                    all_nodes[node.id] = node
                    scores[node.id] = 0.3
                    seed_ids.append(node.id)

        # Step 4: Graph expansion from seed nodes
        for seed_id in list(seed_ids)[:min(5, len(seed_ids))]:  # expand from top 5
            try:
                subgraph = await self._gc.traverse(
                    start_id=seed_id,
                    workspace_id=workspace_id,
                    hops=hops,
                )
                for node in getattr(subgraph, "nodes", []):
                    if node.id not in all_nodes:
                        conf = float(getattr(node, "confidence", 1.0))
                        if conf >= confidence_threshold:
                            all_nodes[node.id] = node
                            # Decayed score based on distance from seed
                            all_nodes[node.id] = node
                            scores[node.id] = scores.get(node.id, scores[seed_id] * 0.7)
                for edge in getattr(subgraph, "edges", []):
                    all_edges[edge.id] = edge
            except Exception:
                pass

        # Step 5: Temporal filtering
        if date_from or date_to:
            filtered: dict[str, ConflictNode] = {}
            for nid, node in all_nodes.items():
                ts = getattr(node, "occurred_at", None) or getattr(node, "created_at", None)
                if ts is None:
                    filtered[nid] = node  # include nodes without timestamp
                    continue
                if date_from and ts < date_from:
                    continue
                if date_to and ts > date_to:
                    continue
                filtered[nid] = node
            all_nodes = filtered

        # Step 6: Filter by node types
        if node_types:
            type_set = set(node_types)
            all_nodes = {
                nid: node for nid, node in all_nodes.items()
                if getattr(node, "label", getattr(node.__class__, "__name__", "")) in type_set
            }

        # Step 7: Rank and truncate
        ranked = sorted(all_nodes.keys(), key=lambda nid: scores.get(nid, 0), reverse=True)
        ranked = ranked[:top_k]

        # Compute coverage stats
        coverage: dict[str, int] = {}
        for nid in ranked:
            node = all_nodes[nid]
            label = getattr(node, "label", node.__class__.__name__)
            coverage[label] = coverage.get(label, 0) + 1

        result.nodes = [all_nodes[nid] for nid in ranked]
        result.edges = list(all_edges.values())
        result.node_ids = ranked
        result.scores = {nid: round(scores.get(nid, 0), 4) for nid in ranked}
        result.coverage = coverage
        result.retrieval_method = "hybrid" if seed_ids else "fallback"
        return result
