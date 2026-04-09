# DIALECTICA Architecture

## Overview

DIALECTICA is the universal data layer for human friction — a neurosymbolic
conflict intelligence platform that transforms unstructured documents into
structured knowledge graphs and delivers reasoning-backed decision support.
The system follows a four-layer pipeline: **document ingestion** (GLiNER
pre-filtering + Gemini extraction), **symbolic representation** (Conflict
Grammar ontology stored in Spanner Graph / Neo4j), **reasoning and inference**
(deterministic symbolic rules fire first, then probabilistic neural components
fill gaps via GraphRAG and GNN embeddings), and **decision support** (AI agents
surface options, risks, and competing interpretations for human decision-makers).
Deterministic conclusions are never overridden by probabilistic inference — this
is the inviolable architectural principle.

---

## System Architecture (Four Layers)

Defined in `packages/ontology/src/dialectica_ontology/neurosymbolic.py` as the
`NeurosymbolicArchitecture` Pydantic model.

### Layer 1 — Neural Ingestion

Extract actors, claims, events, sentiments, commitments, threats, concessions,
timelines, and uncertainty from messy text using the ontology as an extraction
schema. Each extraction carries a confidence score.

- **GLiNER** pre-filters chunks for entity density (prioritizes entity-rich
  passages).
- **Gemini Flash** performs tier-appropriate structured extraction.
- **Pydantic v2** validates every extracted node against the ontology schema.

### Layer 2 — Symbolic Representation

Encode extracted entities into the Conflict Grammar graph with typed relations,
controlled vocabularies, and temporal metadata.

- 15 node types, 20 edge types, 39 enums.
- Three-tier progressive disclosure: Essential (7 nodes / 6 edges), Standard
  (12 / 13), Full (15 / 20).
- Dual-backend graph storage: Spanner Graph (primary) + Neo4j (secondary).

### Layer 3 — Reasoning and Inference

Contradiction checks, commitment tracking, escalation pattern detection,
argument maps, procedural rules, causal hypotheses. Deterministic rules fire
first; neural GNN predictions fill gaps second.

- **9 symbolic components** (see below).
- **7 neural components**: R-GAT, RotatE, temporal attention, narrative
  similarity, conflict pattern matching, escalation prediction, outcome
  prediction.
- **reason-then-embed** bridge protocol: symbolic rules fire -> neural layer
  fills gaps -> human validates -> validated suggestions become new rules.

### Layer 4 — Decision Support

Surface options, risks, missing evidence, and competing interpretations for
human decision-makers. Human validation promotes neural suggestions to new
symbolic rules (learning loop). TACITUS is decision-support, not autonomous
resolution.

- 6 AI agents: Analyst, Advisor, Comparator, Forecaster, Mediator, Theorist.
- SSE streaming for real-time reasoning traces.
- Hallucination detection on every synthesis.

---

## Dependency Graph

```
ontology  <--  graph  <--  extraction  <--  reasoning  <--  api
                                                             ^
                                                             |
                                                         apps/web (via HTTP)

Cross-cutting:
  ontology/subdomains.py      -- knowledge cluster detection (extraction + reasoning)
  api/analytics.py            -- BigQuery event logging (all api routers)
  reasoning/databricks.py     -- Databricks ML connector (reasoning + api)
  api/routers/integration.py  -- TACITUS integration layer (external apps)
```

All Python packages are installed as editable packages (`pip install -e`).
The web frontend communicates with the API exclusively over HTTP.

---

## Package Map

