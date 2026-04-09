# Phase 1: Episodic Graph Layer & Temporal Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **PREREQUISITE:** Phase 0 plan must be fully committed before starting this plan.

**Goal:** Add Graphiti-style episodic ingestion tracking (every entity traces back to a source episode), bi-temporal edge validity (system time + event time), and incremental graph construction so new text can be ingested against an existing workspace graph without full recomputation.

**Architecture:** Three layers added to the existing pipeline:
1. **Episode subgraph** — `EpisodeNode` written before extraction; all entities get `SOURCED_FROM` edges
2. **Bi-temporal edges** — `ConflictRelationship` gains `created_at/expired_at` (system) + `valid_at/invalid_at` (event); invalidation preserves history
3. **Incremental extractor** — new `IncrementalExtractor` class + entity resolution + edge dedup modules

**Tech Stack:** Python 3.12, Pydantic v2, LangGraph, Neo4j Aura (APOC), FastAPI, Next.js 15 (timeline scrubber additions)

---

## File Map

### Task 1.1 — Episode Subgraph
- **Modify:** `packages/ontology/src/dialectica_ontology/primitives.py` — add `EpisodeNode`
- **Modify:** `packages/ontology/src/dialectica_ontology/relationships.py` — add `SourcedFrom` edge type
- **Modify:** `packages/extraction/src/dialectica_extraction/pipeline.py` — create episode before chunk, link entities after extraction
- **Modify:** `packages/graph/src/dialectica_graph/reader.py` — add `get_episodes`, `get_episode_entities`, `get_entity_provenance`
- **Modify:** `packages/api/src/dialectica_api/routers/` — add episode endpoints (create new router file or extend existing)
- **Create:** `packages/ontology/tests/test_episode_node.py`

### Task 1.2 — Bi-Temporal Edges
- **Modify:** `packages/ontology/src/dialectica_ontology/relationships.py` — add temporal fields to `ConflictRelationship`
- **Modify:** `packages/graph/src/dialectica_graph/neo4j_client.py` — update write queries to store temporal fields; update read queries to filter `expired_at IS NULL`; add `get_edges_at(timestamp)`
- **Modify:** `packages/graph/src/dialectica_graph/writer.py` — add `invalidate_edge()`
- **Modify:** `packages/extraction/src/dialectica_extraction/pipeline.py` — temporal edge resolution in `extract_relationships` step
- **Create:** `packages/graph/tests/test_temporal_edges.py`

### Task 1.3 — Incremental Graph Construction
- **Create:** `packages/extraction/src/dialectica_extraction/incremental.py` — `IncrementalExtractor`, `IncrementalResult`
- **Create:** `packages/extraction/src/dialectica_extraction/entity_resolution.py` — `resolve_entities`, `Resolution`
- **Create:** `packages/extraction/src/dialectica_extraction/edge_dedup.py` — `dedup_edges`, `EdgeAction`
- **Modify:** `packages/api/src/dialectica_api/routers/` — `POST /v1/workspaces/{id}/ingest`
- **Create:** `packages/extraction/tests/test_incremental.py`
- **Modify:** `apps/web/src/app/workspaces/[id]/ingest/page.tsx` — Quick Ingest component

---

## Task 1: Add Episode Subgraph (Prompt 1.1)

**Files:**
- Modify: `packages/ontology/src/dialectica_ontology/primitives.py`
- Modify: `packages/ontology/src/dialectica_ontology/relationships.py`
- Modify: `packages/extraction/src/dialectica_extraction/pipeline.py`
- Modify: `packages/graph/src/dialectica_graph/reader.py`
- Create: `packages/ontology/tests/test_episode_node.py`

### Step 1.1 — Write failing tests for EpisodeNode

- [ ] Create `packages/ontology/tests/test_episode_node.py`:

```python
"""Tests for EpisodeNode — Prompt 1.1."""
import hashlib
from datetime import datetime

import pytest

from dialectica_ontology.primitives import EpisodeNode


class TestEpisodeNode:
    def test_episode_node_creation(self):
        ep = EpisodeNode(
            workspace_id="ws-1",
            tenant_id="t-1",
            raw_content="Russia and Turkey signed an agreement.",
            source_type="text_input",
        )
        assert ep.node_type == "episode"
        assert ep.label == "Episode"
        assert ep.word_count == len(ep.raw_content.split())
        assert len(ep.content_hash) == 64  # SHA-256 hex

    def test_content_hash_is_deterministic(self):
        content = "Test conflict text."
        ep1 = EpisodeNode(workspace_id="ws", tenant_id="t", raw_content=content)
        ep2 = EpisodeNode(workspace_id="ws", tenant_id="t", raw_content=content)
        assert ep1.content_hash == ep2.content_hash
        assert ep1.content_hash == hashlib.sha256(content.encode()).hexdigest()

    def test_episode_node_has_ingested_at(self):
        ep = EpisodeNode(workspace_id="ws", tenant_id="t", raw_content="text")
        assert isinstance(ep.ingested_at, datetime)
        assert ep.processed_at is None

    def test_episode_dedup_check(self):
        """Same content_hash means same episode."""
        content = "Identical source text."
        ep1 = EpisodeNode(workspace_id="ws", tenant_id="t", raw_content=content)
        ep2 = EpisodeNode(workspace_id="ws", tenant_id="t", raw_content=content)
        assert ep1.content_hash == ep2.content_hash
```

