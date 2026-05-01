# GraphOps User Usability Targets

Date: 2026-05-01

Objective: a user can open `/graphops`, choose a case objective, ingest text or a sample, inspect typed primitives, see readiness/rule signals, and reload previous runs even without Neo4j or Databricks credentials.

## Implemented In This Pass

1. Local run persistence: every GraphOps ingest is saved under `.dialectica/graphops/runs`.
2. Run history API: `/api/graphops/runs` lists recent local runs.
3. Run reload API: `/api/graphops/runs/[id]` returns a saved run.
4. Console run history: `/graphops` shows recent local runs and reloads them into the result panel.
5. Readiness scoring: extraction results now include quality score, evidence coverage, actor count, issue count, and recommendations.
6. Better arbitrary-text actor extraction: capitalized people, institutions, councils, agencies, unions, and commands can be extracted without being hardcoded.
7. Policy and field samples: policy constraint and field intelligence needs now have runnable sample texts.
8. Richer graph preview edges: graph previews include source/chunk/episode/actor/constraint structural edges, not only evidence links.

## Next Ten Targets

1. Add a review queue panel for low-confidence claims, weak evidence, missing actors, and rule blockers.
2. Add a graph-grounded answer endpoint that returns answer text plus cited evidence spans and rule constraints.
3. Add a per-run graph viewer tab using the extracted preview graph from saved local runs.
4. Add explicit source trust controls before ingestion: internal, public, media, transcript, uncertain, sensitive.
5. Add episode splitting controls so a user can segment a document by scene, meeting, incident, phase, or date.
6. Expand Databricks extraction to reconstruct all staged GraphOps primitive and rule artifact rows into Delta.
7. Add export buttons for JSONL, Cypher, and Delta-ready JSON from each local run.
8. Local benchmark creation: `/api/graphops/benchmarks/run` scores a saved extraction run, raw primitives, or fresh sample text.
9. Console benchmark workbench: `/graphops` can score the current run or the active sample and show metric diagnostics.
10. Add a workspace home page that groups runs by workspace/case and shows status across ingestion, rules, graph write, and benchmarks.
11. Add an offline Neo4j Docker quick-start check that can initialize schema and write the latest local run.
