# DIALECTICA Ontology Notes

Last updated: 2026-05-01

## What Changed

This wave clarifies the operating ontology split:

- `packages/ontology` remains the broader ACO v2 conflict grammar.
- `ontology/tacitus_core_v1.yaml` and `dialectica/ontology/models.py` define
  the smaller TACITUS core v1 contract used by the GraphOps vertical slice.
- `/api/graphops/praxis/context` now emits a compact downstream context bundle
  instead of exposing only raw primitives.

## Why It Matters

Praxis and future TACITUS products should not need to understand every internal
primitive or every experimental graph layer. They need a stable bundle:

- actors;
- claims;
- commitments;
- constraints;
- events;
- narratives;
- evidence spans;
- answer constraints;
- review items;
- readiness score.

This preserves ontology richness while keeping downstream product integration
simple and auditable.

## Current Core Primitive Contract

The stable core is:

- `Actor`
- `Claim`
- `Interest`
- `Constraint`
- `Leverage`
- `Commitment`
- `Event`
- `Narrative`
- `Episode`
- `ActorState`
- `SourceDocument`
- `SourceChunk`
- `EvidenceSpan`
- `ExtractionRun`

Dynamic ontology extensions are allowed only when mapped back to one of these
core primitives.

## Required Invariants

Every extracted claim-like primitive should preserve:

- `workspace_id`
- `case_id`
- `source_id`
- `extraction_run_id`
- `evidence_span_id`
- `provenance_span`
- `confidence`
- `observed_at`
- `valid_from` / `valid_to` when known

If a value is unknown, the system should preserve uncertainty instead of
fabricating precision.

## Migration Risk

Do not remove or rename ACO v2 node types without migration. The broader Python
packages and docs depend on the 15-node/20-edge ontology. The safest path is:

1. keep ACO v2 as the theory-rich ontology package;
2. keep TACITUS core v1 as the product integration contract;
3. map product-specific/dynamic concepts into core v1;
4. generate graph write schemas from the stable contract.

## How To Test

- `uv run pytest tests/test_provenance_required.py`
- `npm run typecheck` in `apps/web`
- `POST /api/graphops/praxis/context` with `sampleKey=policy-constraint-map`
- Verify the response kind is `tacitus.dialectica.praxis_context.v1`.

## Future Improvements

- Add schema compatibility tests between YAML, Python Pydantic models,
  Databricks Delta tables, and GraphOps TypeScript responses.
- Add ontology diff UI for dynamic custom concepts.
- Add graph writeback for `ReviewDecision`, `BenchmarkRun`, and
  `AnswerConstraint`.