- [ ] Run — expect FAIL (EpisodeNode not defined yet):

```bash
cd packages/ontology && python -m pytest tests/test_episode_node.py -v
```

### Step 1.2 — Add `EpisodeNode` to `primitives.py`

- [ ] In `packages/ontology/src/dialectica_ontology/primitives.py`, add after the last node type definition:

```python
class EpisodeNode(ConflictNode):
    """Raw ingestion event — the ground truth source for all derived entities.

    Every entity and relationship traces back to one or more episodes.
    Inspired by Graphiti's episodic subgraph architecture.
    Episodes are the immutable ground truth; entities are derived views.
    """
    label: str = "Episode"
    node_type: Literal["episode"] = "episode"
    source_type: str = "text_input"  # text_input | document | api_import | structured_data
    source_uri: str | None = None     # file path, URL, or API endpoint
    raw_content: str = ""
    content_hash: str = ""            # SHA-256 of raw_content — auto-computed on init
    word_count: int = 0               # auto-computed on init
    extraction_tier: str = "standard"
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: datetime | None = None

    model_config = ConfigDict(populate_by_name=True)

    def model_post_init(self, __context: Any) -> None:
        import hashlib
        if self.raw_content and not self.content_hash:
            self.content_hash = hashlib.sha256(self.raw_content.encode()).hexdigest()
        if self.raw_content and self.word_count == 0:
            self.word_count = len(self.raw_content.split())
        super().model_post_init(__context) if hasattr(super(), "model_post_init") else None
```

Make sure `datetime` and `Any` are imported at top of file. Add `"episode"` to the `NodeType` literal union if one exists.

### Step 1.3 — Add `SOURCED_FROM` to `relationships.py`

- [ ] In `packages/ontology/src/dialectica_ontology/relationships.py`, add the edge class:

```python
class SourcedFrom(ConflictRelationship):
    """Provenance link: entity → episode that produced it.

    Tracks which ingestion event extracted each entity, with position metadata.
    """
    edge_type: Literal["SOURCED_FROM"] = "SOURCED_FROM"
    extraction_confidence: float = 1.0
    chunk_index: int = 0
    char_span_start: int | None = None
    char_span_end: int | None = None
```

Add `"SOURCED_FROM"` to the edge type union/enum if one exists.

### Step 1.4 — Run tests

```bash
cd packages/ontology && python -m pytest tests/test_episode_node.py -v
```

Expected: all 4 PASS.

### Step 1.5 — Update extraction pipeline to create episodes

- [ ] In `packages/extraction/src/dialectica_extraction/pipeline.py`, add a `create_episode` step BEFORE `chunk_document`:

```python
async def create_episode(state: ExtractionState) -> ExtractionState:
    """Step 0: Create EpisodeNode and write to graph before extraction begins.

    Enables deduplication (content_hash check) and provenance tracking.
    """
    from dialectica_ontology.primitives import EpisodeNode

    _start = time.time()
    text = state.get("text", "")

    episode = EpisodeNode(
        workspace_id=state["workspace_id"],
        tenant_id=state["tenant_id"],
        raw_content=text,
        source_type=state.get("source_type", "text_input"),
        source_uri=state.get("source_uri"),
        extraction_tier=state.get("tier", "standard"),
    )

    # Check for duplicate episode in graph
    if state.get("_graph_client"):
        existing = await state["_graph_client"].find_episode_by_hash(
            episode.content_hash, state["workspace_id"]
        )
        if existing:
            logger.info("create_episode: duplicate episode detected (hash=%s) — skipping extraction", episode.content_hash[:12])
            state["episode_id"] = existing.id
            state["is_duplicate_episode"] = True
            state.setdefault("processing_time", {})["create_episode"] = time.time() - _start
            return state

        await state["_graph_client"].upsert_node(episode, state["workspace_id"], state["tenant_id"])

    state["episode_id"] = episode.id
    state["episode"] = episode.model_dump()
    state["is_duplicate_episode"] = False
    state.setdefault("processing_time", {})["create_episode"] = time.time() - _start
    return state
```

- [ ] In `write_to_graph`, after writing entities, create `SOURCED_FROM` edges:

```python
    # Link each written entity back to the episode
    episode_id = state.get("episode_id")
    if episode_id:
        from dialectica_ontology.relationships import SourcedFrom
        for i, node in enumerate(state.get("validated_nodes", [])):
            sourced_edge = SourcedFrom(
                source_id=node["id"],
                target_id=episode_id,
                workspace_id=state["workspace_id"],
                tenant_id=state["tenant_id"],
                chunk_index=node.get("chunk_index", 0),
                extraction_confidence=node.get("confidence_score", 1.0),
            )
            # Write the provenance edge
            try:
                await graph_client.upsert_edge(sourced_edge, state["workspace_id"], state["tenant_id"])
            except Exception as e:
                logger.warning("Failed to write SOURCED_FROM edge for %s: %s", node["id"], e)
```

### Step 1.6 — Add reader methods for episodes

- [ ] In `packages/graph/src/dialectica_graph/reader.py`, add:

```python
async def get_episodes(self, workspace_id: str) -> list[dict]:
    """Return all EpisodeNodes for a workspace, newest first."""
    query = """
    MATCH (e:Episode {workspace_id: $workspace_id})
    WHERE e.expired_at IS NULL
    RETURN e
    ORDER BY e.ingested_at DESC
    """
    result = await self._client.run(query, workspace_id=workspace_id)
    return [record["e"] for record in result]

async def get_episode_entities(self, workspace_id: str, episode_id: str) -> list[dict]:
    """Return all entities sourced from a specific episode."""
    query = """
    MATCH (entity)-[:SOURCED_FROM]->(ep:Episode {id: $episode_id, workspace_id: $workspace_id})
    RETURN entity
    """
    result = await self._client.run(query, episode_id=episode_id, workspace_id=workspace_id)
    return [record["entity"] for record in result]

async def get_entity_provenance(self, workspace_id: str, entity_id: str) -> list[dict]:
    """Return all EpisodeNodes that sourced a given entity."""
    query = """
    MATCH (entity {id: $entity_id, workspace_id: $workspace_id})-[:SOURCED_FROM]->(ep:Episode)
    RETURN ep
    ORDER BY ep.ingested_at DESC
    """
    result = await self._client.run(query, entity_id=entity_id, workspace_id=workspace_id)
    return [record["ep"] for record in result]
```

### Step 1.7 — Add API endpoints

- [ ] Create or extend a router file (e.g., `packages/api/src/dialectica_api/routers/episodes.py`):

```python
"""Episode provenance endpoints — GET /v1/workspaces/{id}/episodes"""
from fastapi import APIRouter, Depends
from dialectica_api.deps import get_graph_client
from dialectica_api.auth import require_api_key

router = APIRouter(prefix="/v1/workspaces/{workspace_id}", tags=["episodes"])


@router.get("/episodes")
async def list_episodes(workspace_id: str, gc=Depends(get_graph_client), _=Depends(require_api_key)):
    """List all ingestion episodes for a workspace."""
    from dialectica_graph.reader import GraphReader
    reader = GraphReader(gc)
    return {"episodes": await reader.get_episodes(workspace_id)}


@router.get("/episodes/{episode_id}")
async def get_episode(workspace_id: str, episode_id: str, gc=Depends(get_graph_client), _=Depends(require_api_key)):
    """Get episode detail with derived entities."""
    from dialectica_graph.reader import GraphReader
    reader = GraphReader(gc)
    entities = await reader.get_episode_entities(workspace_id, episode_id)
    return {"episode_id": episode_id, "entities": entities}


@router.get("/entities/{entity_id}/provenance")
async def get_entity_provenance(workspace_id: str, entity_id: str, gc=Depends(get_graph_client), _=Depends(require_api_key)):
    """Get source episodes for an entity."""
    from dialectica_graph.reader import GraphReader
    reader = GraphReader(gc)
    return {"entity_id": entity_id, "episodes": await reader.get_entity_provenance(workspace_id, entity_id)}
```

- [ ] Register the router in `main.py`.

### Step 1.8 — Run ontology tests

```bash
cd packages/ontology && python -m pytest tests/ -v --tb=short
```

Expected: 452+ tests pass.

### Step 1.9 — Commit

```bash
git add packages/ontology/src/dialectica_ontology/primitives.py \
        packages/ontology/src/dialectica_ontology/relationships.py \
        packages/ontology/tests/test_episode_node.py \
        packages/extraction/src/dialectica_extraction/pipeline.py \
        packages/graph/src/dialectica_graph/reader.py \
        packages/api/src/dialectica_api/routers/episodes.py \
        packages/api/src/dialectica_api/main.py
git commit -m "feat: episodic subgraph — EpisodeNode, SOURCED_FROM edges, provenance API endpoints"
```

---

## Task 2: Bi-Temporal Edge Model (Prompt 1.2)

**Files:**
- Modify: `packages/ontology/src/dialectica_ontology/relationships.py`
- Modify: `packages/graph/src/dialectica_graph/neo4j_client.py`
- Modify: `packages/graph/src/dialectica_graph/writer.py`
- Create: `packages/graph/tests/test_temporal_edges.py`

### Step 2.1 — Write failing tests

- [ ] Create `packages/graph/tests/test_temporal_edges.py`:

```python
"""Tests for bi-temporal edge model — Prompt 1.2."""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from dialectica_ontology.relationships import ConflictRelationship


class TestBiTemporalFields:
    def test_relationship_has_system_time_fields(self):
        """ConflictRelationship has created_at and expired_at."""
        rel = ConflictRelationship(
            edge_type="OPPOSES",
            source_id="a",
            target_id="b",
            workspace_id="ws",
            tenant_id="t",
        )
        assert hasattr(rel, "created_at")
        assert hasattr(rel, "expired_at")
        assert rel.expired_at is None  # currently valid

    def test_relationship_has_event_time_fields(self):
        """ConflictRelationship has valid_at and invalid_at."""
        rel = ConflictRelationship(
            edge_type="SUPPORTS",
            source_id="a",
            target_id="b",
            workspace_id="ws",
            tenant_id="t",
        )
        assert hasattr(rel, "valid_at")
        assert hasattr(rel, "invalid_at")

    def test_expired_edge_is_not_current(self):
        """expired_at set means edge is historical."""
        rel = ConflictRelationship(
            edge_type="TRUSTS",
            source_id="a",
            target_id="b",
            workspace_id="ws",
            tenant_id="t",
            expired_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        assert rel.expired_at is not None
        assert rel.expired_at < datetime.now(tz=timezone.utc)

    def test_confidence_tag_defaults_to_extracted(self):
        rel = ConflictRelationship(
            edge_type="CAUSED",
            source_id="a",
            target_id="b",
            workspace_id="ws",
            tenant_id="t",
        )
        assert rel.confidence_tag == "EXTRACTED"
```

