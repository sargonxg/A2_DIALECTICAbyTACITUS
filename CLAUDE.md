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
- Publish ontology: `cd packages/ontology && uv build && twine upload dist/*`