| Package | Role | Key Entry Point | Lines |
|---------|------|-----------------|------:|
| `packages/ontology` | Conflict Grammar: nodes, edges, enums, tiers, theories, compatibility | `primitives.py`, `relationships.py`, `neurosymbolic.py` | ~8 100 |
| `packages/graph` | Dual-backend graph database abstraction | `interface.py` (ABC), `spanner.py`, `neo4j.py` | ~2 700 |
| `packages/extraction` | 10-step LangGraph extraction pipeline | `pipeline.py`, `gliner_ner.py`, `gemini.py` | ~2 650 |
| `packages/reasoning` | Symbolic rules, GraphRAG, agents, hallucination detection | `query_engine.py`, `symbolic/`, `agents/`, `graphrag/` | ~4 400 |
| `packages/api` | FastAPI service (routers, middleware, config) | `main.py` | ~1 750 |
| `apps/web` | Next.js 14 frontend | `app/` | — |

---

## Data Flow

End-to-end path from document upload to analytical results:

```
  Document Upload
       |
       v
  1. chunk_document         Split into 2 000-char overlapping chunks
       |                    (sentence-boundary aware, 200-char overlap)
       v
  2. gliner_prefilter       GLiNER NER scores entity density per chunk
       |
       v
  3. extract_entities       Gemini Flash extracts typed entities per tier
       |
       v
  4. validate_schema        Pydantic v2 validates against ConflictNode models
       |
       v  (conditional)
  5. repair_extraction      Send validation errors back to Gemini (max 3 retries)
       |
       v
  6. extract_relationships  Gemini extracts edges between validated nodes
       |
       v
  7. resolve_coreference    Cross-chunk entity merging + alias matching
       |
       v
  8. validate_structural    Conflict Grammar structural rules + temporal +
       |                    symbolic validation; relationship scoring
       v
  9. compute_embeddings     Vertex AI text-embedding-005 (768-dim)
       |
       v
  10. write_to_graph        Batch upsert nodes and edges to graph database
       |
       v
  Query Engine
       |
       v
  GraphRAG retrieval  ->  Symbolic analysis  ->  LLM synthesis  ->  Response
  (vector + traverse)     (9 rule modules)       (Gemini Pro)       (with citations)
```

Pipeline defined in `packages/extraction/src/dialectica_extraction/pipeline.py`.
Built as a LangGraph `StateGraph` with conditional edges (validate -> repair
loop). Falls back to sequential execution if LangGraph is unavailable.

### Four-Layer Validation

1. **Schema validation** — Pydantic v2 model parsing against `ConflictNode`
   subclasses (`validators/schema.py`).
2. **Structural validation** — Conflict Grammar rules: required relations,
   valid source/target label constraints (`validators/structural.py`).
3. **Temporal validation** — Allen's interval algebra on `valid_from` /
   `valid_to` fields (`validators/temporal.py`).
4. **Symbolic validation** — Domain-specific rule checks, e.g. Glasl stage
   consistency, UCDP thresholds (`validators/symbolic.py`).

---

## Ontology (ACO v2.0)

TACITUS Core Ontology v2.0 — the Conflict Grammar.

### 15 Node Types

Defined in `packages/ontology/src/dialectica_ontology/primitives.py`. All
inherit from `ConflictNode` (ULID IDs, tenant/workspace scoping, confidence
scores, optional 128/768-dim embeddings).

| # | Node | Theoretical Basis |
|---|------|-------------------|
| 1 | `Actor` | CAMEO/ACLED actor coding + Fisher/Ury |
| 2 | `Conflict` | UCDP incompatibility + Galtung ABC + Glasl + Kriesberg |
| 3 | `Event` | PLOVER event-mode-context + ACLED taxonomy |
| 4 | `Issue` | UCDP incompatibility + Fisher/Ury |
| 5 | `Interest` | Fisher/Ury "Getting to Yes" + Rothman identity |
| 6 | `Norm` | LKIF + CLO + Fisher/Ury objective criteria |
| 7 | `Process` | Ury/Brett/Goldberg + ADR + Glasl intervention |
| 8 | `Outcome` | Mnookin "Beyond Winning" + ADR outcomes |
| 9 | `Narrative` | Winslade & Monk + Sara Cobb + Dewulf + Lakoff |
| 10 | `EmotionalState` | Plutchik wheel + Smith & Ellsworth appraisal |
| 11 | `TrustState` | Mayer/Davis/Schoorman integrative model |
| 12 | `PowerDynamic` | French & Raven 5 bases + Ury/Brett/Goldberg |
| 13 | `Location` | ACLED/UCDP spatial coding |
| 14 | `Evidence` | Legal evidence law + ACLED source methodology |
| 15 | `Role` | SEM (Simple Event Model) role reification |

