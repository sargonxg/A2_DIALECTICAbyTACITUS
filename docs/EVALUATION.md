# DIALECTICA Evaluation

Last updated: 2026-05-01

## What Changed

Evaluation now has three layers:

1. FastAPI gold-corpus benchmark runner.
2. GraphOps local deterministic benchmark engine.
3. Databricks Delta benchmark tables.

This wave adds the missing downstream product gate:

- `/api/graphops/praxis/context` computes a readiness score and review queue
  before Praxis consumes generated context.

## Current Evaluation Surfaces

### FastAPI benchmark

Path:

- `packages/api/src/dialectica_api/benchmark_runner.py`
- `packages/api/src/dialectica_api/routers/benchmark.py`
- `apps/web/src/app/admin/benchmarks/page.tsx`

Measures entity and relationship precision/recall/F1 and hallucination rate
against gold corpora.

### GraphOps benchmark

Path:

- `apps/web/src/lib/graphopsBenchmark.ts`
- `apps/web/src/app/api/graphops/benchmarks/run/route.ts`
- `/graphops` Answer Quality Lab

Scores:

- ontology coverage;
- evidence grounding;
- source grounding;
- causal discipline;
- rule compliance;
- answer usefulness.

### Databricks benchmark tables

Path:

- `databricks/src/evaluate_extractions.py`

Outputs:

- `benchmark_runs`
- `benchmark_scores`
- `benchmark_diagnostics`

### Praxis context readiness

Path:

- `apps/web/src/lib/praxisContext.ts`
- `apps/web/src/lib/graphopsReview.ts`
- `apps/web/src/app/api/graphops/praxis/context/route.ts`

Outputs:

- readiness status and score;
- blockers and warnings;
- review items;
- answer constraints;
- compact evidence-backed context.

## Why It Matters

DIALECTICA should not pass unreviewed extraction output directly to downstream
products. The evaluation layer tells Praxis:

- what can be used safely;
- what should be phrased as uncertain;
- what must be reviewed;
- what missing ontology coverage prevents strong answers.

## How To Test

```bash
cd apps/web
npm run typecheck
npm run build
```

```bash
uv run ruff check databricks/src
python -m py_compile databricks/src/*.py
```

Sample API flow:

```http
POST /api/graphops/praxis/context
{
  "sampleKey": "policy-constraint-map",
  "workspaceId": "policy-demo",
  "caseId": "river-city-housing",
  "objective": "Map policy constraints and implementation risks.",
  "ontologyProfile": "policy-analysis"
}
```

Expected response:

- `kind = tacitus.dialectica.praxis_context.v1`
- `readiness.score` between 0 and 1
- non-empty `context.actors`, `context.claims`, and `context.topEvidence`
- `reviewQueue` with temporal/review items when events lack exact dates.

## Future Improvements

- Add fixture tests for the Praxis context route.
- Add gold datasets for mediation, diplomacy, sanctions/compliance, and crisis
  operations.
- Add Databricks Agent Evaluation notebooks using the same rubric.
- Add CI regression thresholds for ontology coverage, evidence grounding, and
  causal discipline.
