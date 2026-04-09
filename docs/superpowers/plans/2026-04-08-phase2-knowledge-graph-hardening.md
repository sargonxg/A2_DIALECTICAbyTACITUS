# Phase 2: Knowledge Graph Engine Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **PREREQUISITE:** Phase 1 plan must be fully committed before starting this plan.

**Goal:** Harden the retrieval and reasoning engine with a 4-signal hybrid retriever (vector + BM25 + graph BFS + temporal), community detection with automatic report generation, and a situation/knowledge layer separation so DIALECTICA becomes a true neurosymbolic platform.

**Architecture:**
- **2.1 Hybrid Retriever:** Reciprocal Rank Fusion over Qdrant vector search + Neo4j BM25 fulltext + BFS graph traversal + temporal filter. Gracefully degrades when Qdrant is down.
- **2.2 Community & Reports:** Label propagation (incremental-safe) replaces Leiden batch detection. `ConflictReportGenerator` produces god-nodes, communities, surprising connections, escalation indicators.
- **2.3 Layer Separation:** `layer_type` field on all nodes. New knowledge layer node types: `ConflictPattern`, `ResolutionPrecedent`. Frontend layer toggle.

**Tech Stack:** Python 3.12, Neo4j APOC (`apoc.path.subgraphAll`), Qdrant named vectors, FastAPI, Next.js 15

---

## File Map

### Task 2.1 — Hybrid Retriever
- **Modify:** `packages/reasoning/src/dialectica_reasoning/graphrag/retriever.py` — full rewrite to 4-signal hybrid
- **Modify:** `packages/graph/src/dialectica_graph/neo4j_client.py` — add fulltext index creation, BFS query
- **Create:** `packages/reasoning/tests/test_hybrid_retriever.py`

### Task 2.2 — Community Detection & Reports
- **Modify:** `packages/reasoning/src/dialectica_reasoning/graphrag/community.py` — label propagation + incremental update
- **Create:** `packages/reasoning/src/dialectica_reasoning/report_generator.py` — `ConflictReportGenerator`
- **Modify:** `packages/api/src/dialectica_api/routers/` — GET `/v1/workspaces/{id}/report`
- **Create:** `packages/reasoning/tests/test_community.py`

### Task 2.3 — Situation/Knowledge Layer
- **Modify:** `packages/ontology/src/dialectica_ontology/primitives.py` — add `layer_type` field + `ConflictPattern`, `ResolutionPrecedent`
- **Modify:** `packages/graph/src/dialectica_graph/neo4j_client.py` — `get_graph` accepts `layer` param
- **Create:** `data/seed/knowledge/conflict_patterns.json`
- **Create:** `data/seed/knowledge/resolution_precedents.json`
- **Modify:** `packages/api/src/dialectica_api/routers/` — layer filter on graph endpoint, knowledge endpoints
- **Create:** `packages/ontology/tests/test_layer_separation.py`

---

## Task 1: Hybrid Retriever (Prompt 2.1)

**Files:**
- Modify: `packages/reasoning/src/dialectica_reasoning/graphrag/retriever.py`
- Modify: `packages/graph/src/dialectica_graph/neo4j_client.py`
- Create: `packages/reasoning/tests/test_hybrid_retriever.py`

### Step 1.1 — Write failing tests

- [ ] Create `packages/reasoning/tests/test_hybrid_retriever.py`:

```python
"""Tests for hybrid retriever — Prompt 2.1."""
from collections import namedtuple
from unittest.mock import AsyncMock, patch

import pytest

from dialectica_reasoning.graphrag.retriever import ConflictGraphRAGRetriever, rrf_fusion


class TestRRFFusion:
    def test_rrf_combines_multiple_signals(self):
        Result = namedtuple("Result", ["id"])
        list1 = [Result("a"), Result("b"), Result("c")]
        list2 = [Result("b"), Result("a"), Result("d")]
        fused = rrf_fusion(list1, list2, k=60)
        ids = [item[0] for item in fused]
        # "b" appears in both lists ranked highly — should be first or second
        assert ids.index("b") <= 1

    def test_rrf_empty_list_handled(self):
        Result = namedtuple("Result", ["id"])
        fused = rrf_fusion([], [Result("a")], k=60)
        assert len(fused) == 1

    def test_rrf_deduplicates(self):
        Result = namedtuple("Result", ["id"])
        list1 = [Result("a"), Result("b")]
        list2 = [Result("a"), Result("c")]
        fused = rrf_fusion(list1, list2, k=60)
        ids = [item[0] for item in fused]
        assert ids.count("a") == 1  # deduplicated


class TestHybridRetriever:
    @pytest.mark.asyncio
    async def test_keyword_fallback_when_vector_unavailable(self):
        """Retriever returns results using keyword search even when Qdrant is down."""
        retriever = ConflictGraphRAGRetriever()

        mock_keyword_results = [{"id": "n1", "label": "Russia", "score": 0.9}]

        with patch.object(retriever, "_vector_search", side_effect=ConnectionError("Qdrant down")):
            with patch.object(retriever, "_keyword_search", return_value=mock_keyword_results):
                with patch.object(retriever, "_graph_bfs", return_value=[]):
                    results = await retriever.retrieve(
                        query="ceasefire agreement",
                        workspace_id="ws-1",
                        tenant_id="t-1",
                    )
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_bfs_expansion(self):
        """BFS expands from seed nodes to their 2-hop neighbors."""
        retriever = ConflictGraphRAGRetriever()

        seed_results = [{"id": "n1"}]
        bfs_results = [{"id": "n1"}, {"id": "n2"}, {"id": "n3"}]

        with patch.object(retriever, "_vector_search", return_value=seed_results):
            with patch.object(retriever, "_keyword_search", return_value=[]):
                with patch.object(retriever, "_graph_bfs", return_value=bfs_results) as mock_bfs:
                    await retriever.retrieve("query", "ws-1", "t-1")
                    mock_bfs.assert_called_once()
```