### 20 Edge Types

Defined in `packages/ontology/src/dialectica_ontology/relationships.py` as
`EdgeType(StrEnum)`:

`PARTY_TO`, `PARTICIPATES_IN`, `HAS_INTEREST`, `PART_OF`, `CAUSED`,
`AT_LOCATION`, `WITHIN`, `ALLIED_WITH`, `OPPOSED_TO`, `HAS_POWER_OVER`,
`MEMBER_OF`, `GOVERNED_BY`, `VIOLATES`, `RESOLVED_THROUGH`, `PRODUCES`,
`EXPERIENCES`, `TRUSTS`, `PROMOTES`, `ABOUT`, `EVIDENCED_BY`.

Each edge has a schema specifying valid source/target labels and
required/optional properties.

### 39 Enums

Defined in `packages/ontology/src/dialectica_ontology/enums.py`. Cover actor
types, conflict scales/domains/statuses, event types/modes/contexts, Glasl
stages and levels, Kriesberg phases, emotion intensities, trust bases, power
domains, and more.

### 3 Tiers

Defined in `packages/ontology/src/dialectica_ontology/tiers.py`:

| Tier | Nodes | Edges | Purpose |
|------|------:|------:|---------|
| Essential | 7 | 6 | Quick conflict mapping |
| Standard | 12 | 13 | Structured analysis |
| Full | 15 | 20 | Complete neurosymbolic intelligence |

### 16 Theory Modules

Located in `packages/ontology/src/dialectica_ontology/theory/`:

`burton`, `deutsch`, `fisher_ury`, `french_raven`, `galtung`, `glasl`,
`kriesberg`, `lederach`, `mayer_trust`, `pearl_causal`, `plutchik`,
`thomas_kilmann`, `ury_brett_goldberg`, `winslade_monk`, `zartman`, `base`.

### 4 Compatibility Mappers

Located in `packages/ontology/src/dialectica_ontology/compatibility/`:

`acled.py`, `cameo.py`, `plover.py`, `ucdp.py` — map external conflict data
standards into the DIALECTICA ontology.

---

## Graph Database

### Abstract Interface

Defined in `packages/graph/src/dialectica_graph/interface.py` as
`GraphClient(ABC)`. All methods are async. All operations are scoped by
`workspace_id` + `tenant_id` for multi-tenancy.

Key operations:
- **Node CRUD**: `upsert_node`, `delete_node`, `get_node`, `get_nodes`
- **Edge CRUD**: `upsert_edge`, `get_edges`
- **Traversal**: `traverse` (N-hop subgraph from a starting node)
- **Vector search**: `vector_search` (cosine distance on embeddings)
- **Raw query**: `execute_query` (GQL for Spanner, Cypher for Neo4j)
- **Analytics**: `get_workspace_stats`, `get_actor_network`, `get_timeline`,
  `get_escalation_trajectory`
- **Batch**: `batch_upsert_nodes`, `batch_upsert_edges`

### Dual Backend

| Backend | Role | Query Language | Config |
|---------|------|----------------|--------|
| **Google Cloud Spanner Graph** | Primary | GQL + SQL + vector search | Enterprise, 100 PU, us-east1 |
| **Neo4j** | Secondary (optional) | Cypher + APOC | 5-community, Bolt 7687 |

Backend selection via `GRAPH_BACKEND` env var (`spanner` or `neo4j`).

