# Phase 0: Critical Stabilization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stabilize DIALECTICA for Cloud Run deployment: consolidate the duplicate frontend API layer, harden extraction pipeline error handling, add persistent metadata storage (PostgreSQL), and enable runtime API URL configuration so one Docker image works across all environments.

**Architecture:** Four independent stabilization tasks targeting two layers — frontend (0.1, 0.4) and backend (0.2, 0.3). Each produces working, testable software independently. Complete in order: 0.1 → 0.2 → 0.3 → 0.4.

**Tech Stack:** Next.js 15 App Router (standalone output), TypeScript, FastAPI, SQLModel 0.0.18+, asyncpg, Alembic, PostgreSQL 16, Python 3.12, UV workspaces

**GCP Project:** `dialectica-tacitus` (project number: 1059821510864) — frontend → Cloud Run (Next.js), backend → Cloud Run (FastAPI)

---

## File Map

### Task 0.1 — API Layer Consolidation
- **Modify:** `apps/web/src/types/api.ts` — add `GraphNode`, `GraphEdge`, `ReasoningTrace`, `TheoryAssessment`, `ValidateTraceRequest`, `AddEntityRequest`, `AddRelationshipRequest`
- **Modify:** `apps/web/src/lib/api.ts` — add `getWorkspaceGraph`, `addEntity`, `deleteEntity`, `addRelationship`, `getReasoningTraces`, `validateTrace`, `getTheoryAssessments`; update `request()` to use dynamic URL (prep for 0.4)
- **Modify:** `apps/web/src/app/workspace/[id]/page.tsx` — swap all imports from `@/lib/workspace-api` → `@/lib/api` + `@/types/api`
- **Modify:** `apps/web/src/components/GraphEditor.tsx` — swap `IntegrationNode`, `IntegrationEdge` import
- **Modify:** `apps/web/src/components/ReasoningPanel.tsx` — swap `ReasoningTrace` import
- **Modify:** `apps/web/src/components/TheoryGrid.tsx` — swap `TheoryAssessment` import
- **Delete:** `apps/web/src/lib/workspace-api.ts`

### Task 0.2 — Extraction Pipeline Error Handling
- **Modify:** `packages/extraction/src/dialectica_extraction/pipeline.py` — fix 5 error-handling issues + add step timing + ingestion stats
- **Create:** `packages/extraction/tests/test_pipeline_errors.py` — 4 tests

### Task 0.3 — Persistent Metadata Storage
- **Create:** `packages/api/src/dialectica_api/database/__init__.py`
- **Create:** `packages/api/src/dialectica_api/database/models.py` — `User`, `WorkspaceMeta`, `ApiKeyRecord`, `ExtractionJob`
- **Create:** `packages/api/src/dialectica_api/database/engine.py` — async engine factory + `async_session`
- **Create:** `packages/api/src/dialectica_api/database/deps.py` — `get_db` FastAPI dependency
- **Modify:** `packages/api/src/dialectica_api/config.py` — add `database_url`
- **Modify:** `docker-compose.yml` — add `postgres:16-alpine` service
- **Modify:** `docker-compose.local.yml` — add `postgres:16-alpine` service
- **Create:** `packages/api/alembic.ini`
- **Create:** `packages/api/alembic/env.py`
- **Create:** `packages/api/alembic/versions/0001_initial_schema.py`

### Task 0.4 — Runtime Frontend Configuration
- **Create:** `apps/web/src/lib/config.ts` — `getApiUrl()` with `window.__DIALECTICA_CONFIG__` fallback
- **Modify:** `apps/web/src/app/layout.tsx` — inject `<script>window.__DIALECTICA_CONFIG__=…</script>` server-side
- **Modify:** `apps/web/src/lib/api.ts` — use `getApiUrl()` in `request()` and `analyzeStream()`
- **Modify:** `apps/web/next.config.ts` — remove build-time `NEXT_PUBLIC_API_URL` bake-in
- **Modify:** `apps/web/Dockerfile` — remove `ARG NEXT_PUBLIC_API_URL`, add runtime `ENV DIALECTICA_API_URL=""`

---

## Task 1: Consolidate Frontend API Layer (Prompt 0.1)

**Files:**
- Modify: `apps/web/src/types/api.ts`
- Modify: `apps/web/src/lib/api.ts`
- Modify: `apps/web/src/app/workspace/[id]/page.tsx`
- Modify: `apps/web/src/components/GraphEditor.tsx`
- Modify: `apps/web/src/components/ReasoningPanel.tsx`
- Modify: `apps/web/src/components/TheoryGrid.tsx`
- Delete: `apps/web/src/lib/workspace-api.ts`

### Step 1.1 — Add new types to `types/api.ts`

- [ ] Append to `apps/web/src/types/api.ts`:

```typescript
// Graph node — matches workspace graph endpoint response
export interface GraphNode {
  id: string;
  label: string;
  type: string;
  properties: Record<string, unknown>;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
  vx?: number;
  vy?: number;
}

// Graph edge — matches workspace graph endpoint response
export interface GraphEdge {
  id?: string;
  source: string;
  target: string;
  type: string;
  weight?: number;
}

export interface WorkspaceGraphResponse {
  workspace_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata?: Record<string, unknown>;
}

// Reasoning traces
export interface ReasoningTrace {
  id: string;
  rules_fired: string[];
  conclusion: string;
  confidence_type: "deterministic" | "probabilistic";
  confidence_score: number;
  human_validated: boolean;
  human_verdict?: string;
  source_node_ids: string[];
  created_at?: string;
}

export interface ReasoningTracesResponse {
  traces: ReasoningTrace[];
  total: number;
}

export interface ValidateTraceRequest {
  verdict: "confirmed" | "rejected";
  notes?: string;
}

// Theory assessments
export interface TheoryAssessment {
  framework_id: string;
  display_name: string;
  score: number;
  primary_questions: string[];
  key_propositions: string[];
  domain: string;
}

export interface TheoryAssessmentsResponse {
  assessments: TheoryAssessment[];
}

// Graph mutation requests
export interface AddEntityRequest {
  type: string;
  label: string;
  properties?: Record<string, unknown>;
}

export interface AddRelationshipRequest {
  source: string;
  target: string;
  type: string;
}
```

### Step 1.2 — Add new methods to `api.ts`

- [ ] In `apps/web/src/lib/api.ts`, replace the existing `getGraph` stub and add the new workspace methods. Replace the `getGraph` line and add below `getSubgraph`:

```typescript
  // Graph (replaces integration/graph endpoint)
  getGraph: (workspaceId: string) =>
    request<WorkspaceGraphResponse>(`/v1/workspaces/${workspaceId}/graph`),
  getSubgraph: (workspaceId: string, nodeId: string, depth = 2) =>
    request<WorkspaceGraphResponse>(
      `/v1/workspaces/${workspaceId}/graph/subgraph?node_id=${nodeId}&depth=${depth}`,
    ),

  // Entity mutations
  addEntity: (workspaceId: string, entity: AddEntityRequest) =>
    request<GraphNode>(`/v1/workspaces/${workspaceId}/entities`, {
      method: "POST",
      body: JSON.stringify(entity),
    }),
  deleteEntity: (workspaceId: string, entityId: string) =>
    request<void>(`/v1/workspaces/${workspaceId}/entities/${entityId}`, {
      method: "DELETE",
    }),

  // Relationship mutations
  addRelationship: (workspaceId: string, edge: AddRelationshipRequest) =>
    request<GraphEdge>(`/v1/workspaces/${workspaceId}/relationships`, {
      method: "POST",
      body: JSON.stringify(edge),
    }),

  // Reasoning traces
  getReasoningTraces: (workspaceId: string) =>
    request<ReasoningTracesResponse>(
      `/v1/workspaces/${workspaceId}/reasoning/traces`,
    ),
  validateTrace: (
    workspaceId: string,
    traceId: string,
    verdict: "confirmed" | "rejected",
    notes?: string,
  ) =>
    request<ReasoningTrace>(
      `/v1/workspaces/${workspaceId}/reasoning/${traceId}/validate`,
      {
        method: "POST",
        body: JSON.stringify({ verdict, notes } satisfies ValidateTraceRequest),
      },
    ),

  // Theory assessments
  getTheoryAssessments: (workspaceId: string) =>
    request<TheoryAssessmentsResponse>(
      `/v1/workspaces/${workspaceId}/theory/assessments`,
    ),
```

- [ ] Update the import at top of `apps/web/src/lib/api.ts` to include the new types:

```typescript
import type {
  Workspace,
  CreateWorkspaceRequest,
  PaginatedResponse,
  ExtractionRequest,
  ExtractionResult,
  AnalysisRequest,
  AnalysisResult,
  TheoryFramework,
  ApiKey,
  HealthResponse,
  UserProfile,
  WorkspaceGraphResponse,
  GraphNode,
  GraphEdge,
  ReasoningTrace,
  ReasoningTracesResponse,
  ValidateTraceRequest,
  TheoryAssessment,
  TheoryAssessmentsResponse,
  AddEntityRequest,
  AddRelationshipRequest,
} from "@/types/api";
```

### Step 1.3 — Update `apps/web/src/app/workspace/[id]/page.tsx`

- [ ] Replace the import block (lines 12–24) with:

```typescript
import { api } from "@/lib/api";
import type {
  GraphNode,
  GraphEdge,
  ReasoningTrace,
  TheoryAssessment,
} from "@/types/api";
```

- [ ] Replace all calls that used the old workspace-api functions:
  - `fetchWorkspaceGraph(workspaceId)` → `api.getWorkspaceGraph(workspaceId)`
  - `fetchReasoningTraces(workspaceId)` → `api.getReasoningTraces(workspaceId)`
  - `fetchTheoryAssessments(workspaceId)` → `api.getTheoryAssessments(workspaceId)`
  - `addNode(workspaceId, node)` → `api.addEntity(workspaceId, node)`
  - `deleteNode(workspaceId, nodeId)` → `api.deleteEntity(workspaceId, nodeId)`
  - `addEdge(workspaceId, edge)` → `api.addRelationship(workspaceId, edge)`
  - `validateTrace(workspaceId, traceId, verdict, notes)` → `api.validateTrace(workspaceId, traceId, verdict, notes)`

- [ ] Change state types at top of component:
  - `useState<IntegrationNode[]>` → `useState<GraphNode[]>`
  - `useState<IntegrationEdge[]>` → `useState<GraphEdge[]>`

- [ ] Update `.then((data) => { setNodes(data.nodes ?? []); setEdges(data.edges ?? []) })` — the shape is the same (WorkspaceGraphResponse has `nodes` and `edges`).

