# DIALECTICA by TACITUS — Claude Code Project Guide

## What this is
DIALECTICA is the core neurosymbolic conflict intelligence engine for TACITUS (tacitus.me).
It transforms unstructured conflict data into structured knowledge graphs using the
Conflict Grammar ontology (15 node types, 20 edge types, 25+ controlled vocabularies)
and delivers reasoning-backed decision support grounded in 15 conflict resolution theories.

Two domains: human friction (HR disputes, commercial mediation) and warfare/political
conflict (JCPOA-type geopolitical analysis, UN Security Council dynamics).

## Architecture (4 layers)
1. **Neural Ingestion**: GLiNER NER pre-filter -> Gemini 2.5 Flash structured extraction -> Pydantic v2 validation
2. **Symbolic Representation**: Conflict Grammar graph stored in Neo4j Aura (primary) + FalkorDB (tenant layer)
3. **Reasoning & Inference**: 25+ deterministic symbolic rules fire FIRST -> GNN/KGE neural fills gaps -> human validates
4. **Decision Support**: 6 AI agents (Analyst, Advisor, Comparator, Forecaster, Mediator, Theorist) + MCP server

## Critical invariant
Deterministic symbolic conclusions (treaty violations, legal constraints, Glasl stage derivations)
are NEVER overridden by probabilistic neural predictions. Enforced via confidence_type tagging:
"deterministic" (from symbolic rules) vs "probabilistic" (from GNN/LLM).

## Package dependency graph
```
ontology -> graph -> extraction -> reasoning -> api
                                                 ^
                                             apps/web (Next.js)
                                             packages/mcp (MCP server)
                                             packages/sdk-typescript (TS SDK)

Cross-cutting concerns:
  ontology/subdomains.py    — knowledge cluster detection (used by extraction + reasoning)
  api/analytics.py          — BigQuery event logging (used by api routers)
  reasoning/databricks.py   — Databricks ML connector (used by reasoning + api)
  api/routers/integration.py — TACITUS integration layer (used by external TACITUS apps)
```

## Tech stack
- **Python 3.12+**, UV workspaces, Pydantic v2 with StrEnum + discriminated unions
- **FastAPI** (async), LangGraph pipeline orchestration, 14 routers
- **Neo4j Aura** (primary graph DB — TACITUS is in Neo4j Startup Program)
- FalkorDB (tenant isolation, dev/test), Spanner (optional GCP alternative)
- Qdrant (vector search, named vectors for KGE + semantic embeddings)
- **Next.js 15** + React 19 + Tailwind + D3.js (force-directed graphs)
- **Google Cloud**: Cloud Run (API), Vertex AI, Secret Manager, Artifact Registry
- Gemini 2.5 Flash (extraction), Gemini 2.5 Pro (synthesis)

## Optional heavy dependencies
These are NOT installed by default. The codebase works without them:
- `pip install dialectica-reasoning[kge]` — torch, torch-geometric, pykeen, leidenalg, igraph
- `pip install dialectica-extraction[gliner]` — gliner (~500MB model download)
- Without these, KGE features are disabled and GLiNER falls back to keyword matching

## Conventions
- All code must pass `ruff check` and `ruff format --check`
- Type annotations required on all public functions (mypy strict)
- Tests: pytest with pytest-asyncio, mock external services, never mock business logic
- Commits: conventional commits (feat:, fix:, refactor:, docs:, test:, infra:)
- Env vars: see .env.example for all configuration
- Graph queries: always scope by workspace_id AND tenant_id
- Neo4j is the default backend everywhere (GRAPH_BACKEND=neo4j)

## Knowledge Clusters & Subdomains
DIALECTICA organizes conflict knowledge into 6 subdomains, each with specialized
ontology extensions, extraction prompts, and benchmark expectations:

| Subdomain | Scope | Key node types emphasized |
|-----------|-------|--------------------------|
| `geopolitical` | International relations, treaties, sanctions | Actor (state), Norm (treaty), Event (diplomatic) |
| `workplace` | HR disputes, harassment, organizational conflict | Actor (person), Process (grievance), EmotionalState |
| `commercial` | Contract disputes, IP, business mediation | Actor (organization), Norm (contract), Outcome |
| `legal` | Litigation, regulatory, statutory interpretation | Norm (statute/precedent), Process (adjudication), Evidence |
| `armed` | War, insurgency, UCDP-classified conflict | Event (material_conflict), Location, PowerDynamic |
| `environmental` | Resource disputes, climate conflict, land rights | Issue, Location, Norm (regulation) |

- **KnowledgeClusterDetector** (`packages/ontology/src/dialectica_ontology/subdomains.py`):
  Classifies input text into one or more subdomains using keyword heuristics and
  optional GLiNER entity distribution. Used by the extraction pipeline to select
  subdomain-specific extraction prompts and validation rules.