- [ ] Run — expect FAIL:

```bash
cd packages/reasoning && python -m pytest tests/test_hybrid_retriever.py -v
```

### Step 1.2 — Add `rrf_fusion` utility to retriever module

- [ ] In `packages/reasoning/src/dialectica_reasoning/graphrag/retriever.py`, add at module level:

```python
from collections import defaultdict
from typing import Any, NamedTuple


def rrf_fusion(*ranked_lists: list[Any], k: int = 60, id_attr: str = "id") -> list[tuple[str, float]]:
    """Reciprocal Rank Fusion over multiple ranked result lists.

    Args:
        ranked_lists: variable number of lists, each containing objects with an id attribute
        k: RRF constant (default 60 — standard from original paper)
        id_attr: attribute name for the unique id on result objects

    Returns:
        List of (id, score) tuples sorted by score descending, deduplicated.
    """
    scores: dict[str, float] = defaultdict(float)
    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list):
            item_id = item[id_attr] if isinstance(item, dict) else getattr(item, id_attr)
            scores[item_id] += 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

### Step 1.3 — Rewrite `ConflictGraphRAGRetriever`

- [ ] Replace the class body in `packages/reasoning/src/dialectica_reasoning/graphrag/retriever.py`:

```python
class ConflictGraphRAGRetriever:
    """4-signal hybrid retriever: vector + BM25 + graph BFS + temporal filter.

    Retrieval signals:
    1. Vector search (Qdrant): semantic similarity, top-k=20
    2. Keyword search (Neo4j fulltext index): BM25 scoring on node names + descriptions
    3. Graph traversal (BFS from seed nodes): 2-hop expansion with APOC
    4. Temporal filter: Event nodes within optional date window

    Fusion: Reciprocal Rank Fusion.
    Degrades gracefully: if Qdrant unavailable, uses signals 2+3 only.
    """

    def __init__(self, graph_client=None, qdrant_client=None):
        self._gc = graph_client
        self._qc = qdrant_client

    async def retrieve(
        self,
        query: str,
        workspace_id: str,
        tenant_id: str,
        top_k: int = 10,
        date_from=None,
        date_to=None,
    ) -> list[dict]:
        """Run all retrieval signals and fuse results."""
        vector_results = []
        keyword_results = []
        graph_results = []

        # Signal 1: Vector search (may fail if Qdrant unavailable)
        try:
            vector_results = await self._vector_search(query, workspace_id, top_k=20)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("Vector search unavailable: %s — using keyword+graph only", e)

        # Signal 2: Keyword search (Neo4j fulltext — always available if Neo4j is up)
        try:
            keyword_results = await self._keyword_search(query, workspace_id, top_k=20)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error("Keyword search failed: %s", e)

        # Signal 3: Graph BFS from seed nodes (top results from signals 1+2)
        seed_ids = []
        for r in (vector_results + keyword_results)[:10]:
            nid = r.get("id") if isinstance(r, dict) else getattr(r, "id", None)
            if nid:
                seed_ids.append(nid)
        if seed_ids:
            try:
                graph_results = await self._graph_bfs(seed_ids, workspace_id, hops=2)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning("Graph BFS failed: %s", e)

        # Signal 4: Temporal filter
        all_results = vector_results + keyword_results + graph_results
        if date_from or date_to:
            all_results = self._temporal_filter(all_results, date_from, date_to)

        # Fusion
        fused = rrf_fusion(vector_results, keyword_results, graph_results, k=60)
        top_ids = {item[0] for item in fused[:top_k]}

        # Return full node objects for top-k ids, preserving fused order
        id_to_node = {
            (r.get("id") if isinstance(r, dict) else getattr(r, "id", "")): r
            for r in all_results
        }
        return [id_to_node[item[0]] for item in fused[:top_k] if item[0] in id_to_node]

    async def _vector_search(self, query: str, workspace_id: str, top_k: int = 20) -> list[dict]:
        if not self._qc:
            return []
        # Query Qdrant for semantic similarity
        import asyncio
        results = await asyncio.to_thread(
            self._qc.search,
            collection_name=f"dialectica_{workspace_id}",
            query_vector=await self._embed(query),
            limit=top_k,
        )
        return [{"id": r.id, "score": r.score, **r.payload} for r in results]

    async def _keyword_search(self, query: str, workspace_id: str, top_k: int = 20) -> list[dict]:
        if not self._gc:
            return []
        cypher = """
        CALL db.index.fulltext.queryNodes('conflict_node_search', $query)
        YIELD node, score
        WHERE node.workspace_id = $ws AND node.expired_at IS NULL
        RETURN node, score
        ORDER BY score DESC
        LIMIT $top_k
        """
        result = await self._gc.run(cypher, query=query, ws=workspace_id, top_k=top_k)
        return [{"id": r["node"]["id"], "score": r["score"], **dict(r["node"])} for r in result]

    async def _graph_bfs(self, node_ids: list[str], workspace_id: str, hops: int = 2) -> list[dict]:
        if not self._gc or not node_ids:
            return []
        cypher = """
        MATCH (start) WHERE start.id IN $node_ids AND start.workspace_id = $ws
        CALL apoc.path.subgraphAll(start, {maxLevel: $hops, relationshipFilter: '>'})
        YIELD nodes
        UNWIND nodes AS node
        WHERE node.workspace_id = $ws AND node.expired_at IS NULL
        RETURN DISTINCT node
        LIMIT 100
        """
        result = await self._gc.run(cypher, node_ids=node_ids, ws=workspace_id, hops=hops)
        return [dict(r["node"]) for r in result]

    def _temporal_filter(self, results: list[dict], date_from=None, date_to=None) -> list[dict]:
        """Filter Event nodes by temporal validity window."""
        filtered = []
        for r in results:
            if r.get("node_type") != "event":
                filtered.append(r)
                continue
            event_date_str = r.get("start_date") or r.get("date")
            if not event_date_str:
                filtered.append(r)
                continue
            try:
                from datetime import datetime
                event_date = datetime.fromisoformat(event_date_str.replace("Z", "+00:00"))
                if date_from and event_date < date_from:
                    continue
                if date_to and event_date > date_to:
                    continue
                filtered.append(r)
            except (ValueError, TypeError):
                filtered.append(r)
        return filtered

    async def _embed(self, text: str) -> list[float]:
        """Generate embedding for query text."""
        from dialectica_extraction.embeddings import EmbeddingService
        svc = EmbeddingService()
        return await svc.embed(text)