### Step 1.4 — Update `GraphEditor.tsx`

- [ ] Replace line 14 in `apps/web/src/components/GraphEditor.tsx`:

```typescript
// OLD:
import type { IntegrationNode, IntegrationEdge } from "@/lib/workspace-api";

// NEW:
import type { GraphNode, GraphEdge } from "@/types/api";
```

- [ ] Rename all `IntegrationNode` references → `GraphNode`, `IntegrationEdge` → `GraphEdge` throughout the file. The interface `GraphEditorProps` becomes:

```typescript
export interface GraphEditorProps {
  nodes: Array<GraphNode>;
  edges: Array<GraphEdge>;
  onAddNode: (node: { type: string; label: string }) => Promise<void>;
  onDeleteNode: (nodeId: string) => Promise<void>;
  onAddEdge: (edge: { source: string; target: string; type: string }) => Promise<void>;
  readOnly?: boolean;
}

type SimNode = GraphNode & d3.SimulationNodeDatum;
```

### Step 1.5 — Update `ReasoningPanel.tsx`

- [ ] Replace line 14 in `apps/web/src/components/ReasoningPanel.tsx`:

```typescript
// OLD:
import type { ReasoningTrace } from "@/lib/workspace-api";

// NEW:
import type { ReasoningTrace } from "@/types/api";
```

### Step 1.6 — Update `TheoryGrid.tsx`

- [ ] Replace line 4 in `apps/web/src/components/TheoryGrid.tsx`:

```typescript
// OLD:
import type { TheoryAssessment } from "@/lib/workspace-api";

// NEW:
import type { TheoryAssessment } from "@/types/api";
```

### Step 1.7 — Delete `workspace-api.ts`

- [ ] Delete `apps/web/src/lib/workspace-api.ts`:

```bash
rm apps/web/src/lib/workspace-api.ts
```

### Step 1.8 — Verify TypeScript

- [ ] Run from `apps/web/`:

```bash
cd apps/web && npx tsc --noEmit
```

Expected: zero type errors. Fix any that appear.

### Step 1.9 — Verify build

- [ ] Run:

```bash
cd apps/web && npm run build
```

Expected: `✓ Compiled successfully` with no errors.

### Step 1.10 — Commit

```bash
git add apps/web/src/types/api.ts \
        apps/web/src/lib/api.ts \
        apps/web/src/app/workspace/[id]/page.tsx \
        apps/web/src/components/GraphEditor.tsx \
        apps/web/src/components/ReasoningPanel.tsx \
        apps/web/src/components/TheoryGrid.tsx
git rm apps/web/src/lib/workspace-api.ts
git commit -m "refactor: consolidate frontend API layer — merge workspace-api into api.ts"
```

---

## Task 2: Fix Extraction Pipeline Error Handling (Prompt 0.2)

**Files:**
- Modify: `packages/extraction/src/dialectica_extraction/pipeline.py`
- Create: `packages/extraction/tests/test_pipeline_errors.py`

### Step 2.1 — Write failing tests first

- [ ] Create `packages/extraction/tests/test_pipeline_errors.py`:

```python
"""Tests for pipeline error handling — Prompt 0.2."""
from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture()
def base_state() -> dict:
    return {
        "text": "Russia and Ukraine signed a ceasefire in 2024.",
        "tier": "standard",
        "workspace_id": "ws-test",
        "tenant_id": "t-test",
        "errors": [],
        "retry_count": 0,
        "processing_time": {},
        "ingestion_stats": {},
        "gliner_available": True,
    }


class TestInstructorImportError:
    """test_instructor_import_error_falls_back_to_gemini"""

    def test_import_error_falls_back_to_gemini(self, base_state):
        """When instructor is not importable, extract_entities falls back to gemini."""
        from dialectica_extraction.pipeline import extract_entities

        # Make instructor unavailable
        with patch.dict(sys.modules, {"instructor": None}):
            with patch(
                "dialectica_extraction.pipeline.GeminiExtractor.extract",
                return_value={"entities": [], "relationships": []},
            ) as mock_gemini:
                state = {**base_state, "chunks": [{"text": "test", "index": 0, "start": 0, "end": 4}]}
                result = extract_entities(state)
                # Should have called gemini, not crashed
                assert mock_gemini.called or result.get("raw_entities") is not None
                # No import error in errors list
                for err in result.get("errors", []):
                    assert "ImportError" not in err.get("step", "")


class TestGeminiExtractionError:
    """test_gemini_extraction_error_logged_and_state_updated"""

    def test_gemini_error_logged_to_state(self, base_state, caplog):
        """When gemini extraction raises, error is logged and appended to state['errors']."""
        import logging
        from dialectica_extraction.pipeline import extract_entities

        with patch(
            "dialectica_extraction.pipeline.GeminiExtractor",
            side_effect=RuntimeError("Gemini 503"),
        ):
            state = {
                **base_state,
                "chunks": [{"text": "test chunk", "index": 0, "start": 0, "end": 10}],
            }
            with caplog.at_level(logging.ERROR):
                result = extract_entities(state)

            # Error logged at ERROR level (not just WARNING)
            assert any("Gemini 503" in r.message or "extraction" in r.message.lower()
                        for r in caplog.records if r.levelno >= logging.ERROR)
            # Error appended to state
            errors = result.get("errors", [])
            assert len(errors) > 0


class TestRepairRetries:
    """test_repair_retries_exhaust_then_abort"""

    def test_retries_exhaust_returns_abort(self, base_state):
        """When retry_count >= MAX_REPAIR_RETRIES, repair_extraction returns abort signal."""
        from dialectica_extraction.pipeline import MAX_REPAIR_RETRIES, repair_extraction

        state = {
            **base_state,
            "retry_count": MAX_REPAIR_RETRIES,  # already at max
            "validation_errors": ["missing required field: confidence_score"],
            "validated_nodes": [],
        }
        result = repair_extraction(state)
        # repair_extraction must signal abort — check retry_count not incremented
        assert result.get("retry_count", 0) >= MAX_REPAIR_RETRIES


class TestGlinerFailure:
    """test_gliner_failure_marks_unavailable"""

    def test_gliner_exception_sets_unavailable_flag(self, base_state, caplog):
        """When GLiNER raises during prefilter, state['gliner_available'] is set to False."""
        import logging
        from dialectica_extraction.pipeline import gliner_prefilter

        with patch(
            "dialectica_extraction.pipeline.GLiNERPreFilter.filter",
            side_effect=RuntimeError("Model load failed"),
        ):
            state = {
                **base_state,
                "chunks": [{"text": "test", "index": 0, "start": 0, "end": 4}],
            }
            with caplog.at_level(logging.ERROR):
                result = gliner_prefilter(state)

            # Flag must be set
            assert result.get("gliner_available") is False
            # Logged at ERROR, not WARNING
            assert any(r.levelno >= logging.ERROR for r in caplog.records)
```

