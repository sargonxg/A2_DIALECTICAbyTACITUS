# GraphOps Benchmarking Engine

The first production objective is simple: every ingestion run should be scored
before it is trusted by Praxis. The local GraphOps benchmark engine gives the
operator an immediate deterministic score, while Databricks remains the deeper
judge pipeline for model-vs-model and corpus-scale evaluation.

## Runtime Surface

- `POST /api/graphops/benchmarks/run`
- `GET /api/graphops/benchmarks/run?limit=20`
- `/graphops` Answer Quality Lab -> `Run Local Benchmark`
- local artifacts under `.dialectica/graphops/benchmarks`
- Databricks Delta outputs: `benchmark_runs`, `benchmark_scores`,
  `benchmark_diagnostics`

The route accepts:

- a saved `extractionRunId`;
- raw `primitives`;
- or fresh `text` / `sampleKey`, which is extracted and rule-evaluated before
  scoring.

## Scoring Rubric

The deterministic rubric uses six weighted metrics:

| Metric | Weight | Why it matters |
| --- | ---: | --- |
| `ontologyCoverage` | 0.18 | Conflict, policy, and diplomacy questions need actors, claims, events, constraints, episodes, and evidence. |
| `evidenceGrounding` | 0.22 | Claim-like primitives must carry evidence spans before graph-grounded generation. |
| `sourceGrounding` | 0.16 | Candidate answers should overlap with retrieved evidence, not only generic summary. |
| `causalDiscipline` | 0.14 | The engine must separate sequence from causality unless source text supports causal language. |
| `ruleCompliance` | 0.16 | Neurosymbolic warnings and blockers reduce readiness. |
| `answerUsefulness` | 0.14 | A useful Praxis answer names actors, constraints, uncertainty, and next questions. |

The output includes primitive counts, missing ontology types, weak evidence IDs,
unsupported causal claims, top evidence spans, rule-summary context, benchmark
targets, and concrete recommendations.

## Research Alignment

This implementation follows the same separation used by the larger architecture:

- Neo4j GraphRAG packages separate retrievers, graph context, prompt templates,
  and LLM generation. DIALECTICA mirrors that by scoring graph readiness before
  answer generation.
- Databricks Vector Search and AI Functions support the larger cloud path:
  index/query unstructured context, use model-serving endpoints, and persist
  tabular judgments for repeated evaluation.
- RAG evaluation frameworks such as Ragas distinguish context precision,
  faithfulness/groundedness, and answer relevance. DIALECTICA translates those
  ideas into graph-native equivalents: evidence grounding, source grounding,
  ontology coverage, rule compliance, and causal discipline.

## Next Production Blocks

1. Add graph writeback for `BenchmarkRun`, `BenchmarkScore`,
   `BenchmarkDiagnostic`, and `BENCHMARKS_RUN` relationships in Neo4j.
2. Add judge prompts that compare baseline LLM answers against graph-grounded
   answers for the same question.
3. Add gold corpora for diplomacy, policy, mediation, literary conflict, and
   incident brief use cases.
4. Add trend reporting so regressions in ontology coverage, evidence grounding,
   or causal discipline block deployment.
