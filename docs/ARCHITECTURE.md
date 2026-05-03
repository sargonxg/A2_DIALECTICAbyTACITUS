# DIALECTICA — Ingestion Architecture (canonical reference)

Last updated: 2026-05-02

This document is the source of truth for **how data gets into DIALECTICA**.
It exists because the codebase grew three parallel ingestion paths over time;
this file declares which one is canonical and what to do about the others.

## Canonical pipeline (use this)

```
┌──────────────┐   ┌──────────────────────┐   ┌────────────────────────────┐
│ Source       │   │ FastAPI router       │   │ Pipeline runner            │
│ (Gutenberg / │──▶│ /v1/.../ingest/...   │──▶│ chunk → GLiNER → Gemini    │
│  upload /    │   │ /v1/.../extract     │   │ → validate → relationships │
│  paste)      │   │                      │   │ → coreference → embeddings │
└──────────────┘   └──────────┬───────────┘   │ → write_to_graph           │
                              │               └────────────┬───────────────┘
                              │                            │
                              ▼                            ▼
                  ┌──────────────────────┐   ┌────────────────────────────┐
                  │ JobStore (in-memory) │   │ Neo4j Aura (multi-tenant)  │
                  │ + JobProgressEvents  │◀──│ workspace_id + tenant_id   │
                  └──────────┬───────────┘   └────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │ SSE stream endpoint  │
                  │ /extractions/{id}/   │
                  │  stream              │
                  └──────────────────────┘
```

### Components

| Component | Path | Notes |
|-----------|------|-------|
| Source loaders | `packages/extraction/src/dialectica_extraction/sources/` | One module per source. `gutenberg.py` is the reference; add `arxiv.py`, `news.py`, etc. here. |
| LangGraph pipeline | `packages/extraction/src/dialectica_extraction/pipeline.py` | 10-step DAG. Don't fork; extend. |
| Inline runner (with progress) | `packages/api/src/dialectica_api/services/pipeline_runner.py` | Used when Pub/Sub is unavailable (local dev, demo machines). Emits `JobProgressEvent`s as it runs each LangGraph step. |
| Pub/Sub worker | `packages/extraction/src/dialectica_extraction/pubsub_worker.py` | Production async path. Subscribes to `dialectica-extraction-requests`. |
| Job + progress store | `packages/api/src/dialectica_api/services/job_store.py` | In-memory; replace with Redis in production (see **Migration to Redis** below). |
| HTTP entrypoints | `packages/api/src/dialectica_api/routers/extraction.py` (text + uploads), `routers/gutenberg.py` (Gutenberg picker), `routers/extraction_stream.py` (SSE), `routers/corpus_library.py` (catalog of ingested docs) | All workspace-scoped (`/v1/workspaces/{id}/...`). |

### Endpoints (canonical)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/v1/gutenberg/catalog` | Curated 8-book catalog (public, no auth — used by demo) |
| `POST` | `/v1/workspaces/{ws}/ingest/gutenberg` | Fetch + ingest a Gutenberg book by ID |
| `POST` | `/v1/workspaces/{ws}/extract` | Inline text extraction |
| `POST` | `/v1/workspaces/{ws}/extract/document` | Document upload (PDF/DOCX/TXT, ≤10MB) |
| `GET` | `/v1/workspaces/{ws}/extractions` | List jobs in workspace |
| `GET` | `/v1/workspaces/{ws}/extractions/{job_id}` | Single job state |
| `GET` | `/v1/workspaces/{ws}/extractions/{job_id}/stream` | **SSE** progress stream |
| `GET` | `/v1/workspaces/{ws}/corpus/documents` | Ingested SourceDocument library |

### Job lifecycle + SSE event shape

Each ingestion produces one job. The SSE stream emits events of the form:

```json
{
  "job_id": "ab12cd34",
  "step": "extract_entities",
  "status": "complete",
  "message": "",
  "counts": { "entities_raw": 47 },
  "timestamp": 1714665600.123
}
```

`status` is one of `started | complete | failed | info | ready`. The
final frame is an `event: job` containing the full terminal job dict
(including `auto_reasoning` if reasoning was available).

Step keys (canonical, in order):

```
fetch_gutenberg
chunk_document
gliner_prefilter
extract_entities
validate_schema
extract_relationships
resolve_coreference
validate_structural
compute_embeddings
check_review_needed
write_to_graph
```

Frontend rendering: `apps/web/src/components/extraction/LiveExtractionProgress.tsx`
mirrors this list — keep them in sync.

### Auto-reasoning hand-off

When the canonical pipeline completes, the runner calls
`pipeline_runner._attach_auto_reasoning` which runs three cheap queries
against the freshly-written graph:

1. `graph_client.get_workspace_stats` → node/edge totals
2. `graph_client.get_escalation_trajectory` → Glasl stage, direction, velocity
3. `graph_client.get_nodes(label="Actor", limit=5)` → top actors