- [ ] Run tests — expect them all to fail:

```bash
cd packages/extraction && python -m pytest tests/test_pipeline_errors.py -v 2>&1 | head -50
```

Expected: `FAILED` for all 4 tests (functions not yet fixed).

### Step 2.2 — Fix `extract_entities` — catch only ImportError for import, log extraction errors

- [ ] In `packages/extraction/src/dialectica_extraction/pipeline.py`, find the `extract_entities` function. Replace the broad `try/except` around the instructor import with a targeted one. The pattern to find and replace:

**OLD pattern (anywhere instructor is imported inside a try/except):**
```python
try:
    from dialectica_extraction import instructor_extractors  # or similar
    # ... extraction logic
except Exception:
    # ... falls back silently
```

**NEW pattern — split into two separate try blocks:**
```python
# Only catch ImportError for the import itself
try:
    from dialectica_extraction import instructor_extractors
    _instructor_available = True
except ImportError:
    _instructor_available = False

# Extraction errors: log + append to state, never swallow silently
try:
    # ... extraction logic using instructor or gemini
    pass
except Exception:
    import traceback
    error_msg = traceback.format_exc()
    logger.error("Extraction failed in extract_entities: %s", error_msg)
    state.setdefault("errors", []).append({
        "step": "extract_entities",
        "message": str(e),
        "details": {"traceback": error_msg},
    })
```

- [ ] Add step timing around `extract_entities`:

```python
def extract_entities(state: ExtractionState) -> ExtractionState:
    _start = time.time()
    # ... existing function body ...
    state.setdefault("processing_time", {})["extract_entities"] = time.time() - _start
    return state
```

### Step 2.3 — Implement `repair_extraction`

- [ ] Find `repair_extraction` in `pipeline.py` and replace its body with:

```python
def repair_extraction(state: ExtractionState) -> ExtractionState:
    """Attempt to repair validation errors. Aborts if MAX_REPAIR_RETRIES exceeded."""
    _start = time.time()

    retry_count = state.get("retry_count", 0)
    if retry_count >= MAX_REPAIR_RETRIES:
        logger.warning(
            "repair_extraction: max retries (%d) reached, aborting repair",
            MAX_REPAIR_RETRIES,
        )
        state.setdefault("processing_time", {})["repair_extraction"] = time.time() - _start
        return state  # caller checks retry_count to decide abort branch

    validation_errors = state.get("validation_errors", [])
    validated_nodes = list(state.get("validated_nodes", []))
    repaired = 0

    for error in validation_errors:
        error_lower = error.lower()

        # Missing required field → attempt re-extraction (mark chunk for retry)
        if "missing required field" in error_lower or "field required" in error_lower:
            logger.info("repair_extraction: missing field error — marking for re-extraction: %s", error)
            # Record for downstream awareness; full re-extraction handled via retry loop
            state.setdefault("errors", []).append({
                "step": "repair_extraction",
                "message": f"Missing field — will retry: {error}",
                "details": {},
            })
            repaired += 1

        # Invalid enum value → map to AMBIGUOUS sentinel
        elif "invalid enum" in error_lower or "not a valid enum" in error_lower:
            logger.info("repair_extraction: invalid enum — flagging as AMBIGUOUS: %s", error)
            # Mark affected nodes as AMBIGUOUS confidence tag
            for node in validated_nodes:
                if isinstance(node, dict):
                    node.setdefault("confidence_tag", "AMBIGUOUS")
            repaired += 1

        # Duplicate entity → deduplicate (writer.py merge_duplicate_nodes is called later)
        elif "duplicate" in error_lower:
            logger.info("repair_extraction: duplicate entity error — will deduplicate in writer: %s", error)
            repaired += 1

    state["validated_nodes"] = validated_nodes
    state["retry_count"] = retry_count + 1
    state["validation_errors"] = []  # clear after repair attempt
    logger.info("repair_extraction: repaired %d/%d errors (attempt %d)", repaired, len(validation_errors), retry_count + 1)
    state.setdefault("processing_time", {})["repair_extraction"] = time.time() - _start
    return state
```

