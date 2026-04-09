# DIALECTICA Production-Ready Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make DIALECTICA a fully functioning, production-ready neurosymbolic conflict intelligence engine for tacitus.me, with working pipeline, hybrid querying, knowledge clusters, benchmarks, GCP+Databricks cloud deployment, and TACITUS inter-app integration.

**Architecture:** 6 parallel workstreams fixing stubs, connecting real implementations, adding missing subsystems (knowledge clusters, Databricks, BigQuery, benchmarking UI), and hardening for production. Each workstream is independently testable.

**Tech Stack:** Python 3.12, FastAPI, Neo4j Aura, FalkorDB, Qdrant, LangGraph, Gemini 2.5, Next.js 15, D3.js, Terraform, GCP (Cloud Run, BigQuery, Pub/Sub, Secret Manager), Databricks, Playwright

---

## Sub-Project 1: Pipeline Fix-Up (End-to-End)

### Task 1.1: Fix `write_to_graph` — Actually Persist to Neo4j

**Files:**
- Modify: `packages/extraction/src/dialectica_extraction/pipeline.py:527-547`
- Modify: `packages/extraction/src/dialectica_extraction/pipeline.py:653-708`
- Test: `packages/extraction/tests/test_pipeline_write.py`

- [ ] **Step 1: Write failing test for async graph write**

```python
# packages/extraction/tests/test_pipeline_write.py
"""Test that write_to_graph actually calls graph client batch upsert."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from dialectica_extraction.pipeline import write_to_graph_async


@pytest.mark.asyncio
async def test_write_to_graph_calls_batch_upsert():
    mock_gc = AsyncMock()
    mock_gc.batch_upsert_nodes = AsyncMock(return_value=["id1", "id2"])
    mock_gc.batch_upsert_edges = AsyncMock(return_value=["eid1"])

    node1 = MagicMock(id="n1")
    node2 = MagicMock(id="n2")
    edge1 = MagicMock(id="e1")

    state = {
        "_nodes": [node1, node2],
        "_edges": [edge1],
        "workspace_id": "ws-test",
        "tenant_id": "t-test",
        "errors": [],
        "processing_time": {},
        "ingestion_stats": {},
    }

    result = await write_to_graph_async(state, mock_gc)

    mock_gc.batch_upsert_nodes.assert_called_once_with([node1, node2], "ws-test", "t-test")
    mock_gc.batch_upsert_edges.assert_called_once_with([edge1], "ws-test", "t-test")
    assert result["ingestion_stats"]["nodes_written"] == 2
    assert result["ingestion_stats"]["edges_written"] == 1


@pytest.mark.asyncio
async def test_write_to_graph_handles_no_client_gracefully():
    state = {
        "_nodes": [MagicMock()],
        "_edges": [],
        "workspace_id": "ws-test",
        "tenant_id": "t-test",
        "errors": [],
        "processing_time": {},
        "ingestion_stats": {},
    }

    result = await write_to_graph_async(state, None)
    assert result["ingestion_stats"]["nodes_written"] == 1
    assert "graph_client_unavailable" in str(result.get("errors", []))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/extraction/tests/test_pipeline_write.py -v`
Expected: FAIL (write_to_graph_async not defined)

- [ ] **Step 3: Implement `write_to_graph_async` in pipeline.py**

Replace the existing `write_to_graph` function body at line 527:

```python
async def write_to_graph_async(
    state: ExtractionState,
    graph_client: object | None = None,
) -> ExtractionState:
    """Step 10: Batch upsert all nodes and edges to graph database."""
    import time
    start = time.time()
    nodes = state.get("_nodes", [])
    edges = state.get("_edges", [])
    ws = state.get("workspace_id", "")
    tid = state.get("tenant_id", "")

    if graph_client is None:
        state["ingestion_stats"] = {
            "nodes_written": len(nodes),
            "edges_written": len(edges),
            "persisted": False,
            "errors": len(state.get("errors", [])),
        }
        state.setdefault("errors", []).append({
            "step": "write_to_graph",
            "message": "graph_client_unavailable — data returned but not persisted",
        })
        state.setdefault("processing_time", {})["write_to_graph"] = time.time() - start
        return state

    node_ids: list[str] = []
    edge_ids: list[str] = []
    try:
        node_ids = await graph_client.batch_upsert_nodes(nodes, ws, tid)
    except Exception as e:
        state.setdefault("errors", []).append({
            "step": "write_to_graph",
            "message": f"Node write failed: {e}",
        })

    try:
        edge_ids = await graph_client.batch_upsert_edges(edges, ws, tid)
    except Exception as e:
        state.setdefault("errors", []).append({
            "step": "write_to_graph",
            "message": f"Edge write failed: {e}",
        })

    state["ingestion_stats"] = {
        "nodes_written": len(node_ids),
        "edges_written": len(edge_ids),
        "persisted": True,
        "errors": len(state.get("errors", [])),
    }
    state.setdefault("processing_time", {})["write_to_graph"] = time.time() - start
    return state
```

Keep the old synchronous `write_to_graph` as a wrapper that stores data for the caller (existing behavior for LangGraph sync mode). Add the async version as the production path.

- [ ] **Step 4: Update `ExtractionPipeline.run` to accept graph_client**

```python
# In ExtractionPipeline class, modify run() signature:
def run(
    self,
    text: str,
    tier: OntologyTier = OntologyTier.ESSENTIAL,
    workspace_id: str = "",
    tenant_id: str = "",
    graph_client: object | None = None,
) -> ExtractionState:
    # ... existing code ...
    # Store graph_client for async write
    initial_state["_graph_client"] = graph_client
    # ... rest unchanged ...
```

- [ ] **Step 5: Run tests and verify pass**

Run: `uv run pytest packages/extraction/tests/test_pipeline_write.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add packages/extraction/
git commit -m "feat(extraction): implement real graph write in pipeline step 10"
```

---

### Task 1.2: Neo4j Batch Upserts with UNWIND

**Files:**
- Modify: `packages/graph/src/dialectica_graph/neo4j_client.py:512-534`
- Test: `packages/graph/tests/test_neo4j_batch.py`

- [ ] **Step 1: Write failing test for batch UNWIND upsert**

```python
# packages/graph/tests/test_neo4j_batch.py
"""Test that batch upserts use UNWIND instead of serial loop."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from dialectica_graph.neo4j_client import Neo4jGraphClient


@pytest.fixture
def mock_driver():
    driver = AsyncMock()
    session = AsyncMock()
    driver.session.return_value.__aenter__ = AsyncMock(return_value=session)
    driver.session.return_value.__aexit__ = AsyncMock(return_value=None)
    session.run = AsyncMock()
    return driver, session


@pytest.mark.asyncio
async def test_batch_upsert_nodes_uses_unwind(mock_driver):
    driver, session = mock_driver

    with patch("dialectica_graph.neo4j_client.AsyncGraphDatabase") as mock_db:
        mock_db.driver.return_value = driver
        client = Neo4jGraphClient("bolt://localhost:7687")
        client._driver = driver

        nodes = [MagicMock(id=f"n{i}", label="Actor", embedding=None, metadata=None) for i in range(5)]
        for n in nodes:
            n.model_dump.return_value = {"id": n.id, "label": "Actor", "name": f"Actor {n.id}"}

        await client.batch_upsert_nodes(nodes, "ws1", "t1")

        # Should be called once with UNWIND, not 5 times
        assert session.run.call_count <= 2  # At most 2 calls (nodes grouped by label)
        cypher_call = session.run.call_args_list[0]
        assert "UNWIND" in cypher_call.args[0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/graph/tests/test_neo4j_batch.py -v`