### Multi-Tenancy

Every node and edge carries `tenant_id` and `workspace_id`. All graph queries
filter by these fields. The `TenantMiddleware` in the API layer injects tenant
context from the authenticated API key.

### Vector Search

Native 768-dim vector index on Spanner (COSINE_DISTANCE). Embeddings generated
by Vertex AI `text-embedding-005`. Nodes of type Actor, Conflict, Event, and
Narrative receive learned embeddings (recommended dim: 128 for GNN, 768 for
semantic search).

---

## Extraction Pipeline

### 10-Step LangGraph DAG

Defined in `packages/extraction/src/dialectica_extraction/pipeline.py`.

| Step | Function | Description |
|------|----------|-------------|
| 1 | `chunk_document` | Split text into 2 000-char overlapping chunks |
| 2 | `gliner_prefilter` | GLiNER NER scores entity density per chunk |
| 3 | `extract_entities` | Gemini Flash structured extraction by tier |
| 4 | `validate_schema` | Pydantic v2 validation against `ConflictNode` |
| 5 | `repair_extraction` | Send errors back to Gemini (max 3 retries) |
| 6 | `extract_relationships` | Gemini extracts edges between validated nodes |
| 7 | `resolve_coreference` | Cross-chunk entity merging + deduplication |
| 8 | `validate_structural` | Structural + temporal + symbolic validation |
| 9 | `compute_embeddings` | Vertex AI text-embedding-005 (768-dim) |
| 10 | `write_to_graph` | Batch upsert to graph database |

### Conditional Routing

After step 4 (`validate_schema`), a conditional edge routes to:
- `repair_extraction` if there are invalid entities and retries remain.
- `extract_relationships` if all entities are valid or max retries (3) reached.

The repair step loops back to itself until entities validate or retries exhaust.

### Models Used

| Model | Purpose | Package |
|-------|---------|---------|
| GLiNER medium v2.5 | Entity pre-filtering (local, ~500 MB) | `extraction` |
| Gemini 2.5 Flash | Entity and relationship extraction | `extraction` |
| Gemini 2.5 Pro | Reasoning synthesis | `reasoning` |
| text-embedding-005 | Semantic embeddings (768-dim) | `extraction` |

---

## Reasoning Engine

### 9 Symbolic Modules

Defined in `packages/ontology/src/dialectica_ontology/neurosymbolic.py`
(`SymbolicLayer`) and implemented in `packages/reasoning/src/dialectica_reasoning/symbolic/`:

| Module | File | Description |
|--------|------|-------------|
| Glasl escalation rules | `escalation.py` | Stage transition triggers + intervention recs |
| Ury/Brett/Goldberg loopback | `constraint_engine.py` | Failed power contest -> return to interests |
| Trust breach detection | `trust_analysis.py` | Integrity drop > 0.3 triggers alert (Mayer/Davis/Schoorman) |
| UCDP conflict classification | `constraint_engine.py` | 25-death threshold, incompatibility typing |
| Temporal logic | `constraint_engine.py` | Allen's interval algebra on valid_from/valid_to |
| Norm violation detection | `constraint_engine.py` | Event -[VIOLATES]-> Norm chain traversal |
| BATNA/ZOPA computation | `constraint_engine.py` | Reservation values -> Zone of Possible Agreement |
| Causal chain analysis | `causal_analysis.py` | Event -[CAUSED]-> Event path traversal |
| Cross-case structural similarity | `pattern_matching.py` | Subgraph isomorphism for pattern recognition |

Additional symbolic modules: `ripeness.py` (Zartman MHS/MEO ripeness scoring),
`power_analysis.py` (French & Raven power mapping), `network_metrics.py`
(centrality and community detection), `inference.py` (OWL-style inference).

### GraphRAG