Results are attached to the job under `job["auto_reasoning"]` and shown
inline in the ingest UI. Failures here are logged and swallowed; they do
not flip the job to `failed`.

### Demo reasoning theatre hand-off

The May Prompt 2 demo route, `/demo/{scenarioId}/reasoning`, consumes the graph
created by `/demo` and renders a deterministic reasoning surface over three demo
workspaces:

- `demo-romeo`
- `demo-war-peace`
- `demo-syria`

The curated question metadata lives in `data/seed/reasoning_library.json`. The
frontend fixture currently mirrors the planned structured `ReasoningResult`
contract so the UI can render citations, determinism, hallucination risk,
counterfactual diffs, structural-similarity neighbours, Cypher snippets, and
symbolic rules without hard-coding a prose blob.

Planned API endpoints for the backend pass:

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/v1/workspaces/{ws}/reason/curated` | Run a curated question through GraphRAG, symbolic rules, synthesis, and hallucination detection. |
| `POST` | `/v1/workspaces/{ws}/reason/counterfactual` | Re-run a curated question against a transient mutilated graph; never writes back to Neo4j. |
| `POST` | `/v1/workspaces/{ws}/reason/similarity` | Return nearest comparison workspaces by semantic and topology distance. |

## Deprecated / parallel paths (do not extend)

The following predate this consolidation. Don't add features to them; route
new work through the canonical pipeline instead. Removal is scheduled but
deferred until current demos are stable.

### `dialectica/ingestion/` — TACITUS core v1 CLI

Path: `dialectica/ingestion/{load_documents,chunk_documents,extract_primitives,pipeline}.py`

A separate, deterministic-only ingestion path with its own primitives
(`SourceDocument`, `EvidenceSpan`, `Actor`, `Claim`, `Commitment`,
`Constraint`, `Event`, `Narrative`, `ActorState`, `Episode`,
`ExtractionRun`). Used by the local CLI flow documented in
`docs/INGESTION_PIPELINE.md` § "Local TACITUS core v1 CLI".

**Why it still exists:** offline tests and the trust-graph spike depend on
it. **What we will do:** keep it read-compatible; new features land in
`packages/extraction/`.

### `apps/web/src/lib/graphopsExtraction.ts` — frontend-resident pipeline

Path: `apps/web/src/lib/graphopsExtraction.ts` plus `apps/web/src/app/api/graphops/ingest/route.ts`

A Next.js-side pipeline used by the `GraphOpsConsole`. Hits the API but
also runs its own preprocessing. **Why it still exists:** the GraphOps
demo flow uses it. **What we will do:** consolidate into the canonical
`/v1/workspaces/{ws}/extract` endpoint; the frontend should be a thin
client only.

### Databricks notebooks (`notebooks/databricks/`, `databricks/src/`)

These pre-compute Delta-Lake-backed corpora for offline experimentation
(KGE training, large-scale benchmarks). Not in the live path. They share
the `dialectica_extraction.sources.gutenberg` module so the same
fetch-and-strip logic runs in both places.

## Multi-tenant invariants (do not violate)

- Every node and edge in Neo4j carries `workspace_id` AND `tenant_id`.
- Every Cypher query filters on both. See `packages/graph/.../neo4j_client.py:11`.
- API endpoints derive `tenant_id` from the authenticated principal
  (`Depends(get_current_tenant)`); never trust the request body.
- The job store keys jobs by short ID but stores `workspace_id` and uses
  it on every list/get path.

## Migration to Redis (production)

`JobStore` is intentionally in-process. To move it to Redis:

1. Implement `RedisJobStore` with the same interface
   (`upsert_job`, `get_job`, `list_jobs`, `append_event`, `events_for`,
   `stream_events`).
2. Use Redis Streams for `events_for` / `stream_events` (`XADD` per
   `append_event`, `XREAD` blocking for `stream_events`).
3. Override the `get_job_store` dependency in `dialectica_api.deps`.
4. The Pub/Sub worker (`pubsub_worker.py`) needs a hook to publish
   `JobProgressEvent`s into the same Redis Stream — currently it only
   publishes terminal status to `dialectica-graph-updates`.
5. The SSE endpoint code does not change.

## Adding a new source

1. Create `packages/extraction/src/dialectica_extraction/sources/<name>.py`
   exporting a `fetch_<name>(...)` function and an optional curated
   catalog.
2. Add a router in `packages/api/src/dialectica_api/routers/<name>.py`
   that calls `_new_job` from `routers/extraction.py`, then schedules
   `run_pipeline_with_progress(...)` via `asyncio.create_task`.
3. Register the router in `main.py`.
4. Add a frontend tab to `apps/web/src/app/workspaces/[id]/ingest/page.tsx`
   alongside the Gutenberg / upload tabs.
5. Add tests under `packages/api/tests/test_<name>.py` using the same
   `_restore_auth_env` autouse fixture pattern as `test_gutenberg.py`.
