# DIALECTICA Ingestion Pipeline

Last updated: 2026-05-02

> **Canonical reference:** `docs/ARCHITECTURE.md`. That file declares which
> ingestion path is the source of truth (the LangGraph pipeline behind
> `/v1/workspaces/{ws}/extract` and `/v1/workspaces/{ws}/ingest/gutenberg`)
> and which paths below are deprecated. This file is the longer
> walk-through of all paths that currently exist.

## What Changed (2026-05-02 — backbone wave)

A first-class **public-domain ingestion backbone** on top of the existing
LangGraph pipeline:

- **Project Gutenberg picker** — curated 8-book catalog at
  `GET /v1/gutenberg/catalog` (public, no auth) and one-click ingest at
  `POST /v1/workspaces/{ws}/ingest/gutenberg`. Books span both TACITUS
  domains (Romeo & Juliet, War & Peace, Crime & Punishment, Thucydides,
  The Prince, Meditations, Art of War, Wealth of Nations).
- **Live SSE progress stream** at
  `GET /v1/workspaces/{ws}/extractions/{job_id}/stream` — emits one
  `JobProgressEvent` per LangGraph step (`chunked: 312`, `entities_raw: 47`,
  `nodes_written: 23` …). Used by the new `LiveExtractionProgress`
  component on the ingest page.
- **Auto-reasoning hand-off** — on job completion the pipeline runner
  attaches a small reasoning summary (graph stats, escalation trajectory,
  top actors) onto the job and exposes it via the SSE final frame.
- **Corpus library** at `GET /v1/workspaces/{ws}/corpus/documents` —
  list of `SourceDocument` summaries (title, content hash, word count,
  tier, model, ingested-at, node/edge counts).
- **Shared sources module** — Gutenberg fetch + boilerplate-strip moved
  into `packages/extraction/src/dialectica_extraction/sources/gutenberg.py`
  and shared by the API router, the CLI tool (`tools/download_gutenberg.py`),
  and the Databricks notebooks.
- **Shared `JobStore`** — in-process job + progress event store with an
  `asyncio.Event`-driven SSE listener
  (`packages/api/src/dialectica_api/services/job_store.py`). Designed for
  mechanical replacement by a Redis-backed implementation in production
  (see `docs/ARCHITECTURE.md` §"Migration to Redis").

### Frontend

- `apps/web/src/app/workspaces/[id]/ingest/page.tsx` — tabs for
  Project Gutenberg / Upload / Paste, with live progress and auto-reasoning
  rendered inline.
- `apps/web/src/components/extraction/GutenbergPicker.tsx` — book grid +
  domain filter + tier + max-chars selector + free-form Gutenberg ID field.
- `apps/web/src/components/extraction/LiveExtractionProgress.tsx` —
  consumes the SSE stream and renders the canonical 11-step list with
  per-step counters.
- `apps/web/src/app/workspaces/[id]/corpus/page.tsx` — corpus library page
  listing all ingested SourceDocuments with provenance.

### Sprawl note

We had three parallel ingestion paths before this wave (LangGraph,
`dialectica/ingestion/` CLI, `apps/web/src/lib/graphopsExtraction.ts`).
The LangGraph path is now declared canonical in `docs/ARCHITECTURE.md`;
the others are read-compatible only. Don't extend them.

## Actual Current Pipeline

### Local TACITUS core v1 CLI

Path:

- `dialectica/ingestion/load_documents.py`
- `dialectica/ingestion/chunk_documents.py`
- `dialectica/ingestion/extract_primitives.py`
- `dialectica/ingestion/pipeline.py`

Flow:

1. Load local `.txt` documents.
2. Create `SourceDocument` with SHA-256 and trust metadata.
3. Chunk documents with offsets.
4. Run deterministic fallback extraction.
5. Emit `EvidenceSpan`, `Actor`, `Claim`, `Commitment`, `Constraint`, `Event`,
   `Narrative`, `ActorState`, `Episode`, and `ExtractionRun`.
6. Validate primitive names against `tacitus_core_v1`.
7. Write JSONL or Neo4j through the local graph adapter.

### GraphOps web pipeline

Path:

- `apps/web/src/lib/graphopsExtraction.ts`
- `apps/web/src/app/api/graphops/ingest/route.ts`
- `apps/web/src/lib/dynamicOntology.ts`
- `apps/web/src/lib/graphopsRuns.ts`

Flow:

1. Accept pasted text, sample text, TXT, or PDF.
2. Remove common Project Gutenberg boilerplate.
3. Build dynamic ontology plan.
4. Segment into explicit headings or episode windows.
5. Extract primitives with source spans and confidence.
6. Evaluate neurosymbolic rules.
7. Optionally write to Neo4j and/or stage to Databricks.
8. Persist local run for reload.

### Databricks pipeline

Path:

- `databricks/src/ingest_documents.py`
- `databricks/src/extract_to_delta.py`
- `databricks/src/evaluate_extractions.py`
- `databricks/src/sync_to_neo4j.py`

Flow:

1. Ingest raw documents into Delta.
2. Create graph-ready primitive candidates.
3. Compute extraction quality and benchmark tables.
4. Sync accepted graph nodes to Neo4j when secrets are configured.

## Why It Matters

The product needs a repeatable path from messy sources to auditable context:

source -> chunk -> evidence span -> primitive -> rule signal -> benchmark ->
review queue -> Praxis context.

Without this chain, Praxis would receive generic summaries. With it, Praxis can
show what is known, what is uncertain, what is constrained, and what should be
reviewed next.

## How To Test

Local CLI:

```bash
uv run dialectica ingest data/sample_docs --workspace-id local-workspace --case-id demo --dry-run
```

GraphOps API:

```bash
POST /api/graphops/ingest
POST /api/graphops/praxis/context
GET /api/graphops/runs
```

Frontend:

```bash
cd apps/web
npm run typecheck
npm run build
```

## Future Improvements

- Add source packs and trust/license metadata to every upload.
- Add episode boundary editing.
- Add entity resolution candidate generation.
- Add targeted extraction retries for missing primitive types.
- Add export routes for JSONL, Cypher, and Praxis context bundles.