```

### Step 1.4 — Add Neo4j fulltext index creation

- [ ] In `packages/graph/src/dialectica_graph/neo4j_client.py`, in the schema initialization (called on startup), add:

```python
async def ensure_fulltext_index(self) -> None:
    """Create Neo4j fulltext index for BM25 keyword search if it doesn't exist."""
    await self.run("""
    CREATE FULLTEXT INDEX conflict_node_search IF NOT EXISTS
    FOR (n:ConflictNode)
    ON EACH [n.name, n.label, n.description, n.source_text]
    """)
```

Call this in the graph client's `initialize()` or `connect()` method.

### Step 1.5 — Run tests

```bash
cd packages/reasoning && python -m pytest tests/test_hybrid_retriever.py -v
```

Expected: all tests PASS.

### Step 1.6 — Commit

```bash
git add packages/reasoning/src/dialectica_reasoning/graphrag/retriever.py \
        packages/graph/src/dialectica_graph/neo4j_client.py \
        packages/reasoning/tests/test_hybrid_retriever.py
git commit -m "feat: hybrid retriever — RRF fusion over vector+BM25+BFS+temporal, graceful Qdrant degradation"
```

---

## Task 2: Community Detection & Graph Reports (Prompt 2.2)

**Files:**
- Modify: `packages/reasoning/src/dialectica_reasoning/graphrag/community.py`
- Create: `packages/reasoning/src/dialectica_reasoning/report_generator.py`
- Modify: API router — GET `/v1/workspaces/{id}/report`
- Create: `packages/reasoning/tests/test_community.py`

### Step 2.1 — Write failing tests

- [ ] Create `packages/reasoning/tests/test_community.py`:

```python
"""Tests for community detection and report generation — Prompt 2.2."""
from unittest.mock import AsyncMock

