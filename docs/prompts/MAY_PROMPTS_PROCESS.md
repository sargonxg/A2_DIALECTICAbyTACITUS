# May Demo Prompts Process

Last updated: 2026-05-03

## Prompt Files

- May Prompt 1: `docs/prompts/MAY_PROMPT_01_INGESTION_THEATRE.md`
- May Prompt 2: `docs/prompts/MAY_PROMPT_02_REASONING_THEATRE.md`

May Prompt 1 is the active implementation target. May Prompt 2 depends on the
graph-building handoff route produced by Prompt 1.

## Branching

- Prompt archive and this process tracker live on `main`.
- Prompt 1 implementation branch: `feat/demo-ingestion-theatre`.
- Prompt 2 implementation branch, after Prompt 1 lands:
  `feat/demo-reasoning-theatre`.

## Prompt 1 Audit Against Current Repo

The prompt is directionally correct, but several referenced files do not exist
in the current checkout and must be implemented or adapted.

| Contract Path | Current State | Action |
| --- | --- | --- |
| `docs/ARCHITECTURE.md` | Exists | Use as canonical architecture reference. |
| `packages/extraction/src/dialectica_extraction/pipeline.py` | Exists | Reuse 10-step extraction DAG and step names. |
| `packages/api/src/dialectica_api/services/pipeline_runner.py` | Missing | Add runner service that emits canonical progress events. |
| `packages/api/src/dialectica_api/routers/extraction_stream.py` | Missing | Add SSE router or integrate equivalent routes into API. |
| `packages/extraction/src/dialectica_extraction/sources/gutenberg.py` | Missing | Add minimal Gutenberg catalogue/preview helper for book IDs 1513 and 2600. |
| `data/seed/samples/syria_civil_war.json` | Exists | Keep as benchmark seed; add narrative corpus for demo extraction. |
| `data/seed/benchmarks/*_gold.json` | Exists | Use for replay validation/backstop, not as fake live graph. |
| `apps/web/src/components/extraction/LiveExtractionProgress.tsx` | Missing | Build new demo event consumer from scratch using existing API patterns. |
| `apps/web/src/components/graph/ForceGraph.tsx` | Exists | Extend via props/wrapper, do not duplicate graph library. |
| `apps/web/src/lib/api.ts` | Exists | Extend with demo stream/reset/cost/preview helpers. |
| `apps/web/src/types/graph.ts` | Exists | Extend types, do not fork. |
| `apps/web/src/app/demo/page.tsx` | Exists | Replace conductor surface; do not reuse old fake progress behavior. |

## Implementation Order For Prompt 1

1. Archive prompts and process docs.
2. Create `feat/demo-ingestion-theatre`.
3. Add backend demo contracts:
   - demo workspace reset guarded by `DEMO_RESET_ENABLED`;
   - pipeline runner that wraps the existing extraction DAG and emits
     canonical events;
   - SSE stream endpoint;
   - Gutenberg preview/ingest helpers;
   - cost/count endpoint;
   - tests for tenant/workspace guards and replay-friendly event shape.
4. Add data assets:
   - `data/sample_docs/syria_2011_2024_briefing.txt`;
   - `apps/web/public/demo/corpora/syria_2011_2024_briefing.txt`;
   - initial replay NDJSON fixtures generated from local deterministic runs
     until live capture exists.
5. Replace `/demo` with a client-only ingestion theatre:
   - conductor state;
   - eleven act components;
   - live SSE and replay drivers with identical event shape;
   - event log drawer, pause/manual controls, keyboard shortcuts;
   - existing `ForceGraph` wrapper for graph materialization.
6. Add e2e replay tests for all three doors.
7. Update README and architecture/admin docs.

## Local Repo Deviations To Respect

- The web package currently uses `npm`, not `pnpm`.
- Next.js is App Router under `apps/web/src/app`.
- API tests run with `uv run pytest`.
- Existing auth middleware protects non-public API routes; new demo-write
  routes must remain guarded except public health/preview assets.
- No synthetic graph should be displayed as a live run. Offline mode must be
  labelled replay mode and sourced from NDJSON events.

## Current Status

- Prompt files archived: in progress.
- Prompt 1 repo audit: started.
- Backend demo contracts: not started.
- Frontend theatre: not started.
- Replay capture: not started.
- E2E: not started.
