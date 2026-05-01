# DIALECTICA Monster Todo

Date: 2026-05-01

Purpose: turn DIALECTICA into a production-grade, single-user neurosymbolic GraphRAG workbench for TACITUS and Praxis.

## Operating Principle

Build the differentiating backbone in this order:

1. Graph writeback.
2. Hybrid retrieval planning.
3. Trace and explanation.
4. Review queue.
5. Rule library.
6. Benchmark regression.
7. Dynamic ontology versioning.
8. Praxis and SDK integration.

## Milestone 1: Graph Writeback

Status: in progress.

Goal: every accepted extraction, rule signal, benchmark artifact, and review item can be written idempotently to Neo4j.

Implemented:

- `buildGraphOpsGraphWritePlan`.
- `writeGraphOpsPlanToNeo4j`.
- `POST /api/graphops/graph/upsert`.
- Refactored ingestion graph writes through the shared graph module.
- `GET /api/graphops/graph/status`.
- Graph writeback contract test for stable node/edge identities.
- Neo4j runtime schema file: `infrastructure/neo4j/graphops_runtime_schema.cypher`.

Next:

- Add idempotency test that writes the same run twice.
- Add migration file under `infrastructure/neo4j` matching the runtime schema.
- Add support for explicit graph edge rows, not only inferred edges from primitive foreign keys.

Acceptance:

- A sample run can be written twice without changing node or edge counts.
- Query endpoint can retrieve SourceChunk, EvidenceSpan, Claim, Actor, RuleSignal, ReviewDecision, BenchmarkRun.
- Graph write summary reports nodes, edges, warnings, and skipped targets.

## Milestone 2: Hybrid Retrieval Planner

Status: v0 contract implemented.

Implemented:

- `buildGraphOpsRetrievalPlan`.
- `POST /api/graphops/retrieval/plan`.
- `executeGraphOpsRetrievalLocally`.
- `POST /api/graphops/retrieval/execute`.

Next:

- Connect to Neo4j allowlisted Cypher execution.
- Add vector/hybrid placeholders only where indexes exist; otherwise fallback to graph neighborhood retrieval.
- Store retrieval plans and executed Cypher in local run artifacts and benchmark outputs.

Acceptance:

- A question returns a typed plan with strategy, primitive focus, traversal depth, confidence floor, abstention rules, and Cypher template.
- Execution returns cited context, neighborhood nodes, rule findings, and a deterministic trace ID.

## Milestone 3: Trace Viewer

Status: v0 API contract implemented.

Implemented:

- `buildGraphOpsTraceBundle`.
- `POST /api/graphops/trace/build`.

Next:

- Add a visual trace panel to GraphOps.
- Render retrieval plan, graph context, rule findings, citations, and benchmark summary.
- Add export-as-JSON and copy-link affordances.

Acceptance:

- For any graph-grounded answer, the user can see why the retrieval strategy was chosen, which graph nodes were used, which rules fired, and which quotes support the answer.

## Milestone 4: Review Queue

Status: partial.

Existing:

- Praxis review queue derivation from rule signals, weak evidence, missing types, duplicate actor candidates, and unsupported causal claims.

Next:

- Add `GET /api/graphops/review/queue`.
- Add `POST /api/graphops/review/decisions`.
- Persist decisions locally and optionally to Neo4j.
- Add accept, reject, modify states to the GraphOps UI.

Acceptance:

- Rejected primitives are excluded from retrieval context.
- Modified primitives supersede prior primitive IDs through an explicit edge.

## Milestone 5: Rule Library

Status: partial.

Next rules:

- R-001 Causal-vs-temporal separator.
- R-002 Commitment tracker.
- R-003 Norm violation.
- R-004 Power asymmetry.
- R-005 Source trust downgrade.
- R-006 Contradiction detection.
- R-007 Ontology coverage gate.
- R-008 Provenance required.
- R-009 Temporal anachronism.
- R-010 Narrative bias marker.

Acceptance:

- Every rule has positive and negative fixtures.
- Rules write RuleSignal objects and never mutate source primitives.

## Milestone 6: Benchmark Engine

