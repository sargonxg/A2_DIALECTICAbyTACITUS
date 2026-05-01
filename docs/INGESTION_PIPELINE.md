# DIALECTICA Ingestion Pipeline

Last updated: 2026-05-01

## What Changed

This wave adds a Praxis-ready context surface on top of existing ingestion:

- GraphOps can already ingest text, samples, TXT, and PDF.
- Ingested runs persist locally and can be reloaded.
- `/api/graphops/praxis/context` can consume a saved run, raw primitives, or
  fresh text/sample input and return a downstream-ready bundle.

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