- Each subdomain defines which ontology tiers, theory frameworks, and symbolic
  rules are most relevant (e.g., armed subdomain prioritizes Galtung + Glasl +
  Kriesberg; workplace prioritizes Thomas-Kilmann + Fisher-Ury + Mayer trust).

## Benchmarking
4 gold-standard corpora for evaluating extraction pipeline accuracy:

| Corpus | Domain | Entities | Edges |
|--------|--------|----------|-------|
| `jcpoa` | Geopolitical / treaty | ~25 | ~30 |
| `romeo_juliet` | Interpersonal / literary | ~15 | ~20 |
| `crime_punishment` | Psychological / literary | ~18 | ~22 |
| `war_peace` | Armed conflict / literary | ~20 | ~25 |

- **Run benchmarks**: `POST /v1/admin/benchmark/run` with `{"corpus_id":"jcpoa","tier":"standard"}`
- **Make target**: `make benchmark` (runs JCPOA against live API)
- **Test suite**: `make test-benchmark` (runs `packages/api/tests/test_benchmark.py`)
- **Frontend dashboard**: `/admin/benchmarks` — run benchmarks, view results, trend charts
- **Metrics**: entity F1/precision/recall, relationship F1, hallucination rate
- **Custom corpora**: Add JSON to `data/seed/samples/` with a `gold_standard` key (see `docs/benchmarking.md`)

## BigQuery Analytics
Optional analytics pipeline that logs extraction, query, and benchmark events to
BigQuery for longitudinal analysis.

- **3 tables** in `dialectica_analytics` dataset:
  - `extraction_events` — every pipeline run (workspace, corpus, tier, entity/edge counts, duration)
  - `query_events` — every reasoning query (workspace, mode, token count, latency)
  - `benchmark_results` — every benchmark run (corpus, tier, F1, hallucination rate)
- **AnalyticsClient**: `packages/api/src/dialectica_api/analytics.py`
  - `log_extraction_event()`, `log_query_event()`, `log_benchmark_result()`
  - Enabled via `BIGQUERY_ENABLED=true` + `BIGQUERY_DATASET=dialectica_analytics`
  - No-ops gracefully when disabled
- Terraform provisions the BigQuery dataset and tables (`infrastructure/terraform/`)

## Databricks Integration
Optional connector for running KGE (Knowledge Graph Embedding) training and
advanced ML on Databricks.

- **DatabricksConnector**: `packages/reasoning/src/dialectica_reasoning/databricks.py`
  - `export_graph(workspace_id)` — export conflict graph as Spark DataFrame
  - `train_kge(workspace_id, model)` — train RotatE/TransE on exported graph
  - `get_predictions(workspace_id)` — retrieve link predictions back into reasoning
- **Configuration**: `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_CLUSTER_ID`
- Requires `pip install dialectica-reasoning[kge]` for local KGE; Databricks
  provides its own Spark + PyTorch environment
- Falls back gracefully when Databricks is not configured

