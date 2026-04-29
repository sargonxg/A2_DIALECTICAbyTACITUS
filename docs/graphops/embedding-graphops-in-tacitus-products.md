# Embedding GraphOps in TACITUS Products

GraphOps should behave like a reusable TACITUS service, not only a standalone
website. Other products, including Praxis, can treat DIALECTICA as the
neurosymbolic graph layer for understanding situations.

## Runtime Contract

Protected manifest:

```text
GET /api/graphops/manifest
```

The manifest exposes:

- available source packs,
- ontology profiles,
- graph categories,
- quality gates,
- Databricks workflow endpoints,
- Neo4j query endpoint,
- embeddable product surfaces,
- event names for future Pub/Sub orchestration,
- readiness flags for Databricks and Neo4j.

## Product Integration Flow

1. Product creates or selects `tenant_id`, `workspace_id`, `project_id`, and
   `situation_id`.
2. Product sends source metadata and user objective to GraphOps.
3. GraphOps selects or generates an ontology profile.
4. Product triggers the relevant Databricks workflow.
5. Databricks writes Delta candidates and quality tables.
6. Accepted graph facts write to Neo4j after production Neo4j secrets are
   configured.
7. Product asks graph-grounded questions with workspace-scoped retrieval.
8. Product displays provenance, confidence, uncertainty, and review state.

## Praxis Example

Praxis sends:

```json
{
  "workspace_id": "praxis-team-friction-001",
  "objective": "understand commitments, trust injuries, contested scope, and repair options",
  "source_type": "meeting notes and messages",
  "user_role": "team lead",
  "question_type": "what happened and what should I ask next?"
}
```

GraphOps returns:

- active ontology profile: `human-friction + mediation-resolution`,
- required labels: `Actor`, `Issue`, `Interest`, `TrustState`,
  `PowerDynamic`, `Process`, `Claim`,
- review gates: evidence grounding, commitment ambiguity, source sensitivity,
- outputs: commitment ledger, trust repair brief, next-best questions, graph
  context for GraphRAG.

## Production Requirements

- Replace Basic Auth with product-to-product service auth.
- Add workspace-scoped authorization.
- Add `graph_version`, `source_pack_version`, `ontology_profile_version`, and
  `prompt_version` to every run.
- Rotate and configure Neo4j credentials before enabling graph writeback.
- Keep inferred facts, user assertions, source claims, and verified facts
  visibly separate.
