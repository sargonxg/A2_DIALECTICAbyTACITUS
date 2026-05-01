# DIALECTICA Autonomous Improvement Plan

Last updated: 2026-05-01

## Phase 1: Actual System Reconstruction

DIALECTICA is a mixed Python/TypeScript monorepo with three important layers:

1. **Canonical Python platform**
   - `packages/ontology`: ACO v2 ontology, 15 conflict node types, 20 edge
     types, theory modules, validators, compatibility mappers.
   - `packages/extraction`: LangGraph-style extraction pipeline with chunking,
     GLiNER prefilter fallback, Gemini/Instructor extraction, schema repair,
     relationship extraction, coreference, structural/temporal/symbolic
     validation, embeddings, and graph write.
   - `packages/graph`: graph abstraction for Neo4j, FalkorDB, Spanner, Qdrant.
   - `packages/reasoning`: symbolic reasoning, GraphRAG modules, KGE, agents.
   - `packages/api`: FastAPI app with workspaces, extraction, graph, reasoning,
     integration, benchmark, analytics, auth, tenancy, and rate limiting.

2. **TACITUS core v1 local slice**
   - `dialectica/ontology/models.py`: narrow Pydantic primitive contract with
     required workspace/case separation, provenance, confidence, and temporal
     fields.
   - `dialectica/ingestion`: local TXT ingestion, chunking, deterministic
     extraction, ontology mapping, JSONL/graph write.
   - `dialectica/graph`: memory and Neo4j adapters for the local vertical slice.

3. **GraphOps operator app**
   - `apps/web`: protected Next.js console at `/graphops`.
   - Live routes include ingestion, dynamic ontology creation, local run reload,
     rules, benchmarks, Databricks job/tables/run, pipeline planning, manifest,
     and workbench status.
   - Local runs are saved under `.dialectica/graphops/runs`; local benchmark
     artifacts under `.dialectica/graphops/benchmarks`.

## What Is Real vs Aspirational

Real and locally verifiable:
- Text/TXT/PDF/sample ingestion through GraphOps.
- Source chunking, evidence spans, actors, claims, constraints, commitments,
  events, narratives, actor states.
- Dynamic ontology plan generation and pre-extraction segmentation.
- Neurosymbolic rule evaluation.
- Local benchmark scoring and Databricks benchmark table writer.
- Workbench readiness contract and visual status board.
- FastAPI benchmark runner and admin benchmark UI.
- Neo4j write paths exist, but production writeback depends on rotated secrets.

Aspirational or partially implemented:
- Full production GraphRAG retrieval is mostly in Python packages/docs, not fully
  wired into the current GraphOps user flow.
- Text2Cypher/hybrid retrieval is documented and partially represented, but the
  protected GraphOps query route is allowlisted rather than a full retrieval
  planner.
- Agentic reasoning exists in package form and Databricks launch wrappers, but
  structured agent outputs are not yet deeply persisted as graph objects.
- Entity resolution exists in older extraction pipeline modules but is thin in
  the new TACITUS core v1/GraphOps slice.

## Phase 2: Backbone Strategy

DIALECTICA should become a provenance-first context graph engine:

- **Stable core primitives**: Actor, Claim, Interest, Constraint, Leverage,
  Commitment, Event, Narrative, Episode, ActorState, SourceDocument,
  SourceChunk, EvidenceSpan, ExtractionRun.
- **Dynamic ontology layer**: case-specific types are permitted only when mapped
  to core primitives and scored for coverage.
- **Reasoning layer**: deterministic rule signals constrain generation before
  LLM synthesis.
- **Evaluation layer**: every run has benchmark/readiness scores before Praxis
  or downstream products consume it.
- **Review layer**: uncertainty becomes analyst work, not hidden prose.

The current weakest backbone areas are entity resolution, temporal episode
editing, review queue persistence, hybrid retrieval planning, and graph writeback
for rule/benchmark/review artifacts.

## Phase 3: Customer Workflow Alignment

| Workflow | Inputs | Graph objects | Valuable outputs | Downstream consumer |
| --- | --- | --- | --- | --- |
| Diplomats | cables, meeting notes, public statements, treaties | Actor, Claim, Norm/Constraint, Event, Narrative, Commitment | negotiation brief, red lines, concessions, trust risks | Praxis diplomatic brief |
| Mediators | intake notes, party statements, agreements, transcripts | Actor, Interest, Commitment, Constraint, ActorState, Narrative | commitment ledger, process options, verification questions | Praxis mediator companion |
| Intelligence analysts | field reports, OSINT, incident logs, source notes | Actor, Event, Claim, EvidenceSpan, SourceDocument, ActorState | source confidence ledger, gaps, competing hypotheses | conflict desk |
| Defense planners | incident timelines, force posture reports, sanctions docs | Actor, Event, Leverage, Constraint, Narrative | escalation tracker, leverage map, scenario constraints | planning support |
| Sanctions/compliance | statutes, designations, ownership docs, transactions | Actor, Constraint, Leverage, Claim, EvidenceSpan | constrained actor map, evidence bundle, review queue | compliance workbench |
| Enterprise crisis teams | emails, HR notes, incident reports, policies | Actor, Claim, Commitment, Constraint, Narrative, ActorState | trust/risk map, commitments, escalation signals | Praxis enterprise |

