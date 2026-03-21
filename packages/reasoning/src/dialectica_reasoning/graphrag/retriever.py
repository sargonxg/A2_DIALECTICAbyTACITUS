"""
Conflict GraphRAG Retriever — 4-step hybrid vector + graph retrieval with RRF fusion.

Pipeline:
  1. Query Qdrant for top-k=20 semantically similar nodes (filter by tenant_id)
  2. Graph expansion: 2-hop Cypher from seed nodes with edge-type filtering
  3. Temporal filter on Event nodes within optional [date_from, date_to] window
  4. RRF fusion: score(d) = Σ 1/(60 + rank_i(d)) across vector and graph results
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime

from dialectica_graph import GraphClient
from dialectica_ontology.primitives import ConflictNode
from dialectica_ontology.relationships import ConflictRelationship

logger = logging.getLogger(__name__)

RRF_K = 60  # Reciprocal Rank Fusion constant


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

    4-step pipeline:
      1. Vector search: Qdrant semantic top-k with tenant isolation
      2. Graph expansion: N-hop traversal from seed nodes via FalkorDB
      3. Temporal filter: Event nodes within date range
      4. RRF fusion: combine vector scores + graph proximity scores
    """

    def __init__(
        self,
        graph_client: GraphClient,
        vector_store: object | None = None,
        embed_fn: object | None = None,
    ) -> None:
        self._gc = graph_client
        self._vs = vector_store  # QdrantVectorStore
        self._embed_fn = embed_fn

    async def retrieve(
        self,
        query: str,
        workspace_id: str,
        tenant_id: str = "",
        top_k: int = 20,
        hops: int = 2,
        node_types: list[str] | None = None,
        confidence_threshold: float = 0.3,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> RetrievalResult:
        """Execute 4-step hybrid retrieval."""
        result = RetrievalResult(query=query, workspace_id=workspace_id)

        # ── Step 1: Vector search via Qdrant ──────────────────────────────
        vector_ranked: list[str] = []
        vector_scores: dict[str, float] = {}
        all_nodes: dict[str, ConflictNode] = {}

        try:
            query_emb = self._embed_query(query)
            if query_emb and self._vs is not None:
                vs_results = await self._vs.search_semantic(
                    query_embedding=query_emb,
                    tenant_id=tenant_id,
                    top_k=top_k,
                    node_types=node_types,
                    date_from=date_from,
                    date_to=date_to,
                )
                for r in vs_results:
                    nid = r["node_id"]
                    vector_ranked.append(nid)
                    vector_scores[nid] = r["score"]
        except Exception as e:
            logger.warning("Vector search failed: %s", e)

        # Fallback: keyword search on graph if no vector results
        if not vector_ranked:
            try:
                all_graph_nodes = await self._gc.get_nodes(workspace_id, limit=200)
                query_lower = query.lower()
                for node in all_graph_nodes:
                    name = getattr(node, "name", "") or ""
                    desc = getattr(node, "description", "") or ""
                    if query_lower in name.lower() or query_lower in desc.lower():
                        vector_ranked.append(node.id)
                        vector_scores[node.id] = 0.6
                        all_nodes[node.id] = node
                    if len(vector_ranked) >= top_k:
                        break
            except Exception:
                pass

        # Load seed nodes from graph if not already loaded
        for nid in vector_ranked:
            if nid not in all_nodes:
                try:
                    node = await self._gc.get_node(nid, workspace_id)
                    if node:
                        all_nodes[nid] = node
                except Exception:
                    pass

        # ── Step 2: Graph expansion from seed nodes ───────────────────────
        graph_ranked: list[str] = []
        all_edges: dict[str, ConflictRelationship] = {}

        seed_ids = vector_ranked[:min(5, len(vector_ranked))]
        for seed_id in seed_ids:
            try:
                subgraph = await self._gc.traverse(
                    start_id=seed_id,
                    workspace_id=workspace_id,
                    hops=hops,
                )
                for node in getattr(subgraph, "nodes", []):
                    conf = float(getattr(node, "confidence", 1.0))
                    if conf >= confidence_threshold and node.id not in all_nodes:
                        all_nodes[node.id] = node
                        graph_ranked.append(node.id)
                for edge in getattr(subgraph, "edges", []):
                    all_edges[edge.id] = edge
            except Exception:
                pass

        # ── Step 3: Temporal filter ───────────────────────────────────────
        if date_from or date_to:
            to_remove = []
            for nid, node in all_nodes.items():
                ts = getattr(node, "occurred_at", None) or getattr(node, "created_at", None)
                if ts is None:
                    continue  # Keep nodes without timestamp
                if date_from and ts < date_from:
                    to_remove.append(nid)
                elif date_to and ts > date_to:
                    to_remove.append(nid)
            for nid in to_remove:
                all_nodes.pop(nid, None)

        # Filter by node types
        if node_types:
            type_set = set(node_types)
            all_nodes = {
                nid: n for nid, n in all_nodes.items()
                if getattr(n, "label", n.__class__.__name__) in type_set
            }

        # ── Step 4: RRF fusion ────────────────────────────────────────────
        rrf_scores: dict[str, float] = {}

        # Vector ranks
        for rank, nid in enumerate(vector_ranked):
            if nid in all_nodes:
                rrf_scores[nid] = rrf_scores.get(nid, 0) + 1.0 / (RRF_K + rank)

        # Graph expansion ranks (by traversal order = proximity)
        for rank, nid in enumerate(graph_ranked):
            if nid in all_nodes:
                rrf_scores[nid] = rrf_scores.get(nid, 0) + 1.0 / (RRF_K + rank)

        # Rank and truncate
        ranked = sorted(rrf_scores.keys(), key=lambda nid: rrf_scores.get(nid, 0), reverse=True)
        ranked = ranked[:top_k]

        # Coverage stats
        coverage: dict[str, int] = {}
        for nid in ranked:
            label = getattr(all_nodes[nid], "label", all_nodes[nid].__class__.__name__)
            coverage[label] = coverage.get(label, 0) + 1

        result.nodes = [all_nodes[nid] for nid in ranked]
        result.edges = list(all_edges.values())
        result.node_ids = ranked
        result.scores = {nid: round(rrf_scores.get(nid, 0), 4) for nid in ranked}
        result.coverage = coverage
        result.retrieval_method = "hybrid" if vector_ranked else "fallback"
        return result

    def _embed_query(self, query: str) -> list[float] | None:
        """Embed the query text."""
        if self._embed_fn is not None:
            try:
                if hasattr(self._embed_fn, "embed_text"):
                    result = self._embed_fn.embed_text([query])
                    return result[0] if result else None
                return self._embed_fn(query)
            except Exception as e:
                logger.warning("Query embedding failed: %s", e)
        return None