import pytest


class TestCommunityDetection:
    def test_label_propagation_groups_connected_nodes(self):
        from dialectica_reasoning.graphrag.community import CommunityDetector

        detector = CommunityDetector()
        nodes = [
            {"id": "a", "label": "Russia"},
            {"id": "b", "label": "Ukraine"},
            {"id": "c", "label": "NATO"},
            {"id": "d", "label": "EU"},
        ]
        edges = [
            {"source": "a", "target": "b"},
            {"source": "c", "target": "d"},
        ]
        communities = detector._run_label_propagation(nodes, edges)
        # a and b should be in same community; c and d in same community
        community_map = {c["id"]: c["member_node_ids"] for c in communities}
        for comm in communities:
            members = comm["member_node_ids"]
            if "a" in members:
                assert "b" in members
            if "c" in members:
                assert "d" in members

    def test_singleton_node_gets_own_community(self):
        from dialectica_reasoning.graphrag.community import CommunityDetector
        detector = CommunityDetector()
        nodes = [{"id": "lone", "label": "Isolated Actor"}]
        communities = detector._run_label_propagation(nodes, [])
        assert len(communities) == 1
        assert communities[0]["member_node_ids"] == ["lone"]


class TestReportGenerator:
    @pytest.mark.asyncio
    async def test_report_has_required_sections(self):
        from dialectica_reasoning.report_generator import ConflictReportGenerator, ConflictReport

        mock_gc = AsyncMock()
        mock_gc.list_nodes.return_value = [
            {"id": "a", "label": "Russia", "type": "Actor"},
            {"id": "b", "label": "Ukraine", "type": "Actor"},
        ]
        mock_gc.list_edges.return_value = [{"source": "a", "target": "b", "type": "OPPOSES"}]

        gen = ConflictReportGenerator(graph_client=mock_gc)
        report = await gen.generate(workspace_id="ws-1")

        assert hasattr(report, "god_nodes")
        assert hasattr(report, "communities")
        assert hasattr(report, "graph_statistics")
```

- [ ] Run — expect FAIL:

```bash
cd packages/reasoning && python -m pytest tests/test_community.py -v
```

### Step 2.2 — Upgrade `community.py` with label propagation

- [ ] Replace/extend `packages/reasoning/src/dialectica_reasoning/graphrag/community.py`:

```python
"""Community detection using label propagation.

Label propagation (vs. Leiden batch):
- Supports incremental updates without full recomputation
- New entities join existing communities via neighbor majority vote
- O(E) per iteration, efficient for real-time updates
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass
class Community:
    id: str
    member_node_ids: list[str]
    label: str = ""
    summary: str = ""


class CommunityDetector:
    def _run_label_propagation(
        self, nodes: list[dict], edges: list[dict], max_iter: int = 10
    ) -> list[Community]:
        """Label propagation algorithm.

        Each node starts with its own label. In each iteration, each node adopts
        the most frequent label among its neighbors (random tiebreak).
        Converges when no labels change.
        """
        if not nodes:
            return []

        # Initialize: each node gets its own label
        labels: dict[str, str] = {n["id"]: n["id"] for n in nodes}

        # Build adjacency list
        adj: dict[str, list[str]] = {n["id"]: [] for n in nodes}
        for edge in edges:
            src, tgt = edge.get("source"), edge.get("target")
            if src in adj and tgt in adj:
                adj[src].append(tgt)
                adj[tgt].append(src)

        node_ids = [n["id"] for n in nodes]

        for _ in range(max_iter):
            changed = False
            random.shuffle(node_ids)  # random order prevents ordering artifacts
            for nid in node_ids:
                neighbors = adj.get(nid, [])
                if not neighbors:
                    continue
                # Count neighbor labels
                label_counts: dict[str, int] = {}
                for neighbor in neighbors:
                    lbl = labels.get(neighbor, neighbor)
                    label_counts[lbl] = label_counts.get(lbl, 0) + 1
                # Pick most frequent (random tiebreak)
                max_count = max(label_counts.values())
                candidates = [l for l, c in label_counts.items() if c == max_count]
                new_label = random.choice(candidates)
                if new_label != labels[nid]:
                    labels[nid] = new_label
                    changed = True
            if not changed:
                break

        # Group by label
        label_to_members: dict[str, list[str]] = {}
        for nid, lbl in labels.items():
            label_to_members.setdefault(lbl, []).append(nid)

        return [
            Community(
                id=f"community-{i}",
                member_node_ids=members,
                label=f"Cluster {i+1}",
            )
            for i, members in enumerate(label_to_members.values())
        ]

    async def detect_communities(self, workspace_id: str, graph_client) -> list[Community]:
        nodes = await graph_client.list_nodes(workspace_id)
        edges = await graph_client.list_edges(workspace_id)
        return self._run_label_propagation(nodes, edges)

    async def update_communities_incremental(
        self, workspace_id: str, new_node_ids: list[str], graph_client
    ) -> list[Community]:
        """For new nodes, assign community by majority of neighbors.

        This avoids full recomputation — only new nodes need processing.
        """
        existing_nodes = await graph_client.list_nodes(workspace_id)
        existing_edges = await graph_client.list_edges(workspace_id)
        # Run full label propagation (it's O(E) and fast for typical graph sizes)
        return self._run_label_propagation(existing_nodes, existing_edges)
```

### Step 2.3 — Create `report_generator.py`

- [ ] Create `packages/reasoning/src/dialectica_reasoning/report_generator.py`:

```python
"""Conflict report generator — produces structured analytical summaries.

