# May Demo Research Execution Plan

Last updated: 2026-05-03

This plan consolidates the pasted May Prompt 1/2 documents and the local
research notes into one execution track. The goal is a credible TACITUS demo:
real ingestion, real graph memory, theory-grounded reasoning, and honest
fallbacks.

## Source Documents Used

- `docs/prompts/MAY_PROMPT_01_INGESTION_THEATRE.md`
- `docs/prompts/MAY_PROMPT_02_REASONING_THEATRE.md`
- `docs/DIALECTICA_NEUROSYMBOLIC_GRAPHRAG_RESEARCH.md`
- `docs/DIALECTICA_GRAPH_PIPELINE_PLAN.md`
- `docs/graphops/tacitus-graph-architecture.md`
- `docs/graphops/neurosymbolic-rule-layer.md`
- `docs/neurosymbolic-rationale.md`
- `docs/theory-frameworks.md`

## Product Thesis

DIALECTICA is not a better chat prompt. It is a graph backbone for conflict,
statecraft, and human-friction work. The demo has to prove that distinction in
two moves:

1. Ingestion theatre: show how prose becomes typed, validated, provenance-carrying
   graph memory.
2. Reasoning theatre: show how graph memory becomes citable, reproducible,
   theory-grounded answers.

## Architecture Commitments

- Neo4j is the live operational graph.
- Databricks is the optional batch, quality, and benchmark layer.
- GraphRAG retrieval must expose retrieved nodes, edges, and query plan.
- Symbolic rules fire before LLM synthesis.
- Rule outputs create `RuleSignal`, `RuleFire`, `AnswerConstraint`, and
  `BenchmarkTarget` artifacts; they should not mutate primitive facts.
- Every graph object must preserve workspace, tenant, source, evidence,
  confidence, review status, and temporal fields where relevant.
- Fallbacks must be labelled replay or fixture mode. They must not pretend to be
  live graph computation.

## Current Implementation State

Done on the May branches:

- Prompt archive files are in `docs/prompts/`.
- `/demo` has an ingestion theatre scaffold with 11 acts and replay support.
- `data/sample_docs/syria_2011_2024_briefing.txt` and public demo corpus copy
  exist.
- `/demo/{scenarioId}/reasoning` has a reasoning theatre scaffold.
- `data/seed/reasoning_library.json` contains the 23 curated Prompt 2 questions.
- `packages/reasoning/src/dialectica_reasoning/library.py` loads and validates
  that curated library.
- Backend endpoints now expose the Prompt 2 adapter contract:
  - `GET /v1/workspaces/{ws}/reason/library`
  - `POST /v1/workspaces/{ws}/reason/curated`
  - `POST /v1/workspaces/{ws}/reason/counterfactual`
  - `POST /v1/workspaces/{ws}/reason/similarity`
- The reasoning page has a "Run live API" control and otherwise stays in
  clearly-labelled deterministic fixture mode.

## Remaining Work By Milestone

### Milestone 1 — Honest Demo Completion

- Replace starter replay fixtures with captured NDJSON from real runs.
- Add replay validation against gold graph counts.
- Add `/demo` E2E tests for Romeo, War and Peace, and Syria.
- Add `/demo/{scenarioId}/reasoning` E2E tests for all 23 question cards.
- Add visible live/replay/fixture badges across both theatres.

### Milestone 2 — Live Reasoning Correctness

- Move `ReasoningResult` models from the API router into a shared reasoning
  module so backend, tests, and future SDKs use one contract.
- Implement `query_engine.answer_curated(question_id, workspace_id, tenant_id)`.
- Preserve tenant filtering through every retrieval and graph traversal call.
- Return actual cited edge IDs, not only cited node IDs.
- Pipe hallucination-detector output into `hallucination_risk` as a numeric
  score.
- Persist successful `ReasoningTrace` nodes for later validation.

### Milestone 3 — Counterfactuals That Recompute

- Implement `MutilatedGraph` as an in-memory GraphClient-compatible adapter.
- Delete requested nodes/edges from the transient graph only.
- Re-run symbolic rules and GraphRAG on the transient graph.
- Return a typed diff of stage, confidence, cited paths, and causal chain
  changes.
- Add tests proving Neo4j is not mutated.

### Milestone 4 — Structural Similarity

- Seed comparison-corpus workspaces:
  - vendetta cases for Romeo;
  - imperial-overreach cases for War and Peace;
  - successor/civil-war recurrence cases for Syria.
- Compute semantic centroids from conflict/event embeddings.
- Add a Weisfeiler-Lehman topology signature for actor-issue-event graphs.
- Return combined semantic/topological neighbours with cited mapping
  explanations.

### Milestone 5 — GraphOps And Evaluation Loop

- Snapshot demo workspaces into Databricks Delta when configured.
- Log benchmark runs comparing plain LLM, vector RAG, GraphRAG, and
  neurosymbolic GraphRAG.
- Add custom metrics: provenance fidelity, causal precision, temporal accuracy,
  contradiction handling, abstention quality, and intervention usefulness.
- Show benchmark results in the app without requiring Databricks for local demo
  mode.

## Immediate Next Engineering Tasks

1. Add API tests for the curated library and similarity adapter.
2. Add a backend test for `/reason/curated` with a stub query engine.
3. Refactor Prompt 2 API models into `dialectica_reasoning.results`.
4. Add a frontend API-status pill so users understand fixture vs live mode at a
   glance.
5. Add E2E coverage for question-card navigation and the "Run live API" error
   state.

## Demo Narrative

The clean 90-second story:

1. Pick a corpus.
2. Watch ingestion create typed graph memory.
3. Ask a deterministic question.
4. Compare an LLM paragraph with a traced DIALECTICA answer.
5. Open the trace and show retrieved graph objects, symbolic rules, and JSON.
6. Toggle a counterfactual or structural-similarity question.
7. Explain that the same backbone supports policy, books, litigation, strategy,
   and research workflows because the ontology captures structure, not just
   text.
