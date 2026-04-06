# DIALECTICA by TACITUS — Claude Code Project Guide

## What this is
DIALECTICA is the core neurosymbolic conflict intelligence engine for TACITUS (tacitus.me).
It transforms unstructured conflict data into structured knowledge graphs using the
Conflict Grammar ontology (15 node types, 20 edge types, 25+ controlled vocabularies)
and delivers reasoning-backed decision support grounded in 15 conflict resolution theories.

**Two specialized domains:**
1. **Human Friction** (micro-meso scale): Interpersonal, workplace, commercial, legal, family, community disputes. Theories: Fisher/Ury, Mayer Trust, Thomas-Kilmann, Deutsch, Plutchik.
2. **Conflict & Warfare** (macro-meta scale): Geopolitical, armed, political, protracted social, insurgency, hybrid warfare. Theories: Glasl, Zartman, Galtung, Azar, Kelman, Kriesberg, Lederach.

Domain specs: `packages/ontology/src/dialectica_ontology/domains.py`

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

## Testing (630+ tests total)
```bash
make test                     # all Python tests
make test-ontology            # 452 tests, 82% coverage (enums, primitives, relationships, tiers, symbolic rules, neurosymbolic, theories, domains, corpus, benchmarks)
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
- Publish ontology: `cd packages/ontology && uv build && twine upload dist/*`

## ConflictCorpus — Core Queryable Entity
The `ConflictCorpus` is the primary unit of analysis in DIALECTICA. Every workspace maps to
one ConflictCorpus. It wraps the conflict knowledge graph with:
- Source document tracking (ingestion provenance, word counts, extraction tier)
- Computed analytics (Glasl stage, ripeness, patterns, clusters, graph density)
- Benchmark scores (F1, precision, recall, hallucination rate)
- Domain classification (human_friction or conflict_warfare)

Location: `packages/ontology/src/dialectica_ontology/corpus.py`

## Knowledge Clusters & Subdomains
Knowledge clusters group related actors/entities within a conflict graph using
Leiden community detection at multiple resolutions. Each cluster is enriched with:
- Subdomain classification (geopolitical, workplace, commercial, legal, armed, environmental)
- Applicable theories (domain-specific theory selection)
- Escalation indicators (domain-specific warning signs)

Locations:
- Subdomain specs: `packages/ontology/src/dialectica_ontology/domains.py`
- Cluster detector: `packages/reasoning/src/dialectica_reasoning/graphrag/knowledge_clusters.py`

## Benchmarking System
4 gold-standard corpora: jcpoa, romeo_juliet, crime_punishment, war_peace
35+ universal benchmark questions organized by domain, theory, mode, difficulty.
Quality gate: 9 minimum coverage questions every corpus must answer.

Locations:
- Gold standards: `data/seed/benchmarks/*.json`
- Question library: `packages/ontology/src/dialectica_ontology/benchmark_questions.py`
- Runner: `packages/api/src/dialectica_api/benchmark_runner.py`
- API: POST /v1/admin/benchmark/run, GET /v1/admin/benchmark/history
- Frontend: /admin/benchmarks

## TACITUS Integration API
Machine-to-machine endpoints for other TACITUS apps (Praxis, Query Layer):
- GET /v1/integration/graph/{workspace_id} — Full graph snapshot
- GET /v1/integration/context/{workspace_id} — Structured conflict context
- POST /v1/integration/query — Execute conflict analysis query

Location: `packages/api/src/dialectica_api/routers/integration.py`

## Cloud Infrastructure
- **GCP**: Cloud Run (API), BigQuery (analytics), Vertex AI (Gemini), Secret Manager, Pub/Sub, Cloud Storage
- **Neo4j Aura**: Primary graph database (TACITUS is in Neo4j Startup Program)
- **Databricks**: Advanced analytics, KGE training (optional)
- **Vercel**: Frontend deployment
- **Terraform**: `infrastructure/terraform/` (all GCP resources)
- **Runbook**: `docs/runbook.md` (step-by-step production deployment)

## Key new file locations
- **Domain specs**: packages/ontology/src/dialectica_ontology/domains.py (2 domains, 12 subdomains)
- **ConflictCorpus**: packages/ontology/src/dialectica_ontology/corpus.py
- **Benchmark questions**: packages/ontology/src/dialectica_ontology/benchmark_questions.py (35+ questions)
- **Knowledge clusters**: packages/reasoning/src/dialectica_reasoning/graphrag/knowledge_clusters.py
- **Qdrant store**: packages/graph/src/dialectica_graph/qdrant_store.py
- **BigQuery analytics**: packages/api/src/dialectica_api/analytics.py
- **Databricks connector**: packages/reasoning/src/dialectica_reasoning/databricks_connector.py
- **Integration API**: packages/api/src/dialectica_api/routers/integration.py
- **Implementation plan**: docs/superpowers/plans/2026-04-06-dialectica-production-ready.md
