# Graph Reasoning Subsystem Plan

Last updated: 2026-05-03

## Current State

Dialectica is a monorepo with three relevant graph paths:

- `packages/api`: FastAPI service with `/health`, workspace-scoped graph routes, extraction routes, and reasoning routes. It already binds to `PORT` through container command defaults and is deployable on Cloud Run.
- `packages/graph`: async graph abstraction with Neo4j, Spanner, and FalkorDB clients. Neo4j is the default configured backend.
- `packages/extraction`: LangGraph-style extraction pipeline that validates `dialectica_ontology` nodes and can batch upsert to a graph client, but the public extraction endpoint mostly queues Pub/Sub and falls back to synchronous extraction when Pub/Sub is unavailable.
- `dialectica/`: older TACITUS core v1 ingestion CLI with stronger provenance primitives (`SourceDocument`, `SourceChunk`, `EvidenceSpan`, `ExtractionRun`, `Claim`, `Constraint`, `Leverage`, `Commitment`) and a simple Neo4j adapter using `TacitusCoreV1` labels.
- `apps/web`: Next.js GraphOps routes that can ingest local/sample text and persist local runs, with optional Neo4j/Databricks handoff.
- Infrastructure includes Dockerfiles, Cloud Run YAML, Terraform, local Docker Compose with Neo4j, Redis, PostgreSQL, Qdrant, and optional Spanner/FalkorDB.
- `packages/api/src/dialectica_api/database`: SQLModel metadata layer that now also stores durable graph reasoning pipeline runs, chunks, ontology profile plans, graph object mirrors, and graph edge mirrors. SQLite is supported locally; Cloud SQL PostgreSQL is the production target.

The existing ontology package has `Actor`, `Interest`, `Event`, `Narrative`, and `Evidence`, but not first-class `Claim`, `Constraint`, `Leverage`, `Commitment`, or `Source` in ACO v2. The legacy TACITUS core v1 models do contain those concepts with provenance requirements.

## Integration Points

- Add optional Python package path `app/graph_reasoning/` at repo root.
- Add FastAPI router `packages/api/src/dialectica_api/routers/graph_reasoning.py`.
- Register the router from `dialectica_api.main.create_app()`.
- Extend existing `/health` with graph reasoning checks instead of replacing the existing health route.
- Reuse the configured Neo4j instance via `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE`.
- Keep Cozo as a mirror/cache only. Neo4j remains the source of truth.
- Use Cloud SQL as the durable ingestion audit/control plane, not as the graph
  source of truth.
- Preserve Databricks as an optional lakehouse accelerator. Large-scale
  ingestion must still run directly through API chunking and Neo4j writes when
  Databricks is unavailable.
- Use a deterministic ingestion adapter for `/ingest/text` so the endpoint writes real graph objects even when LLM extraction dependencies are unavailable.

## Risks

- Graphiti and Cozo are not currently installed in the workspace. The safe initial implementation must run without hard dependency imports and should expose adapter modes clearly in `/health`.
- The existing API has auth middleware on all non-public paths. New unversioned routes should remain protected except `/health`.
- Existing `packages/extraction` does not persist through `write_to_graph_async` in the public route path today. The graph reasoning endpoint should own its own transaction flow.
- Current Neo4j graph schemas differ between ACO v2 (`ConflictNode`) and legacy TACITUS core v1 (`TacitusCoreV1`). The subsystem should use separate labels (`GraphReasoningObject`) to avoid corrupting either schema.
- Running more than one Cloud Run worker means any in-process Cozo mirror is per-process. It must be treated as rebuildable cache, never primary state.
- Cloud SQL is durable but not zero-cost. Cloud Run can cold start at zero; Cloud
  SQL should be the single consolidated PostgreSQL instance and may be stopped
  only in environments that can tolerate paused metadata writes/run history.

## Cloud Run Constraints

- Backend must be stateless: no required local persistent disk.
- Neo4j must be external: Aura or an existing reachable Neo4j service.
- Cozo local mode is acceptable for dev, but Cloud Run must be safe if the mirror starts empty.
- Optional snapshot mode can use GCS; the service still functions without it by mirroring new writes and reading source-of-truth data from Neo4j when needed.
- Cloud SQL must be attached through the Cloud SQL Unix socket and `DATABASE_URL`
  Secret Manager value in Cloud Run. No local SQLite file is acceptable for
  production durability.
- Use `PORT` in deployment commands. Existing Dockerfiles currently hardcode `8080`; update to use shell expansion for Cloud Run compatibility.
- `/health` must not require auth and must report Neo4j, Graphiti adapter, and Cozo mirror status.

## Implementation Plan