## TACITUS Integration API
3 endpoints that allow other TACITUS platform applications (e.g., trust graph,
context layer, mediation tools) to interact with DIALECTICA:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/integration/graph` | POST | Push/pull conflict graphs between TACITUS apps |
| `/v1/integration/context` | GET | Retrieve workspace context (actors, conflicts, timelines) |
| `/v1/integration/query` | POST | Execute reasoning queries from other TACITUS apps |

- **Router**: `packages/api/src/dialectica_api/routers/integration.py`
- Authenticated via standard API key with `integration` level
- Supports workspace-scoped data exchange with tenant isolation
- DIALECTICA serves as the trust graph and context layer for the broader TACITUS platform

## Key file locations
- **Ontology models**: packages/ontology/src/dialectica_ontology/primitives.py (15 node types)
- **Relationships**: packages/ontology/src/dialectica_ontology/relationships.py (20 edge types)
- **Enums**: packages/ontology/src/dialectica_ontology/enums.py (39 StrEnum types)
- **Symbolic rules**: packages/ontology/src/dialectica_ontology/symbolic_rules.py (25+ rules, RuleEngine)
- **Neurosymbolic config**: packages/ontology/src/dialectica_ontology/neurosymbolic.py (4-layer architecture)
- **Theory frameworks**: packages/ontology/src/dialectica_ontology/theory/ (15 modules)
- **Graph interface**: packages/graph/src/dialectica_graph/interface.py (abstract GraphClient)
- **Neo4j client**: packages/graph/src/dialectica_graph/neo4j_client.py
- **Extraction pipeline**: packages/extraction/src/dialectica_extraction/pipeline.py (10-step LangGraph DAG)
- **GLiNER pre-filter**: packages/extraction/src/dialectica_extraction/gliner_ner.py
- **Reasoning symbolic/**: packages/reasoning/src/dialectica_reasoning/symbolic/ (escalation, ripeness, trust, power, firewall)
- **AI agents**: packages/reasoning/src/dialectica_reasoning/agents/ (6 agents)
- **API entry**: packages/api/src/dialectica_api/main.py (FastAPI app factory)
- **API config**: packages/api/src/dialectica_api/config.py (Settings with env var defaults)
- **Health endpoint**: packages/api/src/dialectica_api/routers/health.py (/health, /health/live, /health/ready)
- **Waitlist endpoint**: packages/api/src/dialectica_api/routers/waitlist.py (public, no auth)
- **MCP server**: packages/mcp/src/dialectica_mcp/server.py (5 tools for Claude)
- **Seed data**: data/seed/samples/ (6 JSON files, 114 nodes, 126 edges)
- **Seed script**: infrastructure/scripts/seed_sample_data.py (async, both JSON formats)
- **Deploy script**: infrastructure/scripts/deploy-cloudrun.sh
- **Secrets setup**: infrastructure/scripts/setup-secrets.sh
- **Demo page**: apps/web/src/app/demo/page.tsx (paste-and-see with ForceGraph)
- **Investor demo**: apps/web/src/app/demo/investor/page.tsx (5-step guided walkthrough)
- **Landing page**: apps/web/src/app/page.tsx (marketing, no auth)
- **Subdomains**: packages/ontology/src/dialectica_ontology/subdomains.py (6 subdomains, KnowledgeClusterDetector)
- **Benchmark router**: packages/api/src/dialectica_api/routers/benchmark.py (POST /v1/admin/benchmark/run)
- **Benchmark dashboard**: apps/web/src/app/admin/benchmarks/page.tsx (frontend UI)
- **Analytics client**: packages/api/src/dialectica_api/analytics.py (BigQuery AnalyticsClient)
- **Databricks connector**: packages/reasoning/src/dialectica_reasoning/databricks.py (DatabricksConnector)
- **Integration router**: packages/api/src/dialectica_api/routers/integration.py (TACITUS integration)
- **Production runbook**: docs/runbook.md (step-by-step deployment guide)
- **Benchmarking guide**: docs/benchmarking.md (corpora, metrics, custom gold standards)

## Running locally

### Minimal (recommended for development)
```bash
cp .env.example .env          # edit Neo4j credentials if needed
make dev-local                # docker-compose.local.yml: Neo4j + Redis + API
make seed                     # load 6 sample conflict graphs into Neo4j
# API: http://localhost:8080/docs
# Neo4j Browser: http://localhost:7474
```

### Frontend
```bash
cd apps/web && npm install && npm run dev
# http://localhost:3000
# http://localhost:3000/demo (paste-and-see demo)
# http://localhost:3000/demo/investor (guided investor walkthrough)
```

### Full stack (all services)
```bash
make dev                      # docker-compose.yml: Neo4j + Redis + API + Web + Qdrant + FalkorDB + MCP
```

## Testing (596 tests total)
```bash
make test                     # all Python tests
make test-ontology            # 420 tests, 80% coverage (enums, primitives, relationships, tiers, symbolic rules, neurosymbolic, theories)
make test-api                 # 72 tests (health, workspaces, entities, extraction, graph, reasoning, theory, admin, auth, tenant isolation)
make test-extraction          # 75 tests (pipeline chunking, GLiNER fallback, density calculation)
make test-reasoning           # 29 tests (escalation, ripeness, trust, firewall, power, KGE availability)
make test-e2e                 # Playwright E2E (demo journey, landing page, sample texts)
make lint                     # ruff check + format check
make quality-all              # lint + typecheck + tsc + web-lint
```

## Deploying

### API to Cloud Run
```bash
# 1. Store Neo4j Aura credentials in GCP Secret Manager (one-time)
make setup-secrets            # interactive: prompts for Neo4j URI, user, password

# 2. Deploy
make deploy                   # builds, pushes, deploys to Cloud Run
# Or manually:
bash infrastructure/scripts/deploy-cloudrun.sh YOUR_GCP_PROJECT_ID us-east1
```

### Frontend to Vercel
```bash
cd apps/web
npx vercel --prod
# Set env var: NEXT_PUBLIC_API_URL = your Cloud Run URL
```

### Docker image only (no deploy)
```bash
docker build -f packages/api/Dockerfile.cloudrun -t dialectica-api .
# Image should be < 500MB (no torch/gliner)
```

## Common tasks
- Add new node type: primitives.py -> enums.py -> relationships.py -> tiers.py -> tests
- Add symbolic rule: symbolic_rules.py -> register in _DEFAULT_RULES -> add test
- Add API endpoint: routers/ -> register in main.py -> add to _PUBLIC_PATHS if unauthenticated -> test
- Add seed data: data/seed/samples/new_scenario.json (use nodes/edges or actors/events format)
- Add benchmark corpus: data/seed/samples/new_corpus.json (add `gold_standard` key, see docs/benchmarking.md)
- Add subdomain: subdomains.py -> add to SubdomainType enum + SUBDOMAIN_KEYWORDS + SUBDOMAIN_THEORIES
- Run production deploy: follow docs/runbook.md step by step
- Publish ontology: `cd packages/ontology && uv build && twine upload dist/*`