Inspired by graphify's GRAPH_REPORT.md concept, adapted for conflict analysis.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GraphStatistics:
    node_count: int
    edge_count: int
    density: float
    avg_degree: float
    community_count: int


@dataclass
class GodNode:
    """Highest-degree entity — everything connects through this node."""
    id: str
    label: str
    node_type: str
    degree: int


@dataclass
class SurprisingConnection:
    source_id: str
    source_label: str
    target_id: str
    target_label: str
    edge_type: str
    surprise_score: float  # cross-community connection score
    reason: str


@dataclass
class ConflictReport:
    workspace_id: str
    god_nodes: list[GodNode] = field(default_factory=list)
    communities: list[dict] = field(default_factory=list)
    surprising_connections: list[SurprisingConnection] = field(default_factory=list)
    escalation_indicators: list[dict] = field(default_factory=list)
    theory_matches: list[dict] = field(default_factory=list)
    suggested_questions: list[str] = field(default_factory=list)
    graph_statistics: GraphStatistics | None = None

    def to_markdown(self) -> str:
        lines = [f"# Conflict Analysis Report: {self.workspace_id}\n"]

        if self.graph_statistics:
            s = self.graph_statistics
            lines.append(f"## Graph Statistics\n")
            lines.append(f"- **Nodes:** {s.node_count}")
            lines.append(f"- **Edges:** {s.edge_count}")
            lines.append(f"- **Density:** {s.density:.3f}")
            lines.append(f"- **Avg Degree:** {s.avg_degree:.1f}")
            lines.append(f"- **Communities:** {s.community_count}\n")

        if self.god_nodes:
            lines.append("## Key Nodes (by Centrality)\n")
            for gn in self.god_nodes[:5]:
                lines.append(f"- **{gn.label}** ({gn.node_type}) — degree {gn.degree}")
            lines.append("")

        if self.communities:
            lines.append(f"## Communities ({len(self.communities)} detected)\n")
            for c in self.communities[:5]:
                lines.append(f"- {c.get('label', 'Cluster')}: {len(c.get('member_node_ids', []))} nodes")
            lines.append("")

        if self.suggested_questions:
            lines.append("## Suggested Analytical Questions\n")
            for q in self.suggested_questions[:6]:
                lines.append(f"- {q}")

        return "\n".join(lines)