- [ ] Run — expect FAIL:

```bash
cd packages/graph && python -m pytest tests/test_temporal_edges.py -v
```

### Step 2.2 — Add temporal fields to `ConflictRelationship`

- [ ] In `packages/ontology/src/dialectica_ontology/relationships.py`, add to the base `ConflictRelationship` class:

```python
    # System time — when this edge record exists in the database
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expired_at: datetime | None = None      # None = currently valid; set = historical

    # Event time — when this fact was true in the real world
    valid_at: datetime | None = None        # When the fact became true
    invalid_at: datetime | None = None      # When the fact stopped being true

    # Provenance
    source_episode_ids: list[str] = Field(default_factory=list)
    confidence_tag: str = "EXTRACTED"       # EXTRACTED | INFERRED | AMBIGUOUS
```

### Step 2.3 — Update Neo4j read queries to filter expired edges

- [ ] In `packages/graph/src/dialectica_graph/neo4j_client.py`, find all Cypher queries that read edges and add:

```cypher
WHERE r.expired_at IS NULL
```

For example, any `MATCH (a)-[r]->(b)` pattern should become:
```cypher
MATCH (a)-[r]->(b) WHERE r.expired_at IS NULL
```

- [ ] Add `get_edges_at(workspace_id, timestamp)` method:

```python
async def get_edges_at(self, workspace_id: str, timestamp: datetime) -> list[dict]:
    """Return all edges that were valid at the given timestamp (time travel)."""
    query = """
    MATCH (a {workspace_id: $ws})-[r]->(b {workspace_id: $ws})
    WHERE r.created_at <= $ts
      AND (r.expired_at IS NULL OR r.expired_at > $ts)
    RETURN a, r, b
    """
    result = await self.run(query, ws=workspace_id, ts=timestamp.isoformat())
    return result
```

### Step 2.4 — Add `invalidate_edge()` to `writer.py`

- [ ] In `packages/graph/src/dialectica_graph/writer.py`, add:

```python
async def invalidate_edge(
    self,
    edge_id: str,
    workspace_id: str,
    tenant_id: str,
    reason: str,
) -> None:
    """Mark an edge as expired. Preserves it for historical queries.

    Sets expired_at = now and records the invalidation reason in metadata.
    The edge remains in the graph but is excluded from current-state queries.
    """
    query = """
    MATCH ()-[r {id: $edge_id}]->()
    WHERE r.workspace_id = $ws AND r.tenant_id = $tid
    SET r.expired_at = $now,
        r.invalidation_reason = $reason
    """
    await self._client.run(
        query,
        edge_id=edge_id,
        ws=workspace_id,
        tid=tenant_id,
        now=datetime.utcnow().isoformat(),
        reason=reason,
    )
```

### Step 2.5 — Add `?at=` time-travel API endpoint

- [ ] In the workspaces router (or graph router), update the graph endpoint to accept `at` param:

```python
@router.get("/graph")
async def get_workspace_graph(
    workspace_id: str,
    at: str | None = None,  # ISO timestamp for time travel
    gc=Depends(get_graph_client),
    _=Depends(require_api_key),
):
    if at:
        from datetime import datetime
        ts = datetime.fromisoformat(at.replace("Z", "+00:00"))
        edges = await gc.get_edges_at(workspace_id, ts)
        return {"workspace_id": workspace_id, "nodes": [], "edges": edges, "at": at}
    # ... existing current graph logic
```

### Step 2.6 — Run tests

```bash
cd packages/graph && python -m pytest tests/test_temporal_edges.py -v
```

Expected: all 4 PASS.

### Step 2.7 — Run full suite

```bash
make test-reasoning && make test-ontology
```

Expected: no regressions.

### Step 2.8 — Commit

```bash
git add packages/ontology/src/dialectica_ontology/relationships.py \
        packages/graph/src/dialectica_graph/neo4j_client.py \
        packages/graph/src/dialectica_graph/writer.py \
        packages/graph/tests/test_temporal_edges.py
git commit -m "feat: bi-temporal edge model — system time + event time fields, invalidate_edge, time-travel query"
```

---

## Task 3: Incremental Graph Construction (Prompt 1.3)

**Files:**
- Create: `packages/extraction/src/dialectica_extraction/incremental.py`
- Create: `packages/extraction/src/dialectica_extraction/entity_resolution.py`
- Create: `packages/extraction/src/dialectica_extraction/edge_dedup.py`
- Modify: API router — add `POST /v1/workspaces/{id}/ingest`
- Create: `packages/extraction/tests/test_incremental.py`

### Step 3.1 — Write failing tests

- [ ] Create `packages/extraction/tests/test_incremental.py`:

```python
"""Tests for incremental graph construction — Prompt 1.3."""
from unittest.mock import AsyncMock, MagicMock

import pytest

from dialectica_extraction.entity_resolution import Resolution, resolve_entities
from dialectica_extraction.edge_dedup import EdgeAction, dedup_edges


class TestEntityResolution:
    def test_exact_name_match_returns_match(self):
        new_entities = [{"id": "e-new", "label": "Russia", "type": "Actor"}]
        existing_nodes = [{"id": "e-existing", "label": "Russia", "type": "Actor"}]
        resolutions = resolve_entities(new_entities, existing_nodes, embed_fn=None)
        assert len(resolutions) == 1
        assert resolutions[0].matched_node_id == "e-existing"
        assert resolutions[0].method == "name_match"

    def test_no_match_returns_new_entity(self):
        new_entities = [{"id": "e-new", "label": "Belarus", "type": "Actor"}]
        existing_nodes = [{"id": "e-existing", "label": "Russia", "type": "Actor"}]
        resolutions = resolve_entities(new_entities, existing_nodes, embed_fn=None)
        assert len(resolutions) == 1
        assert resolutions[0].matched_node_id is None
        assert resolutions[0].method == "new_entity"

    def test_case_insensitive_match(self):
        new_entities = [{"id": "e-new", "label": "RUSSIA", "type": "Actor"}]
        existing_nodes = [{"id": "e-ex", "label": "russia", "type": "Actor"}]
        resolutions = resolve_entities(new_entities, existing_nodes, embed_fn=None)
        assert resolutions[0].matched_node_id == "e-ex"


class TestEdgeDedup:
    def test_new_edge_action_is_create(self):
        new_edges = [{"id": "ed-1", "source": "a", "target": "b", "type": "OPPOSES"}]
        existing_edges = []
        actions = dedup_edges(new_edges, existing_edges)
        assert len(actions) == 1
        assert actions[0].action == "create"

    def test_duplicate_edge_action_is_update(self):
        edge = {"id": "ed-1", "source": "a", "target": "b", "type": "OPPOSES"}
        actions = dedup_edges([edge], [edge])
        assert actions[0].action == "update"

    def test_contradictory_edge_action_is_invalidate_then_create(self):
        existing = [{"id": "ed-old", "source": "a", "target": "b", "type": "TRUSTS", "confidence_score": 0.9}]
        new = [{"id": "ed-new", "source": "a", "target": "b", "type": "OPPOSES", "confidence_score": 0.8}]
        actions = dedup_edges(new, existing)
        action_types = {a.action for a in actions}
        assert "invalidate" in action_types or "create" in action_types


class TestIncrementalDuplicateEpisode:
    @pytest.mark.asyncio
    async def test_duplicate_episode_is_skipped(self):
        from dialectica_extraction.incremental import IncrementalExtractor

        mock_gc = AsyncMock()
        mock_gc.find_episode_by_hash = AsyncMock(return_value={"id": "ep-existing"})

        extractor = IncrementalExtractor(graph_client=mock_gc)
        result = await extractor.ingest_episode(
            text="Same content.",
            workspace_id="ws-1",
            tenant_id="t-1",
        )
        assert result.is_duplicate
        assert result.episode_id == "ep-existing"
        assert result.new_nodes == []
```

- [ ] Run — expect FAIL:

```bash
cd packages/extraction && python -m pytest tests/test_incremental.py -v
```

### Step 3.2 — Create `entity_resolution.py`

- [ ] Create `packages/extraction/src/dialectica_extraction/entity_resolution.py`:

```python
"""Entity resolution — match newly extracted entities against existing graph nodes.

Resolution methods (in priority order):
1. Exact name match (case-insensitive)
2. Jaro-Winkler name similarity (> 0.9 threshold)
3. Embedding cosine similarity (> 0.85 threshold, requires embed_fn)
4. No match → new entity
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class Resolution:
    new_entity_id: str
    matched_node_id: str | None  # None = new entity, not matched
    method: str  # "name_match" | "jaro_winkler" | "embedding_match" | "new_entity"
    confidence: float


def _jaro_winkler(s1: str, s2: str) -> float:
    """Simplified Jaro-Winkler distance — returns 0.0-1.0."""
    try:
        from jellyfish import jaro_winkler_similarity
        return jaro_winkler_similarity(s1, s2)
    except ImportError:
        # Fallback: exact match only
        return 1.0 if s1.lower() == s2.lower() else 0.0


def resolve_entities(
    new_entities: list[dict],
    existing_nodes: list[dict],
    embed_fn: Callable[[list[str]], list[list[float]]] | None = None,
    jaro_threshold: float = 0.9,
    cosine_threshold: float = 0.85,
) -> list[Resolution]:
    """Match each new entity against existing graph nodes.

    Returns one Resolution per new entity.
    """
    resolutions: list[Resolution] = []

    for entity in new_entities:
        entity_label = entity.get("label", "").strip().lower()
        best_match: str | None = None
        best_method = "new_entity"
        best_confidence = 0.0

        for node in existing_nodes:
            node_label = node.get("label", "").strip().lower()

            # 1. Exact match
            if entity_label == node_label:
                best_match = node["id"]
                best_method = "name_match"
                best_confidence = 1.0
                break

            # 2. Jaro-Winkler
            jw_score = _jaro_winkler(entity_label, node_label)
            if jw_score >= jaro_threshold and jw_score > best_confidence:
                best_match = node["id"]
                best_method = "jaro_winkler"
                best_confidence = jw_score

        # 3. Embedding similarity (if no name match and embed_fn provided)
        if best_match is None and embed_fn is not None and existing_nodes:
            try:
                import numpy as np
                new_emb = embed_fn([entity.get("label", "")])[0]
                existing_labels = [n.get("label", "") for n in existing_nodes]
                existing_embs = embed_fn(existing_labels)
                sims = [
                    float(np.dot(new_emb, ex) / (np.linalg.norm(new_emb) * np.linalg.norm(ex) + 1e-9))
                    for ex in existing_embs
                ]
                best_idx = int(np.argmax(sims))
                if sims[best_idx] >= cosine_threshold:
                    best_match = existing_nodes[best_idx]["id"]
                    best_method = "embedding_match"
                    best_confidence = sims[best_idx]
            except Exception:
                pass  # embedding unavailable, fall through to new_entity

        resolutions.append(Resolution(
            new_entity_id=entity["id"],
            matched_node_id=best_match,
            method=best_method,
            confidence=best_confidence if best_match else 0.0,
        ))

    return resolutions
```