Located in `packages/reasoning/src/dialectica_reasoning/graphrag/`:
- `retriever.py` — `ConflictGraphRAGRetriever`: vector search + N-hop traversal.
- `context_builder.py` — `ConflictContextBuilder`: assembles retrieved subgraph
  into structured context for LLM synthesis.

### 6 AI Agents

Located in `packages/reasoning/src/dialectica_reasoning/agents/`:

| Agent | File | Role |
|-------|------|------|
| Analyst | `analyst.py` | General conflict analysis |
| Advisor | `advisor.py` | Strategic recommendations |
| Comparator | `comparator.py` | Cross-case comparison |
| Forecaster | `forecaster.py` | Trajectory prediction |
| Mediator | `mediator.py` | Resolution pathway identification |
| Theorist | `theorist.py` | Theory-grounded interpretation |

### Query Engine

`packages/reasoning/src/dialectica_reasoning/query_engine.py` —
`ConflictQueryEngine` orchestrates the full pipeline:

1. **Retrieval** — GraphRAG vector search + hop expansion.
2. **Context building** — Assemble subgraph into structured text.
3. **Symbolic analysis** — Escalation, ripeness, pattern matching, constraint
   rules (mode-dependent).
4. **LLM synthesis** — Gemini Pro generates grounded answer (with fallback to
   symbolic-only summary).
5. **Citations** — Top-10 retrieved nodes with relevance scores.

Supports 7 modes: `general`, `escalation`, `ripeness`, `trust`, `power`,
`causal`, `network`. Streams via `stream_analyze()` as SSE-compatible JSON.

### Hallucination Detection

`packages/reasoning/src/dialectica_reasoning/hallucination_detector.py` — every
synthesis output is checked for hallucination risk. The `AnalysisResponse`
includes a `hallucination_risk` field.

---

## API Layer

### FastAPI Application

Defined in `packages/api/src/dialectica_api/main.py`. Title: "DIALECTICA API",
version 1.0.0.

### 10 Routers

| Router | Prefix | Purpose |
|--------|--------|---------|
| `health` | `/health` | Liveness and readiness probes |
| `workspaces` | `/workspaces` | Workspace CRUD |
| `entities` | `/entities` | Node CRUD |
| `relationships` | `/relationships` | Edge CRUD |
| `extraction` | `/extraction` | Document ingestion pipeline |
| `graph` | `/graph` | Traversal, subgraph, stats |
| `reasoning` | `/reasoning` | Query engine, analysis |
| `theory` | `/theory` | Theory frameworks and mappings |
| `admin` | `/admin` | API key management, system ops |
| `developers` | `/developers` | Developer portal, sandbox |

### 5 Middleware (LIFO Order)

Starlette middleware executes in LIFO order. The `add_middleware` call order in
`main.py` determines execution sequence:

| Order Added | Middleware | Executes | Purpose |
|-------------|-----------|----------|---------|
| 1 (last) | `LoggingMiddleware` | 5th (outermost) | Structured JSON request logging |
| 2 | `UsageMiddleware` | 4th | Track API usage per key |
| 3 | `RateLimitMiddleware` | 3rd | Per-key rate limiting (60/10/20 rpm) |
| 4 | `TenantMiddleware` | 2nd | Inject tenant context from API key |
| 5 (first) | `AuthMiddleware` | 1st (innermost) | API key authentication |

Request flow: Logging -> Usage -> RateLimit -> Tenant -> Auth -> Router.

### CORS

Configured from `CORS_ORIGINS` env var (comma-separated). Defaults:
`http://localhost:3000,https://app.dialectica.tacitus.ai`.

---

## Infrastructure

### GCP Services