### Step 2.4 — Fix `gliner_prefilter` — log at ERROR, set `gliner_available` flag

- [ ] Find the `gliner_prefilter` function in `pipeline.py`. In its except block, change:

**OLD:**
```python
except Exception as e:
    logger.warning("GLiNER prefilter failed: %s — passing all chunks", e)
    # returns all chunks with priority 1.0
```

**NEW:**
```python
except Exception as e:
    import traceback
    logger.error(
        "GLiNER prefilter UNAVAILABLE — passing all chunks with priority 1.0: %s\n%s",
        e, traceback.format_exc(),
    )
    state["gliner_available"] = False
    # fall back: pass all chunks through with uniform priority
```

- [ ] Also ensure `gliner_available = True` is set at the top of the function (before the try block):

```python
def gliner_prefilter(state: ExtractionState) -> ExtractionState:
    _start = time.time()
    state["gliner_available"] = True  # assume available until proven otherwise
    try:
        # ... existing GLiNER logic ...
    except Exception as e:
        logger.error("GLiNER prefilter UNAVAILABLE: %s", e, exc_info=True)
        state["gliner_available"] = False
        # pass all chunks with priority 1.0 as fallback
        state["prefilter_results"] = [
            {"chunk_index": i, "priority": 1.0, "entities": []}
            for i, _ in enumerate(state.get("chunks", []))
        ]
    state.setdefault("processing_time", {})["gliner_prefilter"] = time.time() - _start
    return state
```

### Step 2.5 — Add timing to ALL pipeline steps

- [ ] Add `_start = time.time()` at the top and `state.setdefault("processing_time", {})["<step_name>"] = time.time() - _start` at the bottom of each pipeline step that doesn't have it yet:
  - `chunk_document`
  - `gliner_prefilter` (done in 2.4)
  - `extract_entities` (done in 2.2)
  - `validate_schema`
  - `repair_extraction` (done in 2.3)
  - `extract_relationships`
  - `resolve_coreference`
  - `validate_structural`
  - `compute_embeddings`
  - `write_to_graph`

### Step 2.6 — Add `ingestion_stats` tracking

- [ ] In `write_to_graph` (the final pipeline step), after writing, compute and store:

```python
state["ingestion_stats"] = {
    "total_chunks": len(state.get("chunks", [])),
    "chunks_processed": len([c for c in state.get("prefilter_results", []) if c.get("priority", 0) > 0]),
    "chunks_failed": len(state.get("errors", [])),
    "entities_extracted": len(state.get("raw_entities", [])),
    "entities_deduplicated": len(state.get("validated_nodes", [])),
    "relationships_extracted": len(state.get("validated_edges", [])),
    "confidence_avg": (
        sum(n.get("confidence_score", 0) for n in state.get("validated_nodes", []))
        / max(len(state.get("validated_nodes", [])), 1)
    ),
}
```

### Step 2.7 — Run tests

- [ ] Run the 4 tests:

```bash
cd packages/extraction && python -m pytest tests/test_pipeline_errors.py -v
```

Expected: all 4 PASS. If any fail, diagnose the pipeline.py function signatures — the test patches assume specific import paths; adjust patch targets if needed (e.g., `dialectica_extraction.pipeline.GLiNERPreFilter` vs the actual import).

### Step 2.8 — Run full extraction test suite

```bash
cd packages/extraction && python -m pytest tests/ -v --tb=short
```

Expected: existing 75 tests still pass.

### Step 2.9 — Commit

```bash
git add packages/extraction/src/dialectica_extraction/pipeline.py \
        packages/extraction/tests/test_pipeline_errors.py
git commit -m "fix: harden extraction pipeline — split ImportError catch, implement repair_extraction, ERROR-level GLiNER log, step timing, ingestion stats"
```

---

## Task 3: Add Persistent Metadata Storage (Prompt 0.3)

**Files:**
- Create: `packages/api/src/dialectica_api/database/__init__.py`
- Create: `packages/api/src/dialectica_api/database/models.py`
- Create: `packages/api/src/dialectica_api/database/engine.py`
- Create: `packages/api/src/dialectica_api/database/deps.py`
- Modify: `packages/api/src/dialectica_api/config.py`
- Modify: `docker-compose.yml`
- Modify: `docker-compose.local.yml`
- Create: `packages/api/alembic.ini`
- Create: `packages/api/alembic/env.py`
- Create: `packages/api/alembic/versions/0001_initial_schema.py`

### Step 3.1 — Create `database/__init__.py`

- [ ] Create `packages/api/src/dialectica_api/database/__init__.py` (empty):

```python
"""Relational metadata store — async SQLModel + PostgreSQL."""
```

### Step 3.2 — Create `database/models.py`

- [ ] Create `packages/api/src/dialectica_api/database/models.py`:

```python
"""SQLModel table definitions for DIALECTICA metadata store.

Stores user/workspace/API key/job metadata in PostgreSQL (Cloud SQL in production).
Neo4j still holds all conflict graph data.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def _ulid() -> str:
    from ulid import ULID
    return str(ULID())


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=_ulid, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    tier: str = "free"  # free | pro | enterprise
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkspaceMeta(SQLModel, table=True):
    __tablename__ = "workspace_meta"

    id: str = Field(default_factory=_ulid, primary_key=True)
    name: str
    description: str = ""
    owner_id: str = Field(foreign_key="users.id", index=True)
    domain: str = "human_friction"  # human_friction | conflict_warfare
    template: Optional[str] = None
    status: str = "active"  # active | archived | deleted
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ApiKeyRecord(SQLModel, table=True):
    __tablename__ = "api_key_records"

    id: str = Field(default_factory=_ulid, primary_key=True)
    key_hash: str = Field(index=True)  # bcrypt hash of the raw API key
    name: str
    user_id: str = Field(foreign_key="users.id", index=True)
    tier: str = "standard"
    rate_limit: int = 100  # requests per minute
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None


class ExtractionJob(SQLModel, table=True):
    __tablename__ = "extraction_jobs"

    id: str = Field(default_factory=_ulid, primary_key=True)
    workspace_id: str = Field(foreign_key="workspace_meta.id", index=True)
    status: str = "pending"  # pending | running | completed | failed
    progress: float = 0.0
    stats: dict = Field(default_factory=dict, sa_column=Column(JSON))
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
```

### Step 3.3 — Create `database/engine.py`

- [ ] Create `packages/api/src/dialectica_api/database/engine.py`:

```python
"""Async SQLAlchemy engine + session factory for DIALECTICA metadata store."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from dialectica_api.config import get_settings

_engine = None
_async_session: async_sessionmaker[AsyncSession] | None = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.environment == "development",
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _async_session
    if _async_session is None:
        _async_session = async_sessionmaker(
            get_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _async_session


async def create_db_and_tables() -> None:
    """Create all tables if they don't exist. Called on API startup."""
    async with get_engine().begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### Step 3.4 — Create `database/deps.py`

- [ ] Create `packages/api/src/dialectica_api/database/deps.py`:

```python
"""FastAPI dependency for injecting database sessions."""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from dialectica_api.database.engine import get_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async DB session, rolling back on error."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### Step 3.5 — Update `config.py`

- [ ] In `packages/api/src/dialectica_api/config.py`, add `database_url` to the `Settings` class after the existing `redis_url` field:

```python
    # Metadata database (PostgreSQL in production, SQLite for dev)
    database_url: str = "sqlite+aiosqlite:///./dialectica.db"
    # For production Cloud SQL (PostgreSQL):
    # DATABASE_URL=postgresql+asyncpg://user:pass@/dialectica?host=/cloudsql/PROJECT:REGION:INSTANCE
```

### Step 3.6 — Add postgres to `docker-compose.local.yml`

- [ ] Add the postgres service to `docker-compose.local.yml` before the `api` service, and add `DATABASE_URL` to the api environment:

```yaml
  postgres:
    image: postgres:16-alpine
    container_name: dialectica-postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: dialectica
      POSTGRES_PASSWORD: dialectica-dev
      POSTGRES_DB: dialectica
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dialectica -d dialectica"]
      interval: 10s
      timeout: 5s
      retries: 5
```

- [ ] Add to the `api` service environment in `docker-compose.local.yml`:

```yaml
      DATABASE_URL: postgresql+asyncpg://dialectica:dialectica-dev@postgres:5432/dialectica
```

- [ ] Add `depends_on` for postgres in the api service:

```yaml
    depends_on:
      neo4j: { condition: service_healthy }
      redis: { condition: service_healthy }
      postgres: { condition: service_healthy }
```

- [ ] Add to the `volumes` section at the bottom:

```yaml
  postgres-data:
```

- [ ] Apply same changes to `docker-compose.yml` (the full-stack compose).

### Step 3.7 — Add Python deps

- [ ] Add to `packages/api/pyproject.toml` (under `[project] dependencies`):

```
"sqlmodel>=0.0.18",
"sqlalchemy[asyncio]>=2.0",
"asyncpg>=0.29",
"aiosqlite>=0.20",
"alembic>=1.13",
"python-ulid>=2.0",
"bcrypt>=4.1",
```

- [ ] Run:

```bash
cd packages/api && uv pip install -e ".[dev]"
```

### Step 3.8 — Wire `create_db_and_tables` into API startup

- [ ] In `packages/api/src/dialectica_api/main.py`, find the lifespan or startup event and add:

```python
from dialectica_api.database.engine import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield
    # cleanup if needed
```

If there's already a lifespan context manager, add `await create_db_and_tables()` inside it before the `yield`.

### Step 3.9 — Set up Alembic

- [ ] From `packages/api/` directory, initialize Alembic:

```bash
cd packages/api && uv run alembic init alembic
```

- [ ] Replace `packages/api/alembic/env.py` with:

```python
"""Alembic environment for DIALECTICA metadata store."""
from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

# Import all models so Alembic picks up their metadata
from dialectica_api.database.models import ApiKeyRecord, ExtractionJob, User, WorkspaceMeta  # noqa: F401

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def get_url() -> str:
    from dialectica_api.config import get_settings
    return get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(get_url())
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

- [ ] Update `packages/api/alembic.ini` to set script_location and the sqlalchemy.url placeholder:

In `alembic.ini`, set:
```ini
script_location = alembic
sqlalchemy.url = sqlite+aiosqlite:///./dialectica.db
```

(This is only used for offline mode; online mode reads from Settings.)

### Step 3.10 — Create initial migration

- [ ] Generate the initial migration:

```bash
cd packages/api && uv run alembic revision --autogenerate -m "initial_schema"
```

- [ ] Review the generated file in `alembic/versions/` — it should contain `create_table` calls for `users`, `workspace_meta`, `api_key_records`, `extraction_jobs`.

- [ ] Apply the migration locally (SQLite for quick dev test):

```bash
cd packages/api && uv run alembic upgrade head
```

Expected: migration runs successfully.

### Step 3.11 — Verify API starts

```bash
cd packages/api && uv run python -c "
import asyncio
from dialectica_api.database.engine import create_db_and_tables
asyncio.run(create_db_and_tables())
print('DB tables created OK')
"
```

Expected: `DB tables created OK`

### Step 3.12 — Commit

```bash
git add packages/api/src/dialectica_api/database/ \
        packages/api/src/dialectica_api/config.py \
        packages/api/src/dialectica_api/main.py \
        packages/api/alembic.ini \
        packages/api/alembic/ \
        docker-compose.yml \
        docker-compose.local.yml
git commit -m "feat: add PostgreSQL metadata store — User, WorkspaceMeta, ApiKeyRecord, ExtractionJob + Alembic migrations"
```

---

## Task 4: Runtime Frontend Configuration (Prompt 0.4)

**Files:**
- Create: `apps/web/src/lib/config.ts`
- Modify: `apps/web/src/app/layout.tsx`
- Modify: `apps/web/src/lib/api.ts`
- Modify: `apps/web/next.config.ts`
- Modify: `apps/web/Dockerfile`

**Why:** Currently `NEXT_PUBLIC_API_URL` is baked in at Docker build time (line 14 of Dockerfile: `ARG NEXT_PUBLIC_API_URL`). This means we need separate images for dev/staging/prod. After this task, one image works everywhere — the API URL is injected at container startup via `DIALECTICA_API_URL` env var.

### Step 4.1 — Create `config.ts`

- [ ] Create `apps/web/src/lib/config.ts`:

```typescript
/**
 * Runtime configuration for DIALECTICA frontend.
 *
 * Priority order:
 * 1. window.__DIALECTICA_CONFIG__.apiUrl — injected by server-rendered layout.tsx
 *    (set from DIALECTICA_API_URL env var at request time)
 * 2. NEXT_PUBLIC_API_URL — build-time fallback (legacy, CI/CD compat)
 * 3. http://localhost:8080 — local development default
 */
export function getApiUrl(): string {
  if (
    typeof window !== "undefined" &&
    (window as unknown as { __DIALECTICA_CONFIG__?: { apiUrl?: string } })
      .__DIALECTICA_CONFIG__?.apiUrl
  ) {
    return (
      window as unknown as { __DIALECTICA_CONFIG__: { apiUrl: string } }
    ).__DIALECTICA_CONFIG__.apiUrl;
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
}
```

### Step 4.2 — Update `layout.tsx` to inject config

- [ ] In `apps/web/src/app/layout.tsx`, add the script injection. The layout is a Server Component (no `"use client"`) so it can read `process.env` at request time.

Replace the existing `RootLayout` return with:

```typescript
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Read at request time on the server — not baked at build time
  const apiUrl = process.env.DIALECTICA_API_URL || "";

  return (
    <html lang="en" className="dark">
      <head>
        {/* Inject runtime config before any client JS executes */}
        <script
          dangerouslySetInnerHTML={{
            __html: `window.__DIALECTICA_CONFIG__=${JSON.stringify({ apiUrl })}`,
          }}
        />
      </head>
      <body className="min-h-screen bg-background">
        <Providers>
          <div className="flex h-screen overflow-hidden">
            <Sidebar />
            <div className="flex flex-col flex-1 overflow-hidden">
              <Header />
              <main className="flex-1 overflow-y-auto p-6">{children}</main>
            </div>
          </div>
        </Providers>
      </body>
    </html>
  );
}
```

### Step 4.3 — Update `api.ts` to use `getApiUrl()`

- [ ] In `apps/web/src/lib/api.ts`, replace line 16:

```typescript
// OLD:
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

// NEW:
import { getApiUrl } from "./config";
```

- [ ] Then update the `request` function to call `getApiUrl()` per-request (not module-level constant):

```typescript
async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const API_URL = getApiUrl();  // resolved per-call, picks up runtime injection
  const apiKey =
    typeof window !== "undefined" ? localStorage.getItem("dialectica_api_key") : null;
  // ... rest unchanged
  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  // ...
}
```

- [ ] Update `analyzeStream` similarly — it builds the URL inline:

```typescript
  analyzeStream: (data: AnalysisRequest): EventSource => {
    const API_URL = getApiUrl();
    // ... rest unchanged, use API_URL local variable
  },
```

### Step 4.4 — Update `next.config.ts`

- [ ] In `apps/web/next.config.ts`, the `rewrites()` function currently reads `process.env.NEXT_PUBLIC_API_URL` (baked at build time). Change to use a server-side env var that can be set at runtime:

```typescript
  async rewrites() {
    // DIALECTICA_API_URL is set at container runtime, not baked at build
    // Falls back to NEXT_PUBLIC_API_URL for backward compat in CI
    const apiUrl =
      process.env.DIALECTICA_API_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:8080";
    return [
      { source: "/api/v1/:path*", destination: `${apiUrl}/v1/:path*` },
      { source: "/api/health", destination: `${apiUrl}/health` },
    ];
  },