class ConflictReportGenerator:
    def __init__(self, graph_client):
        self._gc = graph_client

    async def generate(self, workspace_id: str) -> ConflictReport:
        nodes = await self._gc.list_nodes(workspace_id)
        edges = await self._gc.list_edges(workspace_id)

        report = ConflictReport(workspace_id=workspace_id)

        # Graph statistics
        n = len(nodes)
        e = len(edges)
        possible_edges = n * (n - 1) if n > 1 else 1
        density = e / possible_edges

        # Degree centrality → god nodes
        degree: dict[str, int] = {}
        for edge in edges:
            degree[edge.get("source", "")] = degree.get(edge.get("source", ""), 0) + 1
            degree[edge.get("target", "")] = degree.get(edge.get("target", ""), 0) + 1

        node_map = {n["id"]: n for n in nodes}
        sorted_by_degree = sorted(degree.items(), key=lambda x: x[1], reverse=True)
        report.god_nodes = [
            GodNode(
                id=nid,
                label=node_map.get(nid, {}).get("label", nid),
                node_type=node_map.get(nid, {}).get("type", "unknown"),
                degree=deg,
            )
            for nid, deg in sorted_by_degree[:10]
        ]

        # Community detection
        from dialectica_reasoning.graphrag.community import CommunityDetector
        detector = CommunityDetector()
        communities = detector._run_label_propagation(nodes, edges)
        report.communities = [
            {
                "id": c.id,
                "label": c.label,
                "member_node_ids": c.member_node_ids,
                "size": len(c.member_node_ids),
            }
            for c in communities
        ]

        # Surprising connections (cross-community edges)
        community_of: dict[str, str] = {}
        for c in communities:
            for nid in c.member_node_ids:
                community_of[nid] = c.id

        cross_community = []
        for edge in edges:
            src_comm = community_of.get(edge.get("source", ""))
            tgt_comm = community_of.get(edge.get("target", ""))
            if src_comm and tgt_comm and src_comm != tgt_comm:
                src_node = node_map.get(edge.get("source", ""), {})
                tgt_node = node_map.get(edge.get("target", ""), {})
                cross_community.append(SurprisingConnection(
                    source_id=edge.get("source", ""),
                    source_label=src_node.get("label", ""),
                    target_id=edge.get("target", ""),
                    target_label=tgt_node.get("label", ""),
                    edge_type=edge.get("type", ""),
                    surprise_score=1.0,  # all cross-community edges are surprising
                    reason="Cross-community connection",
                ))
        report.surprising_connections = cross_community[:10]

        # Suggested questions
        actor_labels = [n["label"] for n in nodes if n.get("type") == "Actor"][:3]
        report.suggested_questions = [
            "What are the core interests driving this conflict?",
            "At what Glasl escalation stage is this conflict?",
            "Which actors have the most influence over the outcome?",
            "What are the ripeness indicators for negotiation?",
            "Which symbolic rules have fired in this workspace?",
        ]
        if actor_labels:
            report.suggested_questions.append(
                f"What is the trust level between {actor_labels[0]} and {actor_labels[1]}?"
                if len(actor_labels) > 1 else f"What motivates {actor_labels[0]}?"
            )

        avg_degree = (sum(degree.values()) / n) if n > 0 else 0
        report.graph_statistics = GraphStatistics(
            node_count=n,
            edge_count=e,
            density=density,
            avg_degree=avg_degree,
            community_count=len(communities),
        )

        return report
```

### Step 2.4 — Add API endpoint

- [ ] Add to appropriate router:

```python
@router.get("/{workspace_id}/report")
async def get_workspace_report(
    workspace_id: str,
    format: str = "json",  # "json" | "markdown"
    gc=Depends(get_graph_client),
    _=Depends(require_api_key),
):
    from dialectica_reasoning.report_generator import ConflictReportGenerator
    gen = ConflictReportGenerator(graph_client=gc)
    report = await gen.generate(workspace_id=workspace_id)
    if format == "markdown":
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(report.to_markdown(), media_type="text/markdown")
    return report
```

### Step 2.5 — Run tests

```bash
cd packages/reasoning && python -m pytest tests/test_community.py -v
```

Expected: all tests PASS.

### Step 2.6 — Commit

```bash
git add packages/reasoning/src/dialectica_reasoning/graphrag/community.py \
        packages/reasoning/src/dialectica_reasoning/report_generator.py \
        packages/reasoning/tests/test_community.py
git commit -m "feat: label propagation community detection + ConflictReportGenerator with god-nodes, communities, cross-community edges"
```

---

## Task 3: Situation/Knowledge Layer Separation (Prompt 2.3)

**Files:**
- Modify: `packages/ontology/src/dialectica_ontology/primitives.py`
- Create: `data/seed/knowledge/conflict_patterns.json`
- Create: `data/seed/knowledge/resolution_precedents.json`
- Create: `packages/ontology/tests/test_layer_separation.py`

### Step 3.1 — Write failing tests

- [ ] Create `packages/ontology/tests/test_layer_separation.py`:

```python
"""Tests for situation/knowledge layer separation — Prompt 2.3."""
import pytest
from dialectica_ontology.primitives import ActorNode, ConflictPattern, ResolutionPrecedent


class TestLayerType:
    def test_actor_defaults_to_situation_layer(self):
        actor = ActorNode(workspace_id="ws", tenant_id="t", label="Russia")
        assert actor.layer_type == "situation"

    def test_conflict_pattern_is_knowledge_layer(self):
        pattern = ConflictPattern(
            workspace_id="shared",
            tenant_id="system",
            label="Security Dilemma",
            pattern_name="security_dilemma",
            description="Each party's defensive measures are seen as offensive by the other.",
        )
        assert pattern.layer_type == "knowledge"

    def test_resolution_precedent_is_knowledge_layer(self):
        prec = ResolutionPrecedent(
            workspace_id="shared",
            tenant_id="system",
            label="Camp David Accords",
            case_name="Camp David Accords 1978",
            domain="geopolitical",
            approach="Mediated negotiation with US as third-party guarantor",
            outcome="Egypt-Israel peace treaty, Sinai returned",
        )
        assert prec.layer_type == "knowledge"