| Service | Purpose | Configuration |
|---------|---------|---------------|
| Cloud Spanner | Graph database | Enterprise, 100 PU, us-east1 |
| Vertex AI Gemini 2.5 Flash | Entity extraction | `gemini-2.5-flash-001` |
| Vertex AI Gemini 2.5 Pro | Reasoning synthesis | `gemini-2.5-pro-001` |
| Vertex AI Embeddings | Semantic search | `text-embedding-005`, 768-dim |
| Cloud Run (API) | FastAPI service | 2 CPU, 2 Gi, autoscale |
| Cloud Run (Web) | Next.js app | 1 CPU, 512 Mi, autoscale |
| Cloud Pub/Sub | Async extraction | `dialectica-extraction-requests` + DLQ |
| Cloud Storage | Document uploads | `{project}-dialectica-documents` |
| Secret Manager | Secrets | `ADMIN_API_KEY` |
| Artifact Registry | Docker images | `{region}-docker.pkg.dev/{project}/dialectica` |

### Terraform

Located in `infrastructure/terraform/`. Key resource: `cloud_run.tf` defines
both `dialectica-api` and `dialectica-web` Cloud Run services.

- API: 2 CPU / 2 Gi, startup + liveness probes on `/health:8080`.
- Web: 1 CPU / 512 Mi, `NEXT_PUBLIC_API_URL` points to API service URI.
- Secrets injected via `secret_key_ref` (not environment variables).
- CPU idle enabled, startup CPU boost enabled.

### Docker Compose (Local Development)

Defined in `docker-compose.yml`. Services:

| Service | Image | Port |
|---------|-------|------|
| `spanner-emulator` | `gcr.io/cloud-spanner-emulator/emulator:latest` | 9010 (gRPC), 9020 (REST) |
| `spanner-init` | `python:3.12-slim` (one-shot) | — |
| `api` | Built from `packages/api/Dockerfile` | 8080 |
| `web` | Built from `apps/web/Dockerfile` | 3000 |
| `neo4j` (profile: neo4j) | `neo4j:5-community` | 7474, 7687 |
| `api-neo4j` (profile: neo4j) | Same as api, Neo4j backend | 8081 |

Network: `dialectica-network`. Neo4j activated via `--profile neo4j`.

### CI/CD

**CI** (`.github/workflows/ci.yml`): Triggers on push/PR to `main`/`develop`.

| Job | What It Does |
|-----|-------------|
| `python-lint` | ruff check + ruff format + mypy |
| `python-tests` | pytest with Spanner emulator service container, coverage upload |
| `frontend-lint` | TypeScript type check + Next.js lint |
| `frontend-build` | `npm run build` |
| `docker-build` | Build API + Web images (push only, no publish) |

**Deploy** (`.github/workflows/deploy.yml`): Triggers on push to `main` or
version tags (`v*`).

1. Authenticate via Workload Identity Federation (no service account keys).
2. Build and push images to Artifact Registry.
3. Deploy API to Cloud Run (`--no-allow-unauthenticated`).
4. Deploy Web to Cloud Run (`--allow-unauthenticated`).
5. Post-deployment health check (5 retries, 10 s interval).

---

## Security

### Authentication

- API key authentication via `AuthMiddleware`. Keys validated on every request.
- Admin API key stored in GCP Secret Manager, injected via `secret_key_ref`.
- No hardcoded secrets — `.env.example` contains only placeholder values.
- Production uses Workload Identity Federation for GCP auth (no key files).

### Tenant Isolation

- Every node and edge carries `tenant_id` and `workspace_id`.
- `TenantMiddleware` extracts tenant context from the authenticated API key.
- All graph queries filter by `workspace_id` (enforced at the `GraphClient`
  interface level).

### Rate Limiting

- `RateLimitMiddleware` enforces per-key request limits.
- Default: 60 rpm general, 10 rpm extraction, 20 rpm reasoning.
- Configurable via `RATE_LIMIT_*` environment variables.

### Network

- API Cloud Run service: `--no-allow-unauthenticated` (requires IAM).
- Web Cloud Run service: `--allow-unauthenticated` (public frontend).
- CORS restricted to configured origins.

---

## Scientific Risks and Mitigations