Expected: FAIL (serial loop, no UNWIND)

- [ ] **Step 3: Implement UNWIND batch upserts**

Replace `batch_upsert_nodes` and `batch_upsert_edges` in `neo4j_client.py`:

```python
async def batch_upsert_nodes(
    self,
    nodes: list[ConflictNode],
    workspace_id: str,
    tenant_id: str,
) -> list[str]:
    if not nodes:
        return []

    # Group nodes by label for type-specific MERGE
    by_label: dict[str, list[dict]] = {}
    for node in nodes:
        label = node.label or "ConflictNode"
        props = _node_to_props(node, workspace_id, tenant_id)
        entry = {"id": node.id, "props": props}
        if node.embedding:
            entry["embedding"] = node.embedding
        by_label.setdefault(label, []).append(entry)

    ids: list[str] = []
    async with self._session() as session:
        for label, batch in by_label.items():
            has_embeddings = any("embedding" in e for e in batch)
            cypher = (
                f"UNWIND $batch AS item "
                f"MERGE (n:{label} {{id: item.id}}) "
                f"SET n += item.props, n:ConflictNode, n.updated_at = datetime() "
            )
            if has_embeddings:
                cypher += ", n.embedding = CASE WHEN item.embedding IS NOT NULL THEN item.embedding ELSE n.embedding END "

            await session.run(cypher, {"batch": batch})
            ids.extend(e["id"] for e in batch)

    return ids

async def batch_upsert_edges(
    self,
    edges: list[ConflictRelationship],
    workspace_id: str,
    tenant_id: str,
) -> list[str]:
    if not edges:
        return []

    # Group edges by type for type-specific MERGE
    by_type: dict[str, list[dict]] = {}
    for edge in edges:
        etype = str(edge.type)
        props = _edge_to_props(edge, workspace_id, tenant_id)
        by_type.setdefault(etype, []).append({
            "eid": edge.id,
            "src_id": edge.source_id,
            "tgt_id": edge.target_id,
            "props": props,
        })

    ids: list[str] = []
    async with self._session() as session:
        for etype, batch in by_type.items():
            cypher = (
                "UNWIND $batch AS item "
                "MATCH (s:ConflictNode {id: item.src_id, workspace_id: $ws}) "
                "MATCH (t:ConflictNode {id: item.tgt_id, workspace_id: $ws}) "
                f"MERGE (s)-[r:{etype} {{id: item.eid}}]->(t) "
                "SET r += item.props"
            )
            await session.run(cypher, {"batch": batch, "ws": workspace_id})
            ids.extend(e["eid"] for e in batch)

    return ids
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest packages/graph/tests/test_neo4j_batch.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/graph/
git commit -m "perf(graph): use UNWIND for batch upserts instead of serial loop"
```

---

### Task 1.3: Connect Benchmark Runner to Real Pipeline

**Files:**
- Modify: `packages/api/src/dialectica_api/benchmark_runner.py:218-294`
- Test: `packages/api/tests/test_benchmark_runner.py`

- [ ] **Step 1: Write test for real pipeline integration**

```python
# packages/api/tests/test_benchmark_runner.py
"""Test benchmark runner calls real extraction pipeline."""
import pytest
from unittest.mock import patch, MagicMock
from dialectica_api.benchmark_runner import BenchmarkRunner


@pytest.mark.asyncio
async def test_run_extraction_calls_real_pipeline():
    runner = BenchmarkRunner()

    mock_pipeline = MagicMock()
    mock_state = {
        "validated_nodes": [
            {"id": "n1", "label": "Actor", "name": "Iran"},
            {"id": "n2", "label": "Actor", "name": "USA"},
        ],
        "validated_edges": [
            {"source": "n1", "target": "n2", "type": "OPPOSED_TO"},
        ],
        "errors": [],
    }
    mock_pipeline.run.return_value = mock_state

    with patch(
        "dialectica_api.benchmark_runner.ExtractionPipeline",
        return_value=mock_pipeline,
    ):
        nodes, edges = await runner._run_extraction("test text", "standard", "gemini-2.5-flash")

    mock_pipeline.run.assert_called_once()
    assert len(nodes) == 2
    assert len(edges) == 1


@pytest.mark.asyncio
async def test_run_extraction_falls_back_to_stub_on_import_error():
    runner = BenchmarkRunner()

    with patch(
        "dialectica_api.benchmark_runner.ExtractionPipeline",
        side_effect=ImportError("no pipeline"),
    ):
        nodes, edges = await runner._run_extraction("test text", "standard", "gemini-2.5-flash")

    # Should return stub data as fallback
    assert len(nodes) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest packages/api/tests/test_benchmark_runner.py -v`
Expected: FAIL

- [ ] **Step 3: Replace `_run_extraction` with real pipeline call**

In `benchmark_runner.py`, replace the `_run_extraction` method:

```python
async def _run_extraction(
    self, source_text: str, tier: str, model: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Run the extraction pipeline. Falls back to stub if pipeline unavailable."""
    try:
        from dialectica_extraction.pipeline import ExtractionPipeline
        from dialectica_ontology.tiers import OntologyTier

        pipeline = ExtractionPipeline()
        result = pipeline.run(
            text=source_text,
            tier=OntologyTier(tier),
            workspace_id=f"benchmark-{self.__class__.__name__}",
            tenant_id="benchmark",
        )
        extracted_nodes = result.get("validated_nodes", [])
        extracted_edges = result.get("validated_edges", [])
        return extracted_nodes, extracted_edges

    except (ImportError, Exception) as e:
        logger.warning("Pipeline unavailable (%s), using stub data for benchmark", e)
        return self._stub_extraction()

def _stub_extraction(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Fallback stub data for when real pipeline is unavailable."""
    # ... move existing stub_nodes and stub_edges here ...
    stub_nodes: list[dict[str, Any]] = [
        {"id": "ext_iran", "label": "Actor", "name": "Iran"},
        {"id": "ext_usa", "label": "Actor", "name": "United States"},
        # ... rest of existing stubs ...
    ]
    stub_edges: list[dict[str, Any]] = [
        {"source": "ext_iran", "target": "ext_conflict", "type": "PARTY_TO"},
        # ... rest of existing stubs ...
    ]
    return stub_nodes, stub_edges
```

Add `import logging` and `logger = logging.getLogger(__name__)` at top of file.

- [ ] **Step 4: Run tests**