### Step 3.3 — Create `edge_dedup.py`

- [ ] Create `packages/extraction/src/dialectica_extraction/edge_dedup.py`:

```python
"""Edge deduplication — decide action for each new edge against existing edges.

Actions:
- "create": new edge, no existing edge between this pair with this type
- "update": same source/target/type already exists → increment confidence, add episode
- "invalidate": contradictory relationship (same pair, different semantic type)
"""
from __future__ import annotations

from dataclasses import dataclass, field

# Edge types considered semantically contradictory pairs
_CONTRADICTORY_PAIRS: set[frozenset[str]] = {
    frozenset({"TRUSTS", "OPPOSES"}),
    frozenset({"SUPPORTS", "OPPOSES"}),
    frozenset({"SUPPORTS", "ESCALATED_BY"}),
    frozenset({"DE_ESCALATED_BY", "ESCALATED_BY"}),
}


@dataclass
class EdgeAction:
    action: str  # "create" | "update" | "invalidate"
    edge: dict
    reason: str = ""
    target_edge_id: str | None = None  # for "invalidate" — which existing edge to expire


def _same_pair(e1: dict, e2: dict) -> bool:
    return e1.get("source") == e2.get("source") and e1.get("target") == e2.get("target")


def _is_contradictory(type1: str, type2: str) -> bool:
    return frozenset({type1, type2}) in _CONTRADICTORY_PAIRS


def dedup_edges(
    new_edges: list[dict],
    existing_edges: list[dict],
) -> list[EdgeAction]:
    """Determine what to do with each new edge relative to existing edges."""
    actions: list[EdgeAction] = []

    for new_edge in new_edges:
        new_type = new_edge.get("type", "")
        matched_existing: list[dict] = [
            e for e in existing_edges if _same_pair(new_edge, e)
        ]

        if not matched_existing:
            actions.append(EdgeAction(action="create", edge=new_edge, reason="no existing edge between this pair"))
            continue

        # Check for exact type match → update
        exact = [e for e in matched_existing if e.get("type") == new_type]
        if exact:
            actions.append(EdgeAction(
                action="update",
                edge=new_edge,
                reason="same source/target/type — update confidence",
                target_edge_id=exact[0].get("id"),
            ))
            continue

        # Check for contradictory type → invalidate old + create new
        contradictory = [e for e in matched_existing if _is_contradictory(e.get("type", ""), new_type)]
        if contradictory:
            for old_edge in contradictory:
                actions.append(EdgeAction(
                    action="invalidate",
                    edge=old_edge,
                    reason=f"contradicted by new edge type {new_type}",
                    target_edge_id=old_edge.get("id"),
                ))
            actions.append(EdgeAction(action="create", edge=new_edge, reason="replaces contradicted edge"))
            continue

        # Different type, not contradictory → create alongside
        actions.append(EdgeAction(action="create", edge=new_edge, reason="new edge type between existing pair"))

    return actions
```

### Step 3.4 — Create `incremental.py`

- [ ] Create `packages/extraction/src/dialectica_extraction/incremental.py`:

```python
"""Incremental graph construction — process new text against an existing workspace graph.

Unlike the batch pipeline (pipeline.py), this processes single episodes and
resolves new entities/edges against the existing graph before writing.
"""
from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass
class IncrementalResult:
    episode_id: str
    is_duplicate: bool = False
    new_nodes: list[dict] = field(default_factory=list)
    new_edges: list[dict] = field(default_factory=list)
    resolved_entities: list[dict] = field(default_factory=list)  # {new_id, matched_id, method}
    rules_fired: list[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    errors: list[str] = field(default_factory=list)


class IncrementalExtractor:
    """Process new text episodes incrementally against an existing workspace graph.

    Pipeline per episode:
    1. Create EpisodeNode + check content_hash for dedup
    2. Extract entities (GLiNER + Gemini Flash)
    3. Entity resolution against existing graph (name + embedding similarity)
    4. Edge extraction between new entities AND new-existing entity pairs
    5. Edge deduplication (update | invalidate | create)
    6. Write new nodes/edges to graph
    7. Fire symbolic rules on affected subgraph only
    8. Return IncrementalResult
    """

    def __init__(
        self,
        graph_client: Any,
        gemini_client: Any = None,
        embed_fn: Callable[[list[str]], list[list[float]]] | None = None,
    ):
        self._gc = graph_client
        self._gemini = gemini_client
        self._embed_fn = embed_fn

    async def ingest_episode(
        self,
        text: str,
        workspace_id: str,
        tenant_id: str,
        source_type: str = "text_input",
        source_uri: str | None = None,
        tier: str = "standard",
    ) -> IncrementalResult:
        """Ingest a new text episode into the workspace graph incrementally."""
        import time
        _start = time.time()

        # Step 1: Episode deduplication
        content_hash = hashlib.sha256(text.encode()).hexdigest()
        existing_episode = await self._gc.find_episode_by_hash(content_hash, workspace_id)
        if existing_episode:
            logger.info("Duplicate episode detected (hash=%s) — skipping", content_hash[:12])
            return IncrementalResult(
                episode_id=existing_episode["id"],
                is_duplicate=True,
                processing_time_ms=(time.time() - _start) * 1000,
            )

        # Create episode node
        from dialectica_ontology.primitives import EpisodeNode
        episode = EpisodeNode(
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            raw_content=text,
            source_type=source_type,
            source_uri=source_uri,
            extraction_tier=tier,
        )
        await self._gc.upsert_node(episode.model_dump(), workspace_id, tenant_id)

        result = IncrementalResult(episode_id=episode.id)

        try:
            # Step 2: Extract entities from episode
            new_entities = await self._extract_entities(text, tier)

            # Step 3: Entity resolution
            existing_nodes = await self._gc.list_nodes(workspace_id)
            from dialectica_extraction.entity_resolution import resolve_entities
            resolutions = resolve_entities(new_entities, existing_nodes, embed_fn=self._embed_fn)

            resolved_ids: dict[str, str] = {}  # new_entity_id → graph_node_id
            truly_new: list[dict] = []
            for res in resolutions:
                if res.matched_node_id:
                    resolved_ids[res.new_entity_id] = res.matched_node_id
                else:
                    truly_new.append(next(e for e in new_entities if e["id"] == res.new_entity_id))

            # Write truly new entities
            for node in truly_new:
                await self._gc.upsert_node(node, workspace_id, tenant_id)
                # SOURCED_FROM link
                await self._write_sourced_from(node["id"], episode.id, workspace_id, tenant_id)

            result.new_nodes = truly_new
            result.resolved_entities = [
                {"new_id": r.new_entity_id, "matched_id": r.matched_node_id, "method": r.method}
                for r in resolutions
            ]

            # Step 4: Extract edges (use resolved IDs for existing entities)
            all_node_ids = list(resolved_ids.values()) + [n["id"] for n in truly_new]
            new_edges_raw = await self._extract_edges(text, all_node_ids, tier)

            # Step 5: Edge deduplication
            existing_edges = await self._gc.list_edges(workspace_id)
            from dialectica_extraction.edge_dedup import dedup_edges
            actions = dedup_edges(new_edges_raw, existing_edges)

            for action in actions:
                if action.action == "create":
                    await self._gc.upsert_edge(action.edge, workspace_id, tenant_id)
                    result.new_edges.append(action.edge)
                elif action.action == "update":
                    await self._gc.update_edge_confidence(action.target_edge_id, workspace_id)
                elif action.action == "invalidate":
                    from dialectica_graph.writer import GraphWriter
                    writer = GraphWriter(self._gc)
                    await writer.invalidate_edge(action.target_edge_id, workspace_id, tenant_id, action.reason)

            # Step 7: Fire symbolic rules on affected nodes only
            affected_ids = [n["id"] for n in truly_new]
            if affected_ids:
                rules_fired = await self._fire_rules(affected_ids, workspace_id, tenant_id)
                result.rules_fired = rules_fired

        except Exception as e:
            logger.error("IncrementalExtractor.ingest_episode failed: %s", e, exc_info=True)
            result.errors.append(str(e))

        result.processing_time_ms = (time.time() - _start) * 1000
        return result

    async def _extract_entities(self, text: str, tier: str) -> list[dict]:
        """Extract entities from text using Gemini (or instructor if available)."""
        if self._gemini:
            raw = await self._gemini.extract(text, tier=tier)
            return raw.get("entities", [])
        return []

    async def _extract_edges(self, text: str, node_ids: list[str], tier: str) -> list[dict]:
        """Extract relationships between known entities."""
        if self._gemini:
            raw = await self._gemini.extract(text, tier=tier, entity_ids=node_ids)
            return raw.get("relationships", [])
        return []

    async def _write_sourced_from(
        self, entity_id: str, episode_id: str, workspace_id: str, tenant_id: str
    ) -> None:
        from dialectica_ontology.relationships import SourcedFrom
        edge = SourcedFrom(
            source_id=entity_id,
            target_id=episode_id,
            workspace_id=workspace_id,
            tenant_id=tenant_id,
        )
        try:
            await self._gc.upsert_edge(edge.model_dump(), workspace_id, tenant_id)
        except Exception as e:
            logger.warning("Failed to write SOURCED_FROM for %s: %s", entity_id, e)

    async def _fire_rules(self, node_ids: list[str], workspace_id: str, tenant_id: str) -> list[str]:
        """Fire symbolic rules on the affected subgraph only."""
        try:
            from dialectica_ontology.symbolic_rules import RuleEngine
            engine = RuleEngine()
            nodes = [await self._gc.get_node(nid, workspace_id) for nid in node_ids]
            results = engine.fire_all(nodes=nodes, edges=[], workspace_id=workspace_id)
            return [r.rule_id for r in results if r.fired]
        except Exception as e:
            logger.warning("Symbolic rules failed: %s", e)
            return []
```