From `neurosymbolic.py` `BridgeProtocol.scientific_risks`:

| Risk | Description | Mitigation |
|------|-------------|------------|
| Ontology loss | Schema too rigid flattens meaningful ambiguity | Controlled vocabularies, confidence scores, preserved `source_text` |
| Extraction error propagation | LLM misreads look authoritative in symbolic layer | Confidence scores, HITL validation, stated/inferred distinction |
| Normative overreach | System identifies strategic efficiency without understanding fairness | TACITUS is decision-support, not autonomous resolution |

---

## Knowledge Clusters and Subdomains

DIALECTICA classifies conflict data into 6 subdomains, each with specialized
extraction prompts, validation rules, and theory framework priorities.

### Subdomain Architecture

```
  Input Text
       |
       v
  KnowledgeClusterDetector    (packages/ontology/.../subdomains.py)
       |
       +--> keyword heuristic scoring
       +--> optional GLiNER entity distribution
       |
       v
  SubdomainClassification
       |
       +--> primary_subdomain: str
       +--> secondary_subdomains: list[str]
       +--> confidence: float
       |
       v
  Extraction Pipeline (selects subdomain-specific prompts)
       |
       v
  Reasoning Engine (prioritises relevant theory frameworks)
```

### 6 Subdomains

| Subdomain | Scope | Priority Theories |
|-----------|-------|-------------------|
| `geopolitical` | International relations, treaties, sanctions, diplomacy | Zartman, Kriesberg, Galtung |
| `workplace` | HR disputes, harassment, organizational conflict | Thomas-Kilmann, Fisher-Ury, Mayer trust |
| `commercial` | Contract disputes, IP, business mediation | Fisher-Ury, Ury-Brett-Goldberg, Deutsch |
| `legal` | Litigation, regulatory, statutory interpretation | Ury-Brett-Goldberg, Fisher-Ury |
| `armed` | War, insurgency, UCDP-classified armed conflict | Galtung, Glasl, Kriesberg, Zartman |
| `environmental` | Resource disputes, climate conflict, land rights | Burton (needs), Lederach, Galtung |

Defined in `packages/ontology/src/dialectica_ontology/subdomains.py`.

---

## BigQuery Analytics Pipeline

Optional analytics layer that logs platform events to BigQuery for longitudinal
analysis, cost tracking, and quality monitoring.

### Data Flow

```
  API Routers
       |
       v
  AnalyticsClient              (packages/api/.../analytics.py)
       |
       +--> log_extraction_event()
       +--> log_query_event()
       +--> log_benchmark_result()
       |
       v
  BigQuery Streaming Insert
       |
       v
  dialectica_analytics dataset
       |
       +--> extraction_events table
       +--> query_events table
       +--> benchmark_results table
```

### Tables

| Table | Key Columns | Purpose |
|-------|-------------|---------|
| `extraction_events` | workspace_id, corpus_id, tier, entity_count, edge_count, duration_ms, timestamp | Track extraction volume and performance |
| `query_events` | workspace_id, query_mode, token_count, latency_ms, timestamp | Track reasoning usage and latency |
| `benchmark_results` | corpus_id, tier, entity_f1, relationship_f1, hallucination_rate, timestamp | Track extraction quality over time |

Configuration: `BIGQUERY_ENABLED=true`, `BIGQUERY_DATASET=dialectica_analytics`.
Provisioned by Terraform (`infrastructure/terraform/`). No-ops gracefully when
disabled.

---

## Databricks ML Pipeline

Optional integration for running Knowledge Graph Embedding (KGE) training and
advanced ML on Databricks clusters.

### Data Flow

```
  Conflict Graph (Neo4j)
       |
       v
  DatabricksConnector.export_graph()    (packages/reasoning/.../databricks.py)
       |
       v
  Databricks Cluster
       |
       +--> Spark DataFrame (nodes + edges)
       +--> KGE Training (RotatE, TransE via PyKEEN)
       +--> Link Prediction
       |
       v
  DatabricksConnector.get_predictions()
       |
       v
  Reasoning Engine (neural gap-filling)
```