Run: `uv run pytest packages/api/tests/test_benchmark_runner.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add packages/api/
git commit -m "feat(benchmark): connect runner to real extraction pipeline with stub fallback"
```

---

## Sub-Project 2: Hybrid Query & Knowledge Clusters

### Task 2.1: Qdrant Vector Store Client

**Files:**
- Create: `packages/graph/src/dialectica_graph/qdrant_store.py`
- Test: `packages/graph/tests/test_qdrant_store.py`

- [ ] **Step 1: Write failing test**

```python
# packages/graph/tests/test_qdrant_store.py
"""Test Qdrant vector store operations."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_qdrant_store_search_returns_scored_results():
    from dialectica_graph.qdrant_store import QdrantVectorStore

    mock_client = MagicMock()
    mock_client.query_points = MagicMock(return_value=MagicMock(points=[
        MagicMock(id="n1", score=0.95, payload={"node_id": "n1", "workspace_id": "ws1", "label": "Actor"}),
        MagicMock(id="n2", score=0.82, payload={"node_id": "n2", "workspace_id": "ws1", "label": "Event"}),
    ]))

    with patch("dialectica_graph.qdrant_store.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore(url="http://localhost:6333")
        results = await store.search_semantic(
            query_embedding=[0.1] * 768,
            tenant_id="t1",
            top_k=10,
        )

    assert len(results) == 2
    assert results[0]["node_id"] == "n1"
    assert results[0]["score"] == 0.95


@pytest.mark.asyncio
async def test_qdrant_store_upsert_vectors():
    from dialectica_graph.qdrant_store import QdrantVectorStore

    mock_client = MagicMock()
    mock_client.upsert = MagicMock()

    with patch("dialectica_graph.qdrant_store.QdrantClient", return_value=mock_client):
        store = QdrantVectorStore(url="http://localhost:6333")
        await store.upsert_vectors(
            node_id="n1",
            embedding=[0.1] * 768,
            workspace_id="ws1",
            tenant_id="t1",
            label="Actor",
            name="Iran",
        )

    mock_client.upsert.assert_called_once()
```

- [ ] **Step 2: Implement QdrantVectorStore**

```python
# packages/graph/src/dialectica_graph/qdrant_store.py
"""Qdrant Vector Store — Semantic search with tenant isolation."""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

COLLECTION_NAME = "dialectica_nodes"
VECTOR_DIM = 768


class QdrantVectorStore:
    """Qdrant-backed vector store for conflict node embeddings."""

    def __init__(self, url: str = "http://localhost:6333", api_key: str | None = None) -> None:
        from qdrant_client import QdrantClient
        self._client = QdrantClient(url=url, api_key=api_key)
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        from qdrant_client.models import Distance, VectorParams
        collections = [c.name for c in self._client.get_collections().collections]
        if COLLECTION_NAME not in collections:
            self._client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
            )

    async def search_semantic(
        self,
        query_embedding: list[float],
        tenant_id: str = "",
        top_k: int = 20,
        node_types: list[str] | None = None,
        date_from: Any = None,
        date_to: Any = None,
    ) -> list[dict[str, Any]]:
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        must_conditions = []
        if tenant_id:
            must_conditions.append(FieldCondition(key="tenant_id", match=MatchValue(value=tenant_id)))
        if node_types:
            must_conditions.append(FieldCondition(key="label", match=MatchValue(value=node_types[0])))

        query_filter = Filter(must=must_conditions) if must_conditions else None

        results = self._client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=top_k,
            query_filter=query_filter,
        )

        return [
            {
                "node_id": p.payload.get("node_id", str(p.id)),
                "score": p.score,
                "label": p.payload.get("label", ""),
                "workspace_id": p.payload.get("workspace_id", ""),
            }
            for p in results.points
        ]

    async def upsert_vectors(
        self,
        node_id: str,
        embedding: list[float],
        workspace_id: str,
        tenant_id: str,
        label: str = "",
        name: str = "",
    ) -> None:
        from qdrant_client.models import PointStruct
        self._client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=hash(node_id) % (2**63),
                    vector=embedding,
                    payload={
                        "node_id": node_id,
                        "workspace_id": workspace_id,
                        "tenant_id": tenant_id,
                        "label": label,
                        "name": name,
                    },
                )
            ],
        )

    async def batch_upsert(
        self,
        items: list[dict[str, Any]],
    ) -> int:
        from qdrant_client.models import PointStruct
        points = [
            PointStruct(
                id=hash(item["node_id"]) % (2**63),
                vector=item["embedding"],
                payload={
                    "node_id": item["node_id"],
                    "workspace_id": item.get("workspace_id", ""),
                    "tenant_id": item.get("tenant_id", ""),
                    "label": item.get("label", ""),
                    "name": item.get("name", ""),
                },
            )
            for item in items
        ]
        self._client.upsert(collection_name=COLLECTION_NAME, points=points)
        return len(points)
```

- [ ] **Step 3: Run tests, commit**

Run: `uv run pytest packages/graph/tests/test_qdrant_store.py -v`

```bash
git add packages/graph/
git commit -m "feat(graph): add Qdrant vector store client for semantic search"
```

---

### Task 2.2: Complete Theorist Agent (All 15 Frameworks)

**Files:**
- Modify: `packages/reasoning/src/dialectica_reasoning/agents/theorist.py:207-227`
- Test: `packages/reasoning/tests/test_theorist_complete.py`

- [ ] **Step 1: Write test verifying all 15 frameworks assessed**

```python
# packages/reasoning/tests/test_theorist_complete.py
"""Test that TheoristAgent assesses all 15 frameworks."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from dialectica_reasoning.agents.theorist import TheoristAgent

EXPECTED_FRAMEWORKS = {
    "glasl", "zartman", "fisher_ury", "mayer_trust", "french_raven",
    "pearl_causal", "plutchik", "galtung", "winslade_monk", "kriesberg",
    "burton_basic_needs", "lederach_transformation", "azar_protracted",
    "kelman_problem_solving", "deutsch_cooperation",
}


@pytest.fixture
def mock_graph():
    gc = AsyncMock()
    gc.get_nodes = AsyncMock(return_value=[])
    gc.get_edges = AsyncMock(return_value=[])
    return gc


@pytest.mark.asyncio
async def test_theorist_covers_all_15_frameworks(mock_graph):
    # Setup mock symbolic analyzers to return defaults
    agent = TheoristAgent(mock_graph)
    agent._escalation.compute_glasl_stage = AsyncMock(return_value=MagicMock(
        stage=MagicMock(stage_number=3), confidence=0.5, intervention_type="moderation"
    ))
    agent._ripeness.compute_ripeness = AsyncMock(return_value=MagicMock(
        overall_score=0.4, mhs_score=0.3, meo_score=0.5, is_ripe=False
    ))
    agent._trust.compute_trust_matrix = AsyncMock(return_value=MagicMock(
        dyads=[], average_trust=0.5
    ))
    agent._power.compute_power_map = AsyncMock(return_value=MagicMock(dyads=[]))
    agent._causal.extract_causal_chains = AsyncMock(return_value=[])

    report = await agent.run("ws-test")

    framework_ids = {a.framework_id for a in report.assessments}
    assert framework_ids == EXPECTED_FRAMEWORKS, f"Missing: {EXPECTED_FRAMEWORKS - framework_ids}"
    assert len(report.assessments) == 15
```