Status: partial.

Existing:

- Local deterministic benchmark endpoint.
- Databricks evaluation script.

Next:

- Add gold pack fixtures for literature, mediation, policy, diplomacy, and field reports.
- Add four-stack comparison: plain LLM, vector RAG, GraphRAG, neurosymbolic GraphRAG.
- Add custom metrics for provenance fidelity, causal precision, temporal accuracy, contradiction handling, and abstention quality.

Acceptance:

- A benchmark run can show whether neurosymbolic GraphRAG improves faithfulness, provenance, abstention, and causal precision.

## Milestone 7: Dynamic Ontology Versioning

Status: partial.

Next:

- Version ontology YAML files under `ontology/`.
- Add JSON Schema validation for generated dynamic ontology profiles.
- Add `OntologyVersion` graph nodes.
- Record ontology version on extraction, graph writes, rules, benchmarks, and review decisions.

Acceptance:

- Old runs remain reproducible after an ontology version bump.

## Milestone 8: Databricks Lakehouse Hardening

Status: partial.

Next:

- Normalize bronze, silver, and gold table contracts.
- Enable CDF on graph-ready node and edge tables.
- Add graph sync audit table and watermark.
- Add failed sync retry state with last error.

Acceptance:

- Databricks can answer what changed, what synced, what failed, and what needs review.

## Milestone 9: Praxis Integration

Status: partial.

Existing:

- Praxis context endpoint.

Next:

- Add stable TypeScript client function for Praxis.
- Add contract tests for `tacitus.dialectica.praxis_context.v1`.
- Add answer constraints and trace URLs to Praxis context output.

Acceptance:

- Praxis can call DIALECTICA with a source or run ID and receive a typed, provenance-rich context bundle.

## Milestone 10: Production Operations

Status: partial.

Next:

- Add deployment health checklist.
- Add Vercel env/secrets validation endpoint without exposing values.
- Add CI for typecheck, build, Python lint, and targeted tests.
- Add dependency audit remediation plan.

Acceptance:

- Main deploys only after tests, typecheck, build, and critical graph-contract tests pass.

## Immediate Next Engineering Targets

1. Add Neo4j-backed retrieval execution behind the current local-first executor.
2. Add GraphOps trace panel UI.
3. Add review decision API.
4. Add explicit edge extraction model for MADE_BY, CONTRADICTS, CAUSES, HAS_INTEREST, BINDS, FRAMES.
5. Add first gold pack fixture for Melian Dialogue or Romeo and Juliet.
6. Add rule fixtures for R-001, R-007, and R-008.
7. Add Praxis SDK helpers for context, retrieval, and trace.
8. Add CI wiring for the new Jest graph contract tests.
9. Add dependency audit remediation plan for current npm audit findings.
10. Add optional Databricks demo workflow trigger after local demo-run success.

## Demo-Ready Slice

Status: implemented in the GraphOps web surface.

Implemented:

- `POST /api/graphops/demo/run`.
- `buildGraphOpsDemoReadyRun`.
- Local artifact persistence for demo-ready runs.
- GraphOps UI panel near the top of the console.
- Contract test proving the demo envelope includes extraction, graph plan,
  retrieval, trace, benchmark, and Praxis context.

Acceptance:

- A user can click one button and see a coherent source-to-Praxis demo without
  needing Neo4j or Databricks secrets.
- Live Neo4j writes stay off by default; the demo uses graph write dry-run
  output and graph status separately.

## Promo Recording Slice

Status: implemented in the GraphOps web surface.

Implemented:

- `POST /api/graphops/promo/studio`.
- `buildGraphOpsPromoStudioRun`.
- Shared Aletheia AI planner contract for `/api/graphops/ai-command` and the
  promo studio.
- GraphOps UI panel with promo readiness, live checks, API proof, wow moments,
  recording script, and Praxis handoff.

Acceptance:

- A new user can click one button and get a two-minute promo script that proves
  the live API, AI planner, GraphRAG trace, benchmark guardrails, and Praxis
  context handoff.
- The promo output names review gaps explicitly so the demo can explain
  uncertainty as a first-class feature.