The DatabricksConnector supports three operations:
- `export_graph(workspace_id)` -- serialize conflict graph to Spark DataFrame
- `train_kge(workspace_id, model)` -- train KGE model on Databricks cluster
- `get_predictions(workspace_id)` -- retrieve link predictions for neural inference

Configuration: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_CLUSTER_ID`.
Falls back gracefully when not configured.

---

## TACITUS Integration Layer

DIALECTICA serves as the trust graph and context layer for the broader TACITUS
platform (tacitus.me). Other TACITUS applications connect via the integration API.

### Integration Architecture

```
  TACITUS Platform
       |
       +--> Trust Graph App
       +--> Mediation Tools
       +--> Context Layer
       |
       v
  /v1/integration/*              (packages/api/.../routers/integration.py)
       |
       +--> /graph   (POST)  -- push/pull conflict graphs
       +--> /context (GET)   -- retrieve workspace context
       +--> /query   (POST)  -- execute reasoning queries
       |
       v
  DIALECTICA Core
       |
       +--> Graph DB (Neo4j Aura)
       +--> Reasoning Engine
       +--> Extraction Pipeline
```

### Endpoints

| Endpoint | Method | Purpose | Auth Level |
|----------|--------|---------|------------|
| `/v1/integration/graph` | POST | Push/pull conflict graphs between TACITUS apps | integration |
| `/v1/integration/context` | GET | Retrieve actors, conflicts, timelines for a workspace | integration |
| `/v1/integration/query` | POST | Execute cross-app reasoning queries | integration |

All integration endpoints enforce tenant isolation via workspace_id scoping.

---

## Key File Reference

| File | Path |
|------|------|
| Neurosymbolic architecture | `packages/ontology/src/dialectica_ontology/neurosymbolic.py` |
| 15 node primitives | `packages/ontology/src/dialectica_ontology/primitives.py` |
| 20 edge types | `packages/ontology/src/dialectica_ontology/relationships.py` |
| 39 enums | `packages/ontology/src/dialectica_ontology/enums.py` |
| 3 tiers | `packages/ontology/src/dialectica_ontology/tiers.py` |
| 16 theory modules | `packages/ontology/src/dialectica_ontology/theory/` |
| 4 compat mappers | `packages/ontology/src/dialectica_ontology/compatibility/` |
| Graph interface (ABC) | `packages/graph/src/dialectica_graph/interface.py` |
| Extraction pipeline | `packages/extraction/src/dialectica_extraction/pipeline.py` |
| Query engine | `packages/reasoning/src/dialectica_reasoning/query_engine.py` |
| Hallucination detector | `packages/reasoning/src/dialectica_reasoning/hallucination_detector.py` |
| API entry point | `packages/api/src/dialectica_api/main.py` |
| Terraform Cloud Run | `infrastructure/terraform/cloud_run.tf` |
| Docker Compose | `docker-compose.yml` |
| CI workflow | `.github/workflows/ci.yml` |
| Deploy workflow | `.github/workflows/deploy.yml` |
| Env config template | `.env.example` |
| Subdomains / clusters | `packages/ontology/src/dialectica_ontology/subdomains.py` |
| BigQuery analytics client | `packages/api/src/dialectica_api/analytics.py` |
| Databricks connector | `packages/reasoning/src/dialectica_reasoning/databricks.py` |
| TACITUS integration router | `packages/api/src/dialectica_api/routers/integration.py` |
| Benchmark router | `packages/api/src/dialectica_api/routers/benchmark.py` |
| Benchmark dashboard | `apps/web/src/app/admin/benchmarks/page.tsx` |
| Production runbook | `docs/runbook.md` |
| Benchmarking guide | `docs/benchmarking.md` |