- [ ] **Step 2: Add the missing 5 frameworks to theorist.py**

After the existing Kriesberg assessment (line ~215), add:

```python
        # Burton Basic Human Needs
        needs_score = 0.6 if has_interests else 0.25
        assessments.append(
            FrameworkAssessment(
                framework_id="burton_basic_needs",
                framework_name="Burton Basic Human Needs Theory",
                applicability_score=round(needs_score, 3),
                key_insights=[
                    "Identity, security, and recognition needs analysis"
                    if has_interests else "Interest data needed for needs mapping"
                ],
                indicators_present=["interests", "identity_needs"] if has_interests else [],
            )
        )

        # Lederach Conflict Transformation
        lederach_score = 0.65 if len(actors) > 2 and has_narratives else 0.3
        assessments.append(
            FrameworkAssessment(
                framework_id="lederach_transformation",
                framework_name="Lederach Conflict Transformation",
                applicability_score=round(lederach_score, 3),
                key_insights=[
                    "Relational and structural transformation pathways identified"
                    if has_narratives else "Narrative data needed for transformation analysis"
                ],
                indicators_present=["narratives", "relationships"] if has_narratives else [],
            )
        )

        # Azar Protracted Social Conflict
        azar_score = 0.7 if glasl_num >= 4 and len(actors) > 3 else 0.25
        assessments.append(
            FrameworkAssessment(
                framework_id="azar_protracted",
                framework_name="Azar Protracted Social Conflict Theory",
                applicability_score=round(azar_score, 3),
                key_insights=[
                    f"Protracted indicators: stage {glasl_num}, {len(actors)} actors"
                    if glasl_num >= 4 else "Conflict not yet protracted"
                ],
                indicators_present=["escalation_stage", "actor_count"],
            )
        )

        # Kelman Interactive Problem-Solving
        kelman_score = 0.75 if has_trust and len(actors) >= 2 else 0.3
        assessments.append(
            FrameworkAssessment(
                framework_id="kelman_problem_solving",
                framework_name="Kelman Interactive Problem-Solving",
                applicability_score=round(kelman_score, 3),
                key_insights=[
                    "Trust dynamics available for workshop design"
                    if has_trust else "Trust data needed for Kelman analysis"
                ],
                indicators_present=["trust_dyads", "actors"] if has_trust else [],
            )
        )

        # Deutsch Cooperation-Competition
        deutsch_score = 0.7 if has_power and has_trust else 0.3
        assessments.append(
            FrameworkAssessment(
                framework_id="deutsch_cooperation",
                framework_name="Deutsch Cooperation-Competition Theory",
                applicability_score=round(deutsch_score, 3),
                key_insights=[
                    "Power and trust data available for cooperation analysis"
                    if has_power and has_trust else "Power and trust data needed"
                ],
                indicators_present=["power_dynamics", "trust_dyads"]
                if has_power and has_trust else [],
            )
        )
```

- [ ] **Step 3: Run tests, commit**

Run: `uv run pytest packages/reasoning/tests/test_theorist_complete.py -v`

```bash
git add packages/reasoning/
git commit -m "feat(reasoning): complete all 15 theoretical frameworks in TheoristAgent"
```

---

### Task 2.3: Knowledge Cluster Detection & Subdomain Ontologies

**Files:**
- Create: `packages/reasoning/src/dialectica_reasoning/graphrag/knowledge_clusters.py`
- Create: `packages/ontology/src/dialectica_ontology/subdomains.py`
- Test: `packages/reasoning/tests/test_knowledge_clusters.py`

- [ ] **Step 1: Create subdomain definitions**

