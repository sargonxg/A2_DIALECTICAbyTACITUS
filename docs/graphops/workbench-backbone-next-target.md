# GraphOps Workbench Backbone: Next Engineering Target

The next engineering target is a visible, API-backed workbench contract. Praxis
and standalone developer tools should be able to ask one question at any time:
which block is ready, which block is weak, and what should be improved next?

## What Was Added

- `GET /api/graphops/workbench/status`
- `POST /api/graphops/workbench/status`
- `/graphops` workbench readiness board
- block scoring across ingestion, ontology, temporal segmentation, extraction,
  graph memory, neurosymbolic rules, benchmarks, and product serving
- developer-surface inventory for external tools and Praxis
- research-alignment inventory so implementation choices stay tied to proven
  GraphRAG and evaluation patterns

## Research-Aligned Architecture

The workbench follows five patterns from current GraphRAG and agent evaluation
systems:

1. Structured extraction should preserve source grounding and exact spans.
2. GraphRAG indexing should be staged: text units, entity/relationship
   extraction, graph construction, communities or summaries, and retrieval.
3. Hybrid retrieval should combine vector similarity, full-text matching, graph
   traversal, and safe Text2Cypher-style access where appropriate.
4. Evaluation should use offline evaluation sets during development and online
   production monitoring once traffic exists.
5. Human review should be first-class: rule signals, benchmark diagnostics, and
   review decisions become graph objects instead of hidden notes.

## Practical Next Build Sequence

1. **Review Queue**
   - Turn rule signals and benchmark diagnostics into visible review items.
   - Add `ReviewDecision` persistence for accept/reject/needs-source states.

2. **Hybrid Retrieval Planner**
   - Create a route that returns a retrieval plan: vector query, full-text query,
     Cypher traversal, source-span budget, and answer constraints.
   - Keep the first implementation deterministic and allowlisted.

3. **Graph Writeback for Benchmarks**
   - Write `BenchmarkRun`, `BenchmarkScore`, and `BenchmarkDiagnostic` into
     Neo4j once production secrets are rotated.
   - Link benchmark objects to `ExtractionRun`, `RuleSignal`, and `EvidenceSpan`.

4. **Gold Evaluation Sets**
   - Build small gold sets for book conflict, mediation, policy, diplomacy, and
     incident briefs.
   - Include question, expected answer, expected primitive types, required
     evidence spans, and failure modes.

5. **Standalone Developer Contract**
   - Add examples for calling ingest, rule evaluation, workbench status,
     benchmark scoring, and retrieval planning.
   - Add SDK-ready schemas for all GraphOps endpoints.

## Praxis Fit

Praxis should use DIALECTICA as a context engine:

- send a situation or conversation excerpt;
- receive typed actors, claims, commitments, constraints, events, narratives,
  evidence spans, and rule signals;
- ask for the workbench status;
- only generate advice once graph coverage, evidence grounding, and rule
  compliance are strong enough;
- show uncertainty and next questions when the graph is not ready.

This makes DIALECTICA useful both as an internal engine for `praxis.tacitus.me`
and as a standalone workbench for developers building conflict, policy,
mediation, and diplomacy tools.
