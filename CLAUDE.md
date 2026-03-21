# DIALECTICA by TACITUS — Claude Code Project Guide

## What this is
DIALECTICA is the core neurosymbolic conflict intelligence engine for TACITUS (tacitus.me).
It transforms unstructured conflict data into structured knowledge graphs using the
8-primitive Conflict Grammar ontology (Actor, Claim, Interest, Constraint, Leverage,
Commitment, Event, Narrative) and delivers reasoning-backed decision support for two
domains: human friction (HR disputes, commercial mediation) and warfare/political
conflict (JCPOA-type geopolitical analysis, UN Security Council dynamics).

## Architecture (4 layers)
1. **Neural Ingestion**: GLiNER NER pre-filter -> Gemini 2.5 Flash structured extraction -> Pydantic v2 validation
2. **Symbolic Representation**: Conflict Grammar graph stored in Neo4j Aura (primary) + FalkorDB (tenant layer)
3. **Reasoning & Inference**: 9 deterministic symbolic rules fire FIRST -> GNN/KGE neural fills gaps -> human validates
4. **Decision Support**: 6 AI agents (Analyst, Advisor, Comparator, Forecaster, Mediator, Theorist) + MCP server

## Critical invariant
Deterministic symbolic conclusions (treaty violations, legal constraints) are NEVER overridden
by probabilistic neural predictions. This is enforced via confidence_type tagging:
"deterministic" (from symbolic rules) vs "probabilistic" (from GNN/LLM).

## Package dependency graph
ontology -> graph -> extraction -> reasoning -> api
                                                 ^
                                             apps/web (HTTP)

## Tech stack
- Python 3.12, UV workspaces, Pydantic v2 with StrEnum + discriminated unions
- FastAPI (async), LangGraph pipeline orchestration
- **Neo4j Aura (primary graph DB — TACITUS is in Neo4j Startup Program)**
- FalkorDB (tenant isolation, dev/test), Spanner (optional GCP alternative)
- Qdrant (vector search, named vectors for KGE + semantic embeddings)
- Google Cloud: Cloud Run (API deploy), Vertex AI, Secret Manager
- Gemini 2.5 Flash (extraction), Gemini 2.5 Pro (synthesis), ConfliBERT (classification)

## Optional heavy dependencies
- torch, torch-geometric, pykeen: `pip install dialectica-reasoning[kge]` — only for KGE training
- leidenalg, igraph: included in `[kge]` extra — for Leiden community detection (falls back to networkx)
- gliner: `pip install dialectica-extraction[gliner]` — for zero-shot NER (falls back to keyword matching)

## Conventions
- All code must pass `ruff check` and `ruff format --check`
- Type annotations required on all public functions (mypy strict)
- Tests: pytest with pytest-asyncio, mock external services, never mock business logic
- Commits: conventional commits (feat:, fix:, refactor:, docs:, test:, infra:)
- Env vars: see .env.example for all configuration
- Graph queries: always scope by workspace_id AND tenant_id

## Key file locations
- Ontology models: packages/ontology/src/dialectica_ontology/primitives.py (15 node types)
- Relationships: packages/ontology/src/dialectica_ontology/relationships.py (20 edge types)
- Enums: packages/ontology/src/dialectica_ontology/enums.py (39 StrEnum types)
- Graph interface: packages/graph/src/dialectica_graph/interface.py (abstract GraphClient)
- Neo4j client: packages/graph/src/dialectica_graph/neo4j_client.py
- Extraction pipeline: packages/extraction/src/dialectica_extraction/pipeline.py (10-step LangGraph DAG)
- Symbolic rules: packages/reasoning/src/dialectica_reasoning/symbolic/ (9 modules)
- AI agents: packages/reasoning/src/dialectica_reasoning/agents/ (6 agents)
- API entry: packages/api/src/dialectica_api/main.py
- Seed data: data/seed/samples/ (6 conflict scenarios, 114 nodes, 126 edges)

## Running locally
```
make dev-local           # docker-compose.local.yml: Neo4j + Redis + API
make seed                # load sample data into Neo4j
make test                # all tests
uv run pytest packages/ontology/tests/ -x   # single package
make lint                # ruff check + format check
```

## Testing
```
make test-ontology       # 420 tests, 80% coverage
make test-api            # 72 tests (core API routes)
make test-extraction     # 75 tests (pipeline + GLiNER)
make test-reasoning      # 29 tests (symbolic + KGE availability)
```

## Deploy
- API: Cloud Run via `bash infrastructure/scripts/deploy-cloudrun.sh PROJECT_ID`
- Frontend: Vercel (apps/web)
- Neo4j Aura: production graph database (credentials in Secret Manager)

## Common tasks
- Add new node type: primitives.py -> enums.py -> relationships.py -> tiers.py -> tests
- Add symbolic rule: symbolic/ module -> register in inference.py -> add parametrized test
- Add API endpoint: routers/ -> register in main.py -> add test in api/tests/