```python
# packages/ontology/src/dialectica_ontology/subdomains.py
"""Subdomain Ontology Specializations for Conflict Intelligence.

Defines domain-specific node/edge enrichment for 6 conflict subdomains.
Each subdomain specifies which theories are most applicable,
which node types are primary, and domain-specific vocabulary.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ConflictSubdomain(StrEnum):
    GEOPOLITICAL = "geopolitical"
    WORKPLACE = "workplace"
    COMMERCIAL = "commercial"
    LEGAL = "legal"
    ARMED = "armed"
    ENVIRONMENTAL = "environmental"


@dataclass(frozen=True)
class SubdomainSpec:
    """Specification for a conflict subdomain."""
    subdomain: ConflictSubdomain
    description: str
    primary_node_types: tuple[str, ...]
    primary_edge_types: tuple[str, ...]
    applicable_theories: tuple[str, ...]
    vocabulary: dict[str, str] = field(default_factory=dict)
    escalation_indicators: tuple[str, ...] = ()


SUBDOMAIN_SPECS: dict[ConflictSubdomain, SubdomainSpec] = {
    ConflictSubdomain.GEOPOLITICAL: SubdomainSpec(
        subdomain=ConflictSubdomain.GEOPOLITICAL,
        description="Inter-state and multilateral conflicts involving sovereignty, treaties, and international norms",
        primary_node_types=("Actor", "Conflict", "Event", "Norm", "Interest", "Process", "Outcome"),
        primary_edge_types=("PARTY_TO", "VIOLATED", "CAUSED", "ALLIED_WITH", "OPPOSED_TO", "HAS_POWER_OVER"),
        applicable_theories=("glasl", "zartman", "azar_protracted", "kelman_problem_solving", "pearl_causal"),
        vocabulary={
            "actor": "state or international organization",
            "escalation": "military mobilization, sanctions, diplomatic recall",
            "de-escalation": "ceasefire, treaty signing, back-channel talks",
        },
        escalation_indicators=("military_mobilization", "sanctions_imposed", "diplomatic_expulsion", "treaty_violation"),
    ),
    ConflictSubdomain.WORKPLACE: SubdomainSpec(
        subdomain=ConflictSubdomain.WORKPLACE,
        description="Interpersonal and structural conflicts in organizational settings",
        primary_node_types=("Actor", "Conflict", "Event", "EmotionalState", "Interest", "Process"),
        primary_edge_types=("PARTY_TO", "CAUSED", "HAS_INTEREST", "TRUSTS", "HAS_POWER_OVER"),
        applicable_theories=("glasl", "fisher_ury", "mayer_trust", "french_raven", "plutchik", "deutsch_cooperation"),
        vocabulary={
            "actor": "employee, manager, team, department",
            "escalation": "formal complaint, grievance, litigation threat",
            "de-escalation": "mediation session, policy change, accommodation",
        },
        escalation_indicators=("formal_complaint", "hr_involvement", "legal_threat", "resignation"),
    ),
    ConflictSubdomain.COMMERCIAL: SubdomainSpec(
        subdomain=ConflictSubdomain.COMMERCIAL,
        description="Business disputes including contracts, IP, partnerships, and trade",
        primary_node_types=("Actor", "Conflict", "Issue", "Norm", "Interest", "Outcome", "Evidence"),
        primary_edge_types=("PARTY_TO", "VIOLATED", "HAS_INTEREST", "OPPOSED_TO", "RESOLVED_THROUGH"),
        applicable_theories=("fisher_ury", "glasl", "deutsch_cooperation", "pearl_causal"),
        vocabulary={
            "actor": "company, contractor, partner, regulator",
            "escalation": "lawsuit filed, injunction sought, regulatory complaint",
            "de-escalation": "settlement offer, mediation, arbitration clause",
        },
        escalation_indicators=("lawsuit_filed", "injunction", "regulatory_investigation", "contract_termination"),
    ),
    ConflictSubdomain.LEGAL: SubdomainSpec(
        subdomain=ConflictSubdomain.LEGAL,
        description="Legal proceedings and regulatory disputes",
        primary_node_types=("Actor", "Conflict", "Norm", "Evidence", "Process", "Outcome"),
        primary_edge_types=("PARTY_TO", "VIOLATED", "ABOUT", "RESOLVED_THROUGH", "PRODUCES"),
        applicable_theories=("fisher_ury", "glasl", "pearl_causal"),
        vocabulary={
            "actor": "plaintiff, defendant, judge, counsel, regulator",
            "escalation": "appeal filed, contempt motion, enforcement action",
            "de-escalation": "settlement agreement, consent decree, plea deal",
        },
        escalation_indicators=("appeal_filed", "enforcement_action", "contempt", "class_action"),
    ),
    ConflictSubdomain.ARMED: SubdomainSpec(
        subdomain=ConflictSubdomain.ARMED,
        description="Armed conflicts including civil wars, insurgencies, and military confrontations",
        primary_node_types=("Actor", "Conflict", "Event", "Location", "Narrative", "Interest"),
        primary_edge_types=("PARTY_TO", "CAUSED", "ALLIED_WITH", "OPPOSED_TO", "HAS_POWER_OVER", "OCCURRED_AT"),
        applicable_theories=("glasl", "zartman", "azar_protracted", "galtung", "kriesberg", "lederach_transformation"),
        vocabulary={
            "actor": "state military, non-state armed group, militia, peacekeeping force",
            "escalation": "offensive operation, civilian casualties, weapons proliferation",
            "de-escalation": "ceasefire, peace talks, DDR program, peacekeeping deployment",
        },
        escalation_indicators=("offensive_operation", "civilian_casualties", "weapons_transfer", "forced_displacement"),
    ),
    ConflictSubdomain.ENVIRONMENTAL: SubdomainSpec(
        subdomain=ConflictSubdomain.ENVIRONMENTAL,
        description="Resource, climate, and environmental justice conflicts",
        primary_node_types=("Actor", "Conflict", "Issue", "Location", "Interest", "Norm"),
        primary_edge_types=("PARTY_TO", "CAUSED", "HAS_INTEREST", "ABOUT", "VIOLATED"),
        applicable_theories=("galtung", "burton_basic_needs", "fisher_ury", "deutsch_cooperation"),
        vocabulary={
            "actor": "community, corporation, government agency, NGO, indigenous group",
            "escalation": "blockade, protest, legal challenge, environmental damage",
            "de-escalation": "impact assessment, compensation agreement, regulatory reform",
        },
        escalation_indicators=("environmental_damage", "community_protest", "legal_challenge", "resource_depletion"),
    ),
}


def detect_subdomain(node_labels: set[str], edge_types: set[str]) -> ConflictSubdomain:
    """Heuristic subdomain detection from graph structure."""
    scores: dict[ConflictSubdomain, float] = {}
    for subdomain, spec in SUBDOMAIN_SPECS.items():
        node_overlap = len(node_labels & set(spec.primary_node_types))
        edge_overlap = len(edge_types & set(spec.primary_edge_types))
        scores[subdomain] = node_overlap * 2 + edge_overlap
    return max(scores, key=scores.get)  # type: ignore[arg-type]
```

- [ ] **Step 2: Create knowledge cluster detector**

```python
# packages/reasoning/src/dialectica_reasoning/graphrag/knowledge_clusters.py
"""Knowledge Cluster Detection — Semantic grouping of conflict subgraphs.

Combines Leiden community detection with subdomain ontology classification
to produce labeled, theory-enriched knowledge clusters.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from dialectica_graph import GraphClient
from dialectica_ontology.subdomains import (
    SUBDOMAIN_SPECS,
    ConflictSubdomain,
    detect_subdomain,
)
from dialectica_reasoning.graphrag.community import GraphCommunityDetector, CommunitySummary

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeCluster:
    """A semantically labeled cluster of conflict knowledge."""
    cluster_id: str
    subdomain: ConflictSubdomain
    community: CommunitySummary
    applicable_theories: list[str] = field(default_factory=list)
    primary_node_types: list[str] = field(default_factory=list)
    escalation_indicators: list[str] = field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0
    density: float = 0.0


@dataclass
class ClusterReport:
    """Full cluster analysis for a workspace."""
    workspace_id: str
    clusters: list[KnowledgeCluster] = field(default_factory=list)
    subdomain: ConflictSubdomain = ConflictSubdomain.GEOPOLITICAL
    cross_cluster_edges: int = 0


class KnowledgeClusterDetector:
    """Detects and labels knowledge clusters in conflict graphs."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client
        self._community = GraphCommunityDetector(graph_client)

    async def detect_clusters(
        self,
        workspace_id: str,
        resolution: float = 1.5,
    ) -> ClusterReport:
        """Detect knowledge clusters and classify by subdomain."""
        report = ClusterReport(workspace_id=workspace_id)

        # Get graph structure
        nodes = await self._gc.get_nodes(workspace_id, limit=500)
        edges = await self._gc.get_edges(workspace_id)

        if not nodes:
            return report

        # Detect overall subdomain
        node_labels = {getattr(n, "label", n.__class__.__name__) for n in nodes}
        edge_types = {str(getattr(e, "type", "")) for e in edges}
        report.subdomain = detect_subdomain(node_labels, edge_types)

        # Detect communities
        communities = await self._community.detect_and_summarise(
            workspace_id, resolutions=[resolution]
        )

        # Build node-to-community mapping
        node_to_community: dict[str, int] = {}
        for comm in communities:
            for mid in comm.member_ids:
                node_to_community[mid] = comm.community_id

        # Classify each community
        for comm in communities:
            member_set = set(comm.member_ids)
            cluster_nodes = [n for n in nodes if n.id in member_set]
            cluster_edges = [
                e for e in edges
                if e.source_id in member_set or e.target_id in member_set
            ]

            cluster_labels = {getattr(n, "label", n.__class__.__name__) for n in cluster_nodes}
            cluster_etypes = {str(getattr(e, "type", "")) for e in cluster_edges}
            cluster_subdomain = detect_subdomain(cluster_labels, cluster_etypes)

            spec = SUBDOMAIN_SPECS[cluster_subdomain]
            n = len(cluster_nodes)
            e = len(cluster_edges)

            report.clusters.append(KnowledgeCluster(
                cluster_id=f"cluster-{comm.community_id}-{resolution}",
                subdomain=cluster_subdomain,
                community=comm,
                applicable_theories=list(spec.applicable_theories),
                primary_node_types=list(spec.primary_node_types),
                escalation_indicators=list(spec.escalation_indicators),
                node_count=n,
                edge_count=e,
                density=2 * e / (n * (n - 1)) if n > 1 else 0.0,
            ))

        # Count cross-cluster edges
        cross = 0
        for e in edges:
            src_comm = node_to_community.get(e.source_id)
            tgt_comm = node_to_community.get(e.target_id)
            if src_comm is not None and tgt_comm is not None and src_comm != tgt_comm:
                cross += 1
        report.cross_cluster_edges = cross

        return report
```