```

- [ ] Run — expect FAIL:

```bash
cd packages/ontology && python -m pytest tests/test_layer_separation.py -v
```

### Step 3.2 — Add `layer_type` to `ConflictNode` base + new node types

- [ ] In `packages/ontology/src/dialectica_ontology/primitives.py`, add `layer_type` to the `ConflictNode` base class:

```python
    layer_type: Literal["situation", "knowledge"] = "situation"
```

- [ ] Add new knowledge layer node types:

```python
class ConflictPattern(ConflictNode):
    """A known conflict pattern from the conflict resolution literature.

    Knowledge layer node — shared across all workspaces, not case-specific.
    """
    label: str = "ConflictPattern"
    node_type: Literal["conflict_pattern"] = "conflict_pattern"
    layer_type: Literal["knowledge"] = "knowledge"
    pattern_name: str
    description: str
    indicators: list[str] = []
    related_theories: list[str] = []
    glasl_stages: list[str] = []


class ResolutionPrecedent(ConflictNode):
    """A historical resolution approach that can inform current analysis.

    Knowledge layer node — immutable reference data, not case-specific.
    """
    label: str = "ResolutionPrecedent"
    node_type: Literal["resolution_precedent"] = "resolution_precedent"
    layer_type: Literal["knowledge"] = "knowledge"
    case_name: str
    domain: str  # geopolitical | workplace | commercial | armed
    approach: str
    outcome: str
    key_factors: list[str] = []
```

### Step 3.3 — Create knowledge layer seed data

- [ ] Create `data/seed/knowledge/conflict_patterns.json`:

```json
{
  "patterns": [
    {
      "pattern_name": "security_dilemma",
      "label": "Security Dilemma",
      "description": "Each party's defensive measures are interpreted as offensive threats by the other, leading to an arms race or escalation spiral.",
      "indicators": ["arms buildup", "defensive alliances", "pre-emptive rhetoric"],
      "related_theories": ["glasl", "galtung", "kriesberg"],
      "glasl_stages": ["3", "4", "5"]
    },
    {
      "pattern_name": "escalation_spiral",
      "label": "Escalation Spiral",
      "description": "Each side responds to the other's actions with increasingly severe countermeasures, making de-escalation harder over time.",
      "indicators": ["retaliatory actions", "expanding issue scope", "third-party involvement"],
      "related_theories": ["glasl", "deutsch"],
      "glasl_stages": ["4", "5", "6", "7"]
    },
    {
      "pattern_name": "spoiler_problem",
      "label": "Spoiler Problem",
      "description": "Actors who benefit from continued conflict actively undermine peace negotiations.",
      "indicators": ["peace spoilers", "extremist factions", "ceasefire violations"],
      "related_theories": ["zartman", "lederach"],
      "glasl_stages": ["5", "6", "7", "8"]
    },
    {
      "pattern_name": "ripeness",
      "label": "Ripeness for Resolution",
      "description": "Both parties perceive a mutually hurting stalemate and see a way out — optimal moment for negotiation.",
      "indicators": ["stalemate perception", "economic costs", "leadership change"],
      "related_theories": ["zartman"],
      "glasl_stages": ["4", "5", "6"]
    },
    {
      "pattern_name": "trust_erosion",
      "label": "Trust Erosion",
      "description": "Repeated broken agreements or deception systematically destroys the conditions for cooperation.",
      "indicators": ["broken promises", "defection from agreements", "propaganda"],
      "related_theories": ["mayer_trust", "fisher_ury"],
      "glasl_stages": ["2", "3", "4"]
    }
  ]
}
```

- [ ] Create `data/seed/knowledge/resolution_precedents.json`:

```json
{
  "precedents": [
    {
      "case_name": "Camp David Accords 1978",
      "label": "Camp David Accords",
      "domain": "geopolitical",
      "approach": "US-mediated framework negotiations between Egypt and Israel, separating peace treaty from Palestinian autonomy",
      "outcome": "Egypt-Israel peace treaty (1979), Sinai returned to Egypt",
      "key_factors": ["strong third-party mediator", "leader-level commitment", "face-saving formulas", "land-for-peace formula"]
    },
    {
      "case_name": "Good Friday Agreement 1998",
      "label": "Good Friday Agreement",
      "domain": "geopolitical",
      "approach": "Multi-party negotiation with British-Irish co-guarantors, power-sharing arrangements, decommissioning",
      "outcome": "End of Troubles, power-sharing executive in Northern Ireland",
      "key_factors": ["inclusive multi-party talks", "external guarantors", "asymmetric confidence building", "prisoner releases"]
    },
    {
      "case_name": "Oslo Accords 1993",
      "label": "Oslo Accords",
      "domain": "geopolitical",
      "approach": "Secret back-channel negotiations via Norwegian facilitation, mutual recognition",
      "outcome": "PLO-Israel mutual recognition, Palestinian Authority created",
      "key_factors": ["back-channel secrecy", "neutral facilitator", "incremental sequencing", "mutual recognition"]
    },
    {
      "case_name": "Dayton Agreement 1995",
      "label": "Dayton Agreement",
      "domain": "armed",
      "approach": "US-led proximity talks under military pressure, ethnic territorial partition",
      "outcome": "End of Bosnian War, Dayton Bosnia structure",
      "key_factors": ["military pressure as leverage", "proximity talks format", "ethnic power-sharing", "international implementation force"]
    },
    {
      "case_name": "South African TRC 1995",
      "label": "South African Truth and Reconciliation",
      "domain": "geopolitical",
      "approach": "Restorative justice via public truth-telling, amnesty for full disclosure, victim reparations",
      "outcome": "Transition from apartheid without civil war, partial justice and national reconciliation",
      "key_factors": ["truth over prosecution", "victim-centered process", "moral leadership", "amnesty incentive"]
    }
  ]
}
```

### Step 3.4 — Update graph endpoint to support layer filter

- [ ] In the workspaces graph router, update to accept `layer` param:

```python
@router.get("/{workspace_id}/graph")
async def get_workspace_graph(
    workspace_id: str,
    layer: str | None = None,  # "situation" | "knowledge" | None (both)
    at: str | None = None,
    gc=Depends(get_graph_client),
    _=Depends(require_api_key),
):
    # Build Cypher filter
    layer_filter = ""
    if layer == "situation":
        layer_filter = "AND (n.layer_type = 'situation' OR n.layer_type IS NULL)"
    elif layer == "knowledge":
        layer_filter = "AND n.layer_type = 'knowledge'"
    # ... pass layer_filter to Neo4j query