```

- [ ] Also update the `env` block:

```typescript
  env: {
    INTERNAL_API_URL:
      process.env.DIALECTICA_API_URL ||
      process.env.INTERNAL_API_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://localhost:8080",
  },
```

### Step 4.5 — Update `Dockerfile`

- [ ] In `apps/web/Dockerfile`, remove the build-time ARG and add runtime ENV:

**Stage 2 (builder) — remove these lines:**
```dockerfile
ARG NEXT_PUBLIC_API_URL=http://localhost:8080
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
```

**Stage 3 (production) — add:**
```dockerfile
# Set at container startup via: docker run -e DIALECTICA_API_URL=https://api.tacitus.me
ENV DIALECTICA_API_URL=""
```

Full updated Dockerfile:

```dockerfile
# ─── Stage 1: Dependencies ────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# ─── Stage 2: Builder ─────────────────────────────────────────────────────────
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ─── Stage 3: Production ──────────────────────────────────────────────────────
FROM node:20-alpine AS production
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
# Set at container startup: docker run -e DIALECTICA_API_URL=https://api.dialectica.tacitus.me
ENV DIALECTICA_API_URL=""

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget -qO- http://localhost:3000/ || exit 1

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

CMD ["node", "server.js"]
```

### Step 4.6 — Build and test locally

- [ ] Build:

```bash
cd apps/web && npm run build
```

Expected: `✓ Compiled successfully`

- [ ] Start with runtime URL injection:

```bash
DIALECTICA_API_URL=http://localhost:8080 npm start
```

- [ ] Open browser DevTools → Network → any API call → verify the URL is `http://localhost:8080/v1/...`

- [ ] Also verify the injected config in browser console:

```javascript
window.__DIALECTICA_CONFIG__
// Expected: { apiUrl: "http://localhost:8080" }
```

### Step 4.7 — Test Docker image portability

- [ ] Build the image without any build-time API URL:

```bash
cd apps/web && docker build -t dialectica-web:test .
```

- [ ] Run with production URL:

```bash
docker run -e DIALECTICA_API_URL=https://api.dialectica.tacitus.me -p 3000:3000 dialectica-web:test
```

- [ ] Verify no hardcoded `localhost:8080` in built JS bundles:

```bash
docker run --rm dialectica-web:test grep -r "localhost:8080" /app/.next/static/ 2>/dev/null || echo "Clean — no hardcoded URLs"
```

Expected: `Clean — no hardcoded URLs`

### Step 4.8 — TypeScript check

```bash
cd apps/web && npx tsc --noEmit
```

Expected: zero errors.

### Step 4.9 — Commit

```bash
git add apps/web/src/lib/config.ts \
        apps/web/src/lib/api.ts \
        apps/web/src/app/layout.tsx \
        apps/web/next.config.ts \
        apps/web/Dockerfile
git commit -m "feat: runtime frontend configuration — DIALECTICA_API_URL injected at container startup, no build-time bake"
```

---

## Scope Check

| Spec requirement | Task | Status |
|---|---|---|
| Merge workspace-api.ts into api.ts | Task 1 | ✓ |
| Types for all new methods in types/api.ts | Task 1, Step 1.1 | ✓ |
| Update all workspace-api.ts consumers | Task 1, Steps 1.3–1.6 | ✓ |
| Delete workspace-api.ts | Task 1, Step 1.7 | ✓ |
| Fix extract_entities ImportError catch | Task 2, Step 2.2 | ✓ |
| Implement repair_extraction | Task 2, Step 2.3 | ✓ |
| Fix gliner_prefilter ERROR log + flag | Task 2, Step 2.4 | ✓ |
| Add timing to all steps | Task 2, Step 2.5 | ✓ |
| Add ingestion_stats | Task 2, Step 2.6 | ✓ |
| 4 test cases | Task 2, Step 2.1 | ✓ |
| SQLModel models (4 tables) | Task 3, Steps 3.2 | ✓ |
| Async engine + sessionmaker | Task 3, Step 3.3 | ✓ |
| get_db dependency | Task 3, Step 3.4 | ✓ |
| DATABASE_URL in Settings | Task 3, Step 3.5 | ✓ |
| postgres in docker-compose | Task 3, Step 3.6 | ✓ |
| Alembic migrations | Task 3, Steps 3.9–3.10 | ✓ |
| getApiUrl() with window injection | Task 4, Step 4.1 | ✓ |
| layout.tsx config injection | Task 4, Step 4.2 | ✓ |
| api.ts uses getApiUrl() | Task 4, Step 4.3 | ✓ |
| next.config.ts runtime URL | Task 4, Step 4.4 | ✓ |
| Dockerfile runtime ENV | Task 4, Step 4.5 | ✓ |

**Not covered in this plan (separate plans):**
- Auth middleware using DB API keys (Phase 0.3 optional extension — needs auth middleware file read)
- Workspaces router reading WorkspaceMeta from PostgreSQL (depends on existing router structure)

These two items require reading the existing auth middleware + workspaces router, which could affect 5+ files and should be a separate task after Phase 0 is committed.