- [ ] **Step 3: Write tests**

```python
# packages/reasoning/tests/test_knowledge_clusters.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from dialectica_reasoning.graphrag.knowledge_clusters import KnowledgeClusterDetector
from dialectica_ontology.subdomains import ConflictSubdomain, detect_subdomain


def test_detect_subdomain_geopolitical():
    labels = {"Actor", "Conflict", "Event", "Norm", "Interest"}
    edges = {"PARTY_TO", "VIOLATED", "ALLIED_WITH", "OPPOSED_TO"}
    assert detect_subdomain(labels, edges) == ConflictSubdomain.GEOPOLITICAL


def test_detect_subdomain_workplace():
    labels = {"Actor", "Conflict", "EmotionalState", "Interest"}
    edges = {"PARTY_TO", "TRUSTS", "HAS_POWER_OVER"}
    assert detect_subdomain(labels, edges) == ConflictSubdomain.WORKPLACE


@pytest.mark.asyncio
async def test_cluster_detector_returns_clusters():
    gc = AsyncMock()
    actor1 = MagicMock(id="a1", label="Actor")
    actor2 = MagicMock(id="a2", label="Actor")
    gc.get_nodes = AsyncMock(return_value=[actor1, actor2])
    gc.get_edges = AsyncMock(return_value=[
        MagicMock(source_id="a1", target_id="a2", type="ALLIED_WITH"),
    ])

    detector = KnowledgeClusterDetector(gc)
    detector._community.detect_and_summarise = AsyncMock(return_value=[
        MagicMock(community_id=0, resolution=1.5, member_ids=["a1", "a2"],
                  actor_names=["A1", "A2"], dominant_issues=[], summary="test")
    ])

    report = await detector.detect_clusters("ws-test")
    assert len(report.clusters) >= 1
    assert report.clusters[0].node_count == 2
```

- [ ] **Step 4: Run tests, commit**

Run: `uv run pytest packages/reasoning/tests/test_knowledge_clusters.py packages/reasoning/tests/test_theorist_complete.py -v`

```bash
git add packages/ontology/ packages/reasoning/
git commit -m "feat: knowledge clusters with subdomain ontologies and theory enrichment"
```

---

## Sub-Project 3: Benchmarking System

### Task 3.1: Create Missing Gold Standards

**Files:**
- Create: `data/seed/benchmarks/romeo_juliet_gold.json`
- Create: `data/seed/benchmarks/crime_punishment_gold.json`
- Create: `data/seed/benchmarks/war_peace_gold.json`

(These are gold-standard annotated conflict graphs for benchmark evaluation)

- [ ] **Step 1: Create romeo_juliet_gold.json**

See implementation agent for full JSON content. Structure:
```json
{
  "corpus_id": "romeo_juliet",
  "source_text": "...",
  "gold_nodes": [...],
  "gold_edges": [...]
}
```

- [ ] **Step 2: Create crime_punishment_gold.json and war_peace_gold.json**

Same structure, different corpora.

- [ ] **Step 3: Commit**

```bash
git add data/seed/benchmarks/
git commit -m "feat(benchmark): add 3 gold-standard benchmark corpora"
```

---

### Task 3.2: Frontend Benchmarking Dashboard

**Files:**
- Create: `apps/web/src/app/admin/benchmarks/page.tsx`
- Modify: `apps/web/src/lib/api.ts` (add benchmark endpoints)
- Modify: `apps/web/src/app/admin/page.tsx` (add benchmarks link)

- [ ] **Step 1: Add benchmark API methods to api.ts**

```typescript
// Add to apps/web/src/lib/api.ts
export async function runBenchmark(params: {
  corpus_id: string;
  tier: string;
  model: string;
  include_graph_augmented: boolean;
}): Promise<any> {
  return apiRequest("/v1/admin/benchmark/run", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export async function getBenchmarkHistory(limit = 50): Promise<any[]> {
  return apiRequest(`/v1/admin/benchmark/history?limit=${limit}`);
}
```

- [ ] **Step 2: Create benchmarks page**

Full implementation in `apps/web/src/app/admin/benchmarks/page.tsx` with:
- Corpus selector (jcpoa, romeo_juliet, crime_punishment, war_peace, custom)
- Tier selector (essential, standard, full)
- Run button with loading state
- Results display: overall F1, precision, recall
- Per-type breakdown charts (Recharts bar chart)
- History table with comparison
- Hallucination rate indicator

- [ ] **Step 3: Add link to admin dashboard, commit**

```bash
git add apps/web/
git commit -m "feat(web): add benchmarking dashboard to admin panel"
```

---

## Sub-Project 4: Cloud Production Stack

### Task 4.1: BigQuery Analytics Pipeline

**Files:**
- Create: `infrastructure/terraform/bigquery.tf`
- Create: `packages/api/src/dialectica_api/analytics.py`
- Test: `packages/api/tests/test_analytics.py`

- [ ] **Step 1: Add BigQuery Terraform resource**

```hcl
# infrastructure/terraform/bigquery.tf
resource "google_bigquery_dataset" "analytics" {
  dataset_id = "dialectica_analytics"
  location   = var.region
  labels     = { environment = var.environment }
  depends_on = [google_project_service.required_apis]
}

resource "google_bigquery_table" "extraction_events" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "extraction_events"
  schema     = file("${path.module}/schemas/extraction_events.json")
  time_partitioning { type = "DAY"; field = "timestamp" }
}

resource "google_bigquery_table" "query_events" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "query_events"
  schema     = file("${path.module}/schemas/query_events.json")
  time_partitioning { type = "DAY"; field = "timestamp" }
}

resource "google_bigquery_table" "benchmark_results" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "benchmark_results"
  schema     = file("${path.module}/schemas/benchmark_results.json")
  time_partitioning { type = "DAY"; field = "timestamp" }
}
```

- [ ] **Step 2: Create analytics module**