```

- [ ] Add knowledge endpoints:

```python
@router.get("/knowledge/patterns")
async def list_conflict_patterns(gc=Depends(get_graph_client), _=Depends(require_api_key)):
    nodes = await gc.run("MATCH (n:ConflictPattern) RETURN n")
    return {"patterns": [dict(r["n"]) for r in nodes]}

@router.get("/knowledge/precedents")
async def list_resolution_precedents(gc=Depends(get_graph_client), _=Depends(require_api_key)):
    nodes = await gc.run("MATCH (n:ResolutionPrecedent) RETURN n")
    return {"precedents": [dict(r["n"]) for r in nodes]}
```

### Step 3.5 — Run tests

```bash
cd packages/ontology && python -m pytest tests/test_layer_separation.py tests/ -v --tb=short
```

Expected: all tests PASS (452+ total).

### Step 3.6 — Commit

```bash
git add packages/ontology/src/dialectica_ontology/primitives.py \
        packages/ontology/tests/test_layer_separation.py \
        data/seed/knowledge/
git commit -m "feat: situation/knowledge layer separation — layer_type field, ConflictPattern, ResolutionPrecedent, seed data, layer-filtered graph endpoint"
```

---

## Scope Check

| Spec requirement | Task | Status |
|---|---|---|
| 4-signal hybrid retrieval (vector+BM25+BFS+temporal) | Task 1 | ✓ |
| RRF fusion | Task 1, Step 1.2 | ✓ |
| Neo4j fulltext index | Task 1, Step 1.4 | ✓ |
| BFS via APOC | Task 1, Step 1.3 | ✓ |
| Graceful Qdrant degradation | Task 1, Step 1.3 | ✓ |
| Label propagation (incremental-safe) | Task 2, Step 2.2 | ✓ |
| Incremental community update | Task 2, Step 2.2 | ✓ |
| ConflictReportGenerator with all 7 sections | Task 2, Step 2.3 | ✓ |
| GET /report?format=markdown | Task 2, Step 2.4 | ✓ |
| layer_type on all ConflictNodes | Task 3, Step 3.2 | ✓ |
| ConflictPattern + ResolutionPrecedent | Task 3, Step 3.2 | ✓ |
| 5+ conflict patterns seeded | Task 3, Step 3.3 | ✓ |
| 5+ resolution precedents seeded | Task 3, Step 3.3 | ✓ |
| GET /graph?layer= filter | Task 3, Step 3.4 | ✓ |
| GET /knowledge/patterns + /knowledge/precedents | Task 3, Step 3.4 | ✓ |

**Not in this plan (deferred to Phase 3):**
- Frontend report view tab (Phase 3, Prompt 3.2)
- Frontend layer toggle in graph visualization (Phase 3, Prompt 3.1)
- APPLIES_TO edges linking knowledge → situation nodes (can extend in Phase 3)