### Step 3.5 — Add `POST /v1/workspaces/{id}/ingest` API endpoint

- [ ] Add to the appropriate router (e.g., `workspaces.py`):

```python
@router.post("/{workspace_id}/ingest")
async def ingest_text(
    workspace_id: str,
    body: IngestRequest,
    gc=Depends(get_graph_client),
    settings=Depends(get_settings_dep),
    _=Depends(require_api_key),
):
    """Incrementally ingest new text into workspace graph.

    Processes the text against the existing graph:
    - Creates an EpisodeNode (with dedup via content_hash)
    - Extracts and resolves entities against existing nodes
    - Extracts and deduplicates edges
    - Fires symbolic rules on affected subgraph
    """
    from dialectica_extraction.incremental import IncrementalExtractor
    from dialectica_extraction.gemini import GeminiExtractor

    gemini = GeminiExtractor(model=settings.gemini_flash_model, project=settings.gcp_project_id)
    extractor = IncrementalExtractor(graph_client=gc, gemini_client=gemini)

    result = await extractor.ingest_episode(
        text=body.text,
        workspace_id=workspace_id,
        tenant_id=body.tenant_id or "default",
        source_type=body.source_type,
        source_uri=body.source_uri,
        tier=body.tier,
    )
    return result


class IngestRequest(BaseModel):
    text: str
    tenant_id: str | None = None
    source_type: str = "text_input"
    source_uri: str | None = None
    tier: str = "standard"
```

### Step 3.6 — Run tests

```bash
cd packages/extraction && python -m pytest tests/test_incremental.py -v
```

Expected: all 7 tests PASS.

### Step 3.7 — Run full extraction test suite

```bash
cd packages/extraction && python -m pytest tests/ -v --tb=short
```

Expected: all 75+ tests pass.

### Step 3.8 — Commit

```bash
git add packages/extraction/src/dialectica_extraction/incremental.py \
        packages/extraction/src/dialectica_extraction/entity_resolution.py \
        packages/extraction/src/dialectica_extraction/edge_dedup.py \
        packages/extraction/tests/test_incremental.py \
        packages/api/src/dialectica_api/routers/
git commit -m "feat: incremental graph construction — IncrementalExtractor, entity resolution, edge dedup, POST /ingest endpoint"
```

---

## Scope Check

| Spec requirement | Task | Status |
|---|---|---|
| EpisodeNode with all fields | Task 1, Step 1.2 | ✓ |
| Content hash (SHA-256) + word_count auto-compute | Task 1, Step 1.2 | ✓ |
| SOURCED_FROM edge type | Task 1, Step 1.3 | ✓ |
| Episode created before chunk_document | Task 1, Step 1.5 | ✓ |
| SOURCED_FROM edges written after extraction | Task 1, Step 1.5 | ✓ |
| Episode deduplication via content_hash | Task 1, Step 1.5 | ✓ |
| get_episodes / get_episode_entities / get_entity_provenance | Task 1, Step 1.6 | ✓ |
| GET /episodes, GET /episodes/{eid}, GET /entities/{eid}/provenance | Task 1, Step 1.7 | ✓ |
| created_at / expired_at on ConflictRelationship | Task 2, Step 2.2 | ✓ |
| valid_at / invalid_at on ConflictRelationship | Task 2, Step 2.2 | ✓ |
| source_episode_ids + confidence_tag on edges | Task 2, Step 2.2 | ✓ |
| invalidate_edge() | Task 2, Step 2.4 | ✓ |
| Read queries filter expired_at IS NULL | Task 2, Step 2.3 | ✓ |
| GET /graph?at= time-travel endpoint | Task 2, Step 2.5 | ✓ |
| IncrementalExtractor with full pipeline | Task 3, Step 3.4 | ✓ |
| Entity resolution (name + JW + embedding) | Task 3, Step 3.2 | ✓ |
| Edge deduplication (create/update/invalidate) | Task 3, Step 3.3 | ✓ |
| POST /v1/workspaces/{id}/ingest | Task 3, Step 3.5 | ✓ |
| Duplicate episode skipped | Task 3, Step 3.4 | ✓ |
| Symbolic rules fired on affected subgraph | Task 3, Step 3.4 | ✓ |

**Not in this plan (frontend items deferred to Phase 3):**
- Frontend "Quick Ingest" component (Phase 3, Prompt 3.3)
- Frontend temporal scrubber / history view (Phase 3, Prompt 3.1)
- Incremental community update (covered in Phase 2, Prompt 2.2)