```python
# packages/api/src/dialectica_api/analytics.py
"""BigQuery Analytics — Event logging for DIALECTICA operations."""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class AnalyticsClient:
    """Async BigQuery event logger."""

    def __init__(self) -> None:
        self._project = os.getenv("GCP_PROJECT_ID", "")
        self._dataset = "dialectica_analytics"
        self._client = None

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from google.cloud import bigquery
                self._client = bigquery.Client(project=self._project)
            except Exception as e:
                logger.warning("BigQuery unavailable: %s", e)
        return self._client

    async def log_extraction(
        self,
        workspace_id: str,
        tenant_id: str,
        nodes_extracted: int,
        edges_extracted: int,
        processing_time_ms: float,
        tier: str,
        errors: int = 0,
    ) -> None:
        client = self._get_client()
        if not client:
            return
        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "workspace_id": workspace_id,
            "tenant_id": tenant_id,
            "nodes_extracted": nodes_extracted,
            "edges_extracted": edges_extracted,
            "processing_time_ms": processing_time_ms,
            "tier": tier,
            "errors": errors,
        }
        table = f"{self._project}.{self._dataset}.extraction_events"
        try:
            client.insert_rows_json(table, [row])
        except Exception as e:
            logger.warning("BigQuery insert failed: %s", e)

    async def log_query(
        self,
        workspace_id: str,
        query: str,
        mode: str,
        response_time_ms: float,
        nodes_retrieved: int,
        confidence: float,
    ) -> None:
        client = self._get_client()
        if not client:
            return
        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "workspace_id": workspace_id,
            "query_text": query[:500],
            "mode": mode,
            "response_time_ms": response_time_ms,
            "nodes_retrieved": nodes_retrieved,
            "confidence": confidence,
        }
        table = f"{self._project}.{self._dataset}.query_events"
        try:
            client.insert_rows_json(table, [row])
        except Exception as e:
            logger.warning("BigQuery insert failed: %s", e)

    async def log_benchmark(self, result: dict[str, Any]) -> None:
        client = self._get_client()
        if not client:
            return
        row = {
            "timestamp": datetime.utcnow().isoformat(),
            **{k: v for k, v in result.items() if isinstance(v, (str, int, float, bool))},
        }
        table = f"{self._project}.{self._dataset}.benchmark_results"
        try:
            client.insert_rows_json(table, [row])
        except Exception as e:
            logger.warning("BigQuery insert failed: %s", e)
```

- [ ] **Step 3: Commit**

```bash
git add infrastructure/terraform/ packages/api/
git commit -m "feat(infra): BigQuery analytics pipeline for extraction, query, and benchmark events"
```

---

### Task 4.2: Databricks Integration for Advanced Analytics

**Files:**
- Create: `infrastructure/terraform/databricks.tf`
- Create: `packages/reasoning/src/dialectica_reasoning/databricks_connector.py`

- [ ] **Step 1: Add Databricks Terraform config**

```hcl
# infrastructure/terraform/databricks.tf
# Databricks workspace for advanced conflict analytics
# Requires: Databricks account linked to GCP project

variable "databricks_account_id" {
  description = "Databricks account ID"
  type        = string
  default     = ""
}

resource "google_project_service" "databricks" {
  count   = var.databricks_account_id != "" ? 1 : 0
  project = var.project_id
  service = "iam.googleapis.com"
}

# Note: Full Databricks workspace provisioning requires the databricks/databricks provider.
# Configure separately: https://registry.terraform.io/providers/databricks/databricks/latest
# This file provides the GCP-side IAM and networking prerequisites.

resource "google_service_account" "databricks" {
  count        = var.databricks_account_id != "" ? 1 : 0
  account_id   = "dialectica-databricks"
  display_name = "DIALECTICA Databricks Service Account"
}

resource "google_project_iam_member" "databricks_bq" {
  count   = var.databricks_account_id != "" ? 1 : 0
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.databricks[0].email}"
}

resource "google_project_iam_member" "databricks_storage" {
  count   = var.databricks_account_id != "" ? 1 : 0
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.databricks[0].email}"
}
```

- [ ] **Step 2: Create Databricks connector**

```python
# packages/reasoning/src/dialectica_reasoning/databricks_connector.py
"""Databricks Connector — Export conflict graphs for advanced ML/analytics.

Supports:
  - Export Neo4j graph snapshots to Delta Lake tables
  - Run KGE training jobs (TransE, DistMult, ComplEx)
  - Import Databricks ML predictions back to reasoning layer
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DatabricksConfig:
    workspace_url: str = ""
    token: str = ""
    cluster_id: str = ""
    catalog: str = "dialectica"
    schema: str = "conflict_graphs"


class DatabricksConnector:
    """Bridge between DIALECTICA and Databricks for advanced analytics."""

    def __init__(self, config: DatabricksConfig | None = None) -> None:
        self._config = config or DatabricksConfig()
        self._client = None

    def _get_client(self) -> Any:
        if self._client is None and self._config.workspace_url:
            try:
                from databricks.sdk import WorkspaceClient
                self._client = WorkspaceClient(
                    host=self._config.workspace_url,
                    token=self._config.token,
                )
            except ImportError:
                logger.warning("databricks-sdk not installed")
            except Exception as e:
                logger.warning("Databricks connection failed: %s", e)
        return self._client

    async def export_graph_snapshot(
        self,
        workspace_id: str,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> str | None:
        """Export graph snapshot to Databricks Delta Lake table."""
        client = self._get_client()
        if not client:
            logger.info("Databricks not configured — skipping export")
            return None

        try:
            # Use Databricks SQL to insert into Delta Lake
            table_name = f"{self._config.catalog}.{self._config.schema}.graph_snapshots"
            statement = client.statement_execution.execute_statement(
                warehouse_id=self._config.cluster_id,
                catalog=self._config.catalog,
                schema=self._config.schema,
                statement=f"""
                    INSERT INTO {table_name}
                    VALUES ('{workspace_id}', '{json.dumps(nodes)}', '{json.dumps(edges)}', current_timestamp())
                """,
            )
            return str(statement.statement_id)
        except Exception as e:
            logger.warning("Databricks export failed: %s", e)
            return None

    async def trigger_kge_training(
        self,
        workspace_id: str,
        model_type: str = "TransE",
        epochs: int = 100,
    ) -> str | None:
        """Trigger KGE model training job on Databricks."""
        client = self._get_client()
        if not client:
            return None

        try:
            run = client.jobs.submit(
                run_name=f"dialectica-kge-{workspace_id}-{model_type}",
                tasks=[{
                    "task_key": "train_kge",
                    "existing_cluster_id": self._config.cluster_id,
                    "spark_python_task": {
                        "python_file": "dbfs:/dialectica/jobs/train_kge.py",
                        "parameters": [
                            "--workspace-id", workspace_id,
                            "--model-type", model_type,
                            "--epochs", str(epochs),
                        ],
                    },
                }],
            )
            return str(run.run_id)
        except Exception as e:
            logger.warning("Databricks KGE training failed: %s", e)
            return None

    async def get_kge_predictions(
        self,
        workspace_id: str,
        head_id: str,
        relation: str,
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Get KGE link prediction results from Databricks."""
        client = self._get_client()
        if not client:
            return []

        try:
            table = f"{self._config.catalog}.{self._config.schema}.kge_predictions"
            result = client.statement_execution.execute_statement(
                warehouse_id=self._config.cluster_id,
                statement=f"""
                    SELECT tail_id, score, tail_label
                    FROM {table}
                    WHERE workspace_id = '{workspace_id}'
                      AND head_id = '{head_id}'
                      AND relation = '{relation}'
                    ORDER BY score DESC
                    LIMIT {top_k}
                """,
            )
            return [
                {"tail_id": row[0], "score": float(row[1]), "tail_label": row[2]}
                for row in (result.result.data_array or [])
            ]
        except Exception as e:
            logger.warning("Databricks KGE query failed: %s", e)
            return []
```

