# May Demo Prompts Process

Last updated: 2026-05-03

## Prompt Files

- May Prompt 1: `docs/prompts/MAY_PROMPT_01_INGESTION_THEATRE.md`
- May Prompt 2: `docs/prompts/MAY_PROMPT_02_REASONING_THEATRE.md`

May Prompt 1 is the active implementation target. May Prompt 2 depends on the
graph-building handoff route produced by Prompt 1.

## Branching

- Prompt archive branch on GitHub: `may-demo-prompts`.
- Prompt 1 implementation branch: `feat/demo-ingestion-theatre-prompt1`.
- Prompt 2 implementation branch, after Prompt 1 lands:
  `feat/demo-reasoning-theatre`.

## Current Remote Baseline

`origin/main` already contains a merged ingestion PR with several Prompt 1
building blocks:

- `packages/api/src/dialectica_api/services/pipeline_runner.py`
- `packages/api/src/dialectica_api/services/job_store.py`
- `packages/api/src/dialectica_api/routers/extraction_stream.py`
- `packages/api/src/dialectica_api/routers/gutenberg.py`
- `packages/extraction/src/dialectica_extraction/sources/gutenberg.py`
- `apps/web/src/components/extraction/LiveExtractionProgress.tsx`
- Gutenberg picker and corpus pages under `apps/web/src/app/workspaces/[id]/`

This means Prompt 1 work should not rebuild the SSE/Gutenberg foundation from
scratch. The next work is to turn those primitives into the cinematic `/demo`
theatre and add the missing demo-only controls, replay mode, data corpus, and
act components.

## Prompt 1 Audit Against Current Repo

| Contract Path | Current State | Action |
| --- | --- | --- |
| `docs/ARCHITECTURE.md` | Exists | Use as canonical ingestion architecture reference. |
| `packages/extraction/src/dialectica_extraction/pipeline.py` | Exists | Reuse 10-step extraction DAG and step names. |
| `packages/api/src/dialectica_api/services/pipeline_runner.py` | Exists | Extend counts and cost metadata as needed. |
| `packages/api/src/dialectica_api/routers/extraction_stream.py` | Exists | Reuse for live mode; add replay/capture docs separately. |
| `packages/extraction/src/dialectica_extraction/sources/gutenberg.py` | Exists | Use book IDs 1513 and 2600 for doors. |
| `data/seed/samples/syria_civil_war.json` | Exists | Keep as graph seed; add narrative corpus for text extraction. |
| `data/seed/benchmarks/*_gold.json` | Exists | Use for replay validation/backstop, not as fake live graph. |
| `apps/web/src/components/extraction/LiveExtractionProgress.tsx` | Exists | Reuse event-source wiring concepts, not the linear UI. |
| `apps/web/src/components/graph/ForceGraph.tsx` | Exists | Extend through props/wrapper, do not duplicate graph library. |
| `apps/web/src/lib/api.ts` | Exists | Extend with demo reset/cost/preview helpers. |
| `apps/web/src/types/graph.ts` | Exists | Extend types, do not fork. |
| `apps/web/src/app/demo/page.tsx` | Exists | Replace fake progress with conductor surface. |

## Implementation Order For Prompt 1

1. Normalize architecture-doc casing for Windows-safe development on this branch.
2. Add demo data and manifests:
   - `data/sample_docs/syria_2011_2024_briefing.txt`;
   - `apps/web/public/demo/corpora/syria_2011_2024_briefing.txt`;
   - `apps/web/src/components/demo/data/doors.ts`;
   - narrator scripts and replay metadata.
3. Add backend demo controls:
   - demo workspace reset guarded by `DEMO_RESET_ENABLED`;
   - cost/count endpoint for extraction jobs;
   - any missing preview helper needed by `/demo`.
4. Replace `/demo` with a client-only ingestion theatre:
   - conductor state;
   - eleven act components;
   - live SSE and replay drivers with identical event shape;
   - event log drawer, pause/manual controls, keyboard shortcuts;
   - existing `ForceGraph` wrapper for graph materialization.
5. Add initial replay fixtures and replay-mode banner.
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

- Prompt files archived on GitHub branch `may-demo-prompts`.
- Prompt 1 implementation branch: started.
- Backend SSE/Gutenberg foundation: present from `origin/main`.
- Frontend theatre: first scaffold complete. `/demo` now uses a client
  conductor, eleven act files, live SSE/replay mode switching, event-log drawer,
  pause/skip controls, scenario manifest, and Prompt 2 handoff stub.
- Replay capture: starter NDJSON fixtures added; live capture middleware still
  not implemented.
- E2E: not started.