## Phase 4: Technical Audit Findings

Critical issues and gaps:
- GraphOps frontend extractor uses deterministic heuristics and should not be
  represented as full AI extraction.
- Core v1 local extraction has strong provenance fields, but weak temporal
  normalization and no explicit review queue.
- FastAPI extraction job store is in-memory when Pub/Sub is unavailable.
- Neo4j writeback is implemented in several places but production depends on
  secrets and graph artifact schema hardening.
- Entity resolution in the GraphOps slice is mostly name de-duplication.
- Benchmarking now exists locally and in Databricks, but gold sets and CI
  regression gates need expansion.
- API contracts for Praxis need a compact context endpoint instead of requiring
  downstream apps to understand every primitive.

## Phase 5: Research-Informed Design

Useful external patterns:
- Microsoft GraphRAG separates Documents, TextUnits, Entities, Relationships,
  Claims, Communities, Community Reports, and Embeddings.
- Neo4j GraphRAG exposes vector, vector+Cypher, hybrid, hybrid+Cypher, and
  Text2Cypher retrieval patterns; DIALECTICA should start with allowlisted
  hybrid plans before open Text2Cypher.
- LangExtract emphasizes exact source grounding, long-document chunking,
  parallel/multi-pass extraction, and interactive source review.
- Databricks Agent Evaluation separates offline evaluation sets from production
  monitoring and gives root-cause diagnostics for failed rows.
- Ragas metrics map cleanly to DIALECTICA metrics: context precision/recall,
  faithfulness, response relevance, groundedness, tool accuracy, and rubrics.
- Neo4j GDS Node Similarity is useful for candidate entity resolution but must
  be bounded because all-pairs similarity is expensive.
- Event sourcing is valuable only where audit/history justifies added
  complexity; use append-only ReviewDecision/ExtractionRun/BenchmarkRun events
  first rather than making every graph write event-sourced.

## Phase 6: Build Task List

### 5 Critical Infrastructure Improvements

1. Praxis-ready context endpoint with typed summaries and review items.
2. Review queue derivation and persistence for rules, weak evidence, missing
   ontology coverage, unsupported causality, and low confidence.
3. Hybrid retrieval planner API with allowlisted Cypher, source budget, vector
   search intent, full-text intent, and answer constraints.
4. Neo4j writeback for BenchmarkRun, BenchmarkScore, RuleSignal, ReviewDecision.
5. Entity resolution candidate engine for Actor aliases and duplicate sources.

### 5 Quality/Reliability Improvements

1. Local evaluation script for provenance completeness, temporal quality, and
   primitive coverage.
2. Fixture tests for policy, diplomacy, mediation, book conflict, and crisis
   workflows.
3. Better temporal normalization and episode boundary validation.
4. Schema compatibility tests between `ontology/tacitus_core_v1.yaml`, Python
   Pydantic models, Databricks tables, and web GraphOps output.
5. Error envelopes on every GraphOps API route with stable `code`, `message`,
   `retryable`, and `details`.

### 5 Product-Enabling Improvements

1. Praxis context card UI with actors, constraints, commitments, events, review
   blockers, and next questions.
2. Export endpoints for JSONL, Cypher, and Praxis context bundles.
3. Developer examples for calling GraphOps from other Tacitus products.
4. Workspace home page grouping runs, benchmark scores, review status, and graph
   write status.
5. Analyst-readable reasoning trace attached to each answer plan.

### 5 Research/Experimental Improvements

1. LangExtract-style grounded extraction adapter behind the existing primitive
   contract.
2. BookNLP adapter for literary conflict and quote/speaker/character graphs.
3. Neo4j GDS entity-resolution candidate notebook/job.
4. Databricks Agent Evaluation notebook using `benchmark_runs` and gold sets.
5. FalkorDB adapter compatibility tests for the core v1 graph subset.

## Current Implementation Wave

This wave implements the highest-value low-risk surface:

- Praxis-ready context bundle API.
- Review queue derivation from primitives, rules, and benchmark diagnostics.
- Documentation for ingestion, ontology, and evaluation decisions.
- Tests/build verification.

## How To Validate

- `npm run typecheck` in `apps/web`
- `npm run build` in `apps/web`
- `uv run ruff check databricks/src`
- `python -m py_compile databricks/src/*.py`
- GraphOps local API checks against `/api/graphops/praxis/context`
- Existing Python tests for core local ingestion and provenance.

## Best Next Direction

After this wave, build the review queue UI and hybrid retrieval planner. Do not
open-endedly add agents until the context contract, review items, retrieval
plans, and benchmark gates are stable enough for Praxis to consume safely.