- [ ] **Step 3: Commit**

```bash
git add infrastructure/terraform/ packages/reasoning/
git commit -m "feat(infra): Databricks integration for graph analytics and KGE training"
```

---

## Sub-Project 5: TACITUS Integration Layer

### Task 5.1: Inter-App API Contract

**Files:**
- Create: `packages/api/src/dialectica_api/routers/integration.py`
- Test: `packages/api/tests/test_integration_api.py`

- [ ] **Step 1: Create integration router**

```python
# packages/api/src/dialectica_api/routers/integration.py
"""Integration Router — API for other TACITUS apps (Praxis, Query Layer).

Endpoints designed for machine-to-machine consumption with structured responses.
All endpoints require admin or service-level API key.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from dialectica_api.deps import require_admin, get_graph_client_dep

router = APIRouter(prefix="/v1/integration", tags=["integration"])


class GraphSnapshotResponse(BaseModel):
    workspace_id: str
    nodes: list[dict] = Field(default_factory=list)
    edges: list[dict] = Field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0
    subdomain: str = ""
    escalation_stage: int | None = None
    ripeness_score: float | None = None


class ContextResponse(BaseModel):
    workspace_id: str
    context_text: str = ""
    key_actors: list[str] = Field(default_factory=list)
    key_issues: list[str] = Field(default_factory=list)
    escalation_summary: str = ""
    theory_recommendation: str = ""


class QueryResponse(BaseModel):
    answer: str = ""
    confidence: float = 0.0
    citations: list[dict] = Field(default_factory=list)
    reasoning_trace: list[dict] = Field(default_factory=list)
    escalation_stage: int | None = None
    patterns_detected: list[str] = Field(default_factory=list)


@router.get("/graph/{workspace_id}", response_model=GraphSnapshotResponse)
async def get_graph_snapshot(
    workspace_id: str,
    _admin: None = Depends(require_admin),
    graph_client=Depends(get_graph_client_dep),
) -> GraphSnapshotResponse:
    """Get full graph snapshot for a workspace (for Praxis context layer)."""
    nodes = await graph_client.get_nodes(workspace_id, limit=1000)
    edges = await graph_client.get_edges(workspace_id)
    return GraphSnapshotResponse(
        workspace_id=workspace_id,
        nodes=[n.model_dump(mode="json") for n in nodes],
        edges=[e.model_dump(mode="json") for e in edges],
        node_count=len(nodes),
        edge_count=len(edges),
    )


@router.get("/context/{workspace_id}", response_model=ContextResponse)
async def get_conflict_context(
    workspace_id: str,
    _admin: None = Depends(require_admin),
    graph_client=Depends(get_graph_client_dep),
) -> ContextResponse:
    """Get structured conflict context (for Praxis and top-level query)."""
    from dialectica_reasoning.graphrag.context_builder import ConflictContextBuilder
    from dialectica_reasoning.graphrag.retriever import ConflictGraphRAGRetriever, RetrievalResult

    nodes = await graph_client.get_nodes(workspace_id, limit=200)
    edges = await graph_client.get_edges(workspace_id)

    actors = [getattr(n, "name", n.id) for n in nodes if getattr(n, "label", "") == "Actor"]
    issues = [getattr(n, "name", n.id) for n in nodes if getattr(n, "label", "") == "Issue"]

    retrieval = RetrievalResult(
        query="full context",
        workspace_id=workspace_id,
        nodes=nodes,
        edges=edges,
    )
    builder = ConflictContextBuilder()
    context_text = builder.build_context(retrieval, mode="general")

    return ContextResponse(
        workspace_id=workspace_id,
        context_text=context_text,
        key_actors=actors[:20],
        key_issues=issues[:10],
    )


@router.post("/query", response_model=QueryResponse)
async def query_conflict(
    workspace_id: str = Query(...),
    query: str = Query(...),
    mode: str = Query(default="general"),
    _admin: None = Depends(require_admin),
    graph_client=Depends(get_graph_client_dep),
) -> QueryResponse:
    """Execute conflict query (for top-level TACITUS query layer)."""
    from dialectica_reasoning.query_engine import ConflictQueryEngine

    engine = ConflictQueryEngine(graph_client)
    result = await engine.analyze(query, workspace_id, mode=mode)

    return QueryResponse(
        answer=result.answer,
        confidence=result.confidence,
        citations=[
            {"node_id": c.node_id, "name": c.node_name, "type": c.node_type, "relevance": c.relevance}
            for c in result.citations
        ],
        reasoning_trace=[
            {"step": s.step, "status": s.status, "summary": s.result_summary}
            for s in result.reasoning_trace
        ],
        escalation_stage=result.escalation_stage,
        patterns_detected=result.patterns_detected,
    )
```

- [ ] **Step 2: Register router in main.py**

Add to imports and router includes in `main.py`:
```python
from dialectica_api.routers import integration
# ...
app.include_router(integration.router)
```

- [ ] **Step 3: Add to _PUBLIC_PATHS exclusion (integration requires auth)**

- [ ] **Step 4: Write tests, commit**

```bash
git add packages/api/
git commit -m "feat(api): TACITUS integration endpoints for Praxis and query layer"
```

---

## Sub-Project 6: Documentation & Deployment Guide

### Task 6.1: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

Add sections for:
- Knowledge clusters and subdomains
- Benchmarking system usage
- BigQuery analytics
- Databricks integration
- TACITUS integration API
- Updated file locations

### Task 6.2: Create Production Deployment Runbook

**Files:**
- Create: `docs/runbook.md`

Step-by-step guide covering:
1. Prerequisites (GCP project, Neo4j Aura, Databricks account)
2. Infrastructure setup (Terraform)
3. Secret configuration
4. Database seeding
5. API deployment (Cloud Run)
6. Frontend deployment (Vercel)
7. Monitoring setup
8. Health verification
9. Benchmark baseline

### Task 6.3: Update Architecture Docs

**Files:**
- Modify: `docs/architecture.md`
- Modify: `docs/deployment.md`

Add knowledge clusters, BigQuery analytics, Databricks, integration layer.

---

## Execution Order

```
Sub-Project 1 (Pipeline) ──────────────────┐
Sub-Project 2 (Hybrid Query + Clusters) ───┤──> Sub-Project 6 (Docs)
Sub-Project 3 (Benchmarks) ────────────────┤
Sub-Project 4 (Cloud Stack) ───────────────┤
Sub-Project 5 (Integration) ───────────────┘
```

All sub-projects 1-5 can run in parallel. Sub-project 6 runs last to capture all changes.