1. Create `app/graph_reasoning/` modules:
   - `schema.py`: ontology models with stable hash IDs, source IDs, timestamps, confidence, validity windows, and edge provenance.
   - `neo4j_client.py`: source-of-truth writes, schema initialization, search, actor fetch, change queries.
   - `graphiti_client.py`: native Graphiti adapter when installed, with Neo4j episode/provenance compatibility mode when not.
   - `cozo_client.py`: Datalog-style relation mirror API with in-memory fallback and optional embedded Cozo hook.
   - `reasoning_queries.py`: actor profile, indirect constraints, leverage map, provenance trace, timeline, changed-since.
   - `ingestion_adapter.py`: deterministic text-to-object adapter that never emits orphan objects and always creates `Source`/`Evidence`.
   - `sync_service.py`: idempotent orchestration across Graphiti, Neo4j, and Cozo with partial failure logging.
2. Add unversioned routes:
   - `POST /ingest/text`
   - `GET /graph/actor/{id}`
   - `GET /graph/search?q=`
   - `GET /reasoning/actor/{id}`
   - `GET /reasoning/constraints/{id}`
   - `GET /reasoning/leverage/{id}`
   - `GET /reasoning/timeline`
   - `GET /reasoning/changed-since`
   - `GET /reasoning/provenance/{id}`
3. Add tests covering schema validation, deduplication, Neo4j/Graphiti/Cozo adapter behavior, reasoning queries, API endpoints, and unavailable backend behavior.
4. Update deployment docs and Dockerfiles so the root `app/` package is available in the API container.

## Self-Audit Log

### Pass 1: Architecture Sanity

Completed. The subsystem is additive and uses separate `GraphReasoningObject`
and `GraphReasoningEpisode` labels, so it does not rewrite existing ACO v2 or
TACITUS core v1 graph data. Cloud Run remains stateless: Neo4j is durable,
Graphiti compatibility records live in Neo4j, and Cozo is a rebuildable mirror.

### Pass 2: Backend Correctness

Completed. Ingestion is deterministic and idempotent by SHA-256 source hash.
Every emitted object and edge has `source_ids`, `confidence`, `created_at`, and
validity fields. Edges are written only after endpoint nodes are upserted, so
the subsystem does not intentionally create orphan graph objects.

### Pass 3: Test Coverage

Completed initial coverage in `packages/api/tests/test_graph_reasoning.py`:
ontology provenance validation, ingestion writes, deduplication, Graphiti call
path, Cozo mirror writes, reasoning queries, API endpoints, changed-since, and
Neo4j-unavailable failure mode.

### Pass 4: Security and Env Audit

Completed. New unversioned graph reasoning routes inherit existing API-key auth
middleware. `/health` remains public. No secrets are hardcoded. New env vars are
documented in `.env.example` and deployment docs.

### Pass 5: Product Sanity

Completed with limitations. Provenance and temporality are preserved in every
object and edge. `graphiti-core` and `cozo-embedded` are installed for the API
package. Graphiti still defaults to compatibility mode until native LLM/embedder
credentials are configured; Cozo embedded is enabled through `COZO_USE_EMBEDDED`
and remains a rebuildable mirror, not a source of truth.

### Pass 6: Native Graphiti/Cozo Enablement

Completed. The API package now includes native Graphiti and embedded Cozo
dependencies. Cozo uses `cozo_embedded.CozoDbPy` and creates the Datalog-style
relations `actor`, `claim`, `constraint`, `leverage`, `commitment`, `event`,
`narrative`, `source`, `evidence`, and `edge`. Cloud Run guidance keeps Cozo in
`mem` mode unless a snapshot hydrate/flush flow is explicitly added.

### Pass 7: Cloud SQL and Dynamic Pipeline Consolidation

Completed. `DATABASE_URL` now drives a durable SQLModel audit store with
pipeline runs, pre-ingestion source chunks, dynamic ontology profile records,
and graph object/edge mirrors. `/ingest/text` accepts `objective` and
`ontology_profile`, builds a dynamic ontology plan, chunks large sources before
graph writes, writes Graphiti/Neo4j/Cozo, and records the full run in Cloud SQL.
GraphOps now sends the active objective/profile and displays `/pipeline/runs`.
This keeps Databricks optional: batch/lakehouse jobs can consume the same
metadata later, but direct API ingestion still works without Databricks.

### Pass 8: Graphify Audit Baseline

Completed. The optional subsystem now has a scoped graphify artifact at
`app/graph_reasoning/graphify-out/`:

- `GRAPH_REPORT.md` summarizes graph-reasoning subsystem communities, god
  nodes, and knowledge gaps.
- `graph.html` provides the interactive local graph visualization.
- `graph.json` is force-added despite the repository-wide `*.json` ignore rule
  because it is the GraphRAG-ready graphify data artifact for this subsystem.

The full repository was intentionally not graphified in this commit: detection
found more than 500 supported files, which would produce a noisy graph and
include broad documentation areas unrelated to this subsystem. The committed
artifact is scoped to `app/graph_reasoning` so it remains reviewable.
