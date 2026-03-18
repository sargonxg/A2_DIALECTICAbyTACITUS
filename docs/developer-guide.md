# DIALECTICA Developer Guide

A comprehensive guide for developing, testing, and contributing to the DIALECTICA
neurosymbolic conflict intelligence platform by TACITUS.

---

## Table of Contents

1. [Repository Structure](#1-repository-structure)
2. [Getting Started](#2-getting-started)
3. [Package Development](#3-package-development)
4. [Adding New Node and Edge Types to the Ontology](#4-adding-new-node-and-edge-types-to-the-ontology)
5. [Writing and Running Tests](#5-writing-and-running-tests)
6. [API Development](#6-api-development)
7. [Code Style and Conventions](#7-code-style-and-conventions)
8. [Contributing Guidelines](#8-contributing-guidelines)
9. [Common Make Targets Reference](#9-common-make-targets-reference)

---

## 1. Repository Structure

DIALECTICA is organized as a Python monorepo with five packages and one frontend
application. All Python packages use Poetry for dependency management and are
installed as editable packages.

```
A2_DIALECTICAbyTACITUS/
├── packages/
│   ├── ontology/          # Conflict Grammar: nodes, edges, enums, tiers, theories
│   ├── graph/             # Dual-backend graph DB abstraction (Spanner + Neo4j)
│   ├── extraction/        # 10-step LangGraph extraction pipeline
│   ├── reasoning/         # Symbolic rules, GraphRAG, AI agents
│   ├── api/               # FastAPI service (routers, middleware, config)
│   └── sdk-typescript/    # Generated TypeScript SDK
├── apps/
│   └── web/               # Next.js 14 frontend
├── infrastructure/
│   ├── terraform/         # GCP infrastructure definitions
│   └── scripts/           # Seed scripts, SDK generation, admin key creation
├── docs/                  # Project documentation
├── Makefile               # Development, test, build, and deploy targets
├── docker-compose.yml     # Local development services
├── .env.example           # Environment variable template
└── .github/workflows/     # CI and deploy pipelines
```

### Dependency Graph

Packages depend on each other in a strict linear chain:

```
ontology  <--  graph  <--  extraction  <--  reasoning  <--  api
                                                             ^
                                                             |
                                                         apps/web (via HTTP)
```

Each package imports only from packages to its left. The web frontend communicates
with the API exclusively over HTTP.

### Package Summary

| Package | PyPI Name | Description |
|---------|-----------|-------------|
| `packages/ontology` | `dialectica-ontology` | 15 node types, 20 edge types, 39 enums, 3 tiers, 16 theory modules, 4 compatibility mappers |
| `packages/graph` | `dialectica-graph` | Async `GraphClient` ABC with Spanner Graph and Neo4j implementations |
| `packages/extraction` | `dialectica-extraction` | GLiNER pre-filtering + Gemini Flash extraction + 4-layer validation |
| `packages/reasoning` | `dialectica-reasoning` | 9 symbolic rule modules, GraphRAG retriever, 6 AI agents, hallucination detection |
| `packages/api` | `dialectica-api` | FastAPI app with 12 routers, 5 middleware layers, Prometheus metrics |

---

## 2. Getting Started

### Prerequisites

- Python 3.11 or later (3.12 recommended)
- Node.js 18+ and npm (for the web frontend and TypeScript SDK)
- Docker and Docker Compose (for local services)
- A GCP project with Vertex AI enabled (for extraction/reasoning features)
- Optional: Google Cloud SDK (`gcloud`) for deployment

### Clone the Repository

```bash
git clone https://github.com/sargonxg/dialectica.git
cd dialectica
```

### Install Python Dependencies

All five Python packages are installed in editable mode so that changes take
effect immediately:

```bash
make install
```

This runs:

```bash
pip install -e packages/ontology
pip install -e packages/graph
pip install -e packages/extraction
pip install -e packages/reasoning
pip install -e packages/api
```

Order matters: each package depends on the packages listed before it.

### Install Dev Tools

To also install linting, type-checking, and testing tools plus the web frontend
dependencies:

```bash
make install-dev
```

This installs `ruff`, `mypy`, `pytest`, `pytest-asyncio`, and `pytest-cov`, then
runs `npm install` in `apps/web`.

### Environment Configuration

Copy the environment template and fill in your values:

```bash
cp .env.example .env
```

Key variables to configure for local development:

| Variable | Purpose | Local Default |
|----------|---------|---------------|
| `GCP_PROJECT_ID` | Your GCP project | (required) |
| `SPANNER_EMULATOR_HOST` | Use local Spanner emulator | `localhost:9010` |
| `GRAPH_BACKEND` | Graph database backend | `spanner` |
| `ENVIRONMENT` | `development` or `production` | `development` |
| `ADMIN_API_KEY` | Admin key for API access | Set any string for dev |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

For local development with the Spanner emulator, uncomment `SPANNER_EMULATOR_HOST`
and leave `GOOGLE_APPLICATION_CREDENTIALS` empty. The emulator runs as a Docker
service.

### Start Local Services

The fastest way to get everything running locally:

```bash
make dev
```

This starts Docker Compose with the following services:

| Service | Port | Description |
|---------|------|-------------|
| `spanner-emulator` | 9010 (gRPC), 9020 (REST) | Local Spanner emulator |
| `spanner-init` | -- | One-shot schema initialization |
| `api` | 8080 | FastAPI backend |
| `web` | 3000 | Next.js frontend |

To also include the Neo4j backend:

```bash
make dev-neo4j
```

This adds a Neo4j 5 Community instance (ports 7474, 7687) and a second API
instance (`api-neo4j` on port 8081) configured to use Neo4j.

### Seed the Database

After services are running, seed reference data:

```bash
make seed-schema       # Initialize Spanner schema
make seed-frameworks   # Load theory frameworks
make seed-samples      # Load JCPOA and sample conflict graphs
```

Or run all three at once:

```bash
make seed
```

### Verify the Setup

- API docs: http://localhost:8080/docs (Swagger UI)
- API ReDoc: http://localhost:8080/redoc
- Health check: http://localhost:8080/health
- Prometheus metrics: http://localhost:8080/metrics
- Web frontend: http://localhost:3000
- Neo4j Browser (if enabled): http://localhost:7474

---

## 3. Package Development

### ontology (`packages/ontology`)

The ontology package is the foundation of the entire system. It defines the
Conflict Grammar (ACO v2.0) as Pydantic v2 models.

**Source layout:**

```
packages/ontology/src/dialectica_ontology/
├── __init__.py
├── primitives.py        # 15 ConflictNode subclasses (Actor, Conflict, Event, ...)
├── relationships.py     # 20 EdgeType definitions with source/target constraints
├── enums.py             # 39 controlled vocabulary enums
├── tiers.py             # 3 progressive disclosure tiers (Essential/Standard/Full)
├── schemas.py           # Shared schema utilities
├── validators.py        # Validation helpers
├── symbolic_rules.py    # Symbolic rule definitions
├── neurosymbolic.py     # NeurosymbolicArchitecture Pydantic model (4 layers)
├── theory_graph.py      # Theory-to-ontology mapping graph
├── theory/              # 16 theory modules (Glasl, Fisher/Ury, Galtung, etc.)
├── compatibility/       # 4 external standard mappers (ACLED, CAMEO, PLOVER, UCDP)
└── py.typed             # PEP 561 marker for typed package
```

Key design rules:
- All node types inherit from `ConflictNode`, which provides ULID IDs,
  `tenant_id`/`workspace_id` scoping, confidence scores, and optional embeddings.
- Edge types are defined in `EdgeType(StrEnum)` with schemas specifying valid
  source and target node labels.
- Enums use `StrEnum` for JSON serialization compatibility.
- The ontology is **never** allowed to import from graph, extraction, reasoning,
  or api.

### graph (`packages/graph`)

Provides an async abstract interface (`GraphClient` ABC) and two concrete
implementations.

**Key files:**

- `interface.py` -- The `GraphClient` abstract base class. All methods are async
  and scoped by `workspace_id` + `tenant_id`.
- `spanner.py` -- Google Cloud Spanner Graph implementation (GQL + SQL + vector).
- `neo4j.py` -- Neo4j implementation (Cypher + APOC).

Key operations: `upsert_node`, `upsert_edge`, `get_node`, `get_nodes`,
`get_edges`, `traverse`, `vector_search`, `execute_query`, `batch_upsert_nodes`,
`batch_upsert_edges`, `get_workspace_stats`, `get_actor_network`, `get_timeline`,
`get_escalation_trajectory`.

Backend selection is controlled by the `GRAPH_BACKEND` environment variable
(`spanner` or `neo4j`).

### extraction (`packages/extraction`)

A 10-step LangGraph `StateGraph` pipeline that ingests documents and populates
the graph.

**Pipeline steps:**

1. `chunk_document` -- Split into 2000-char overlapping chunks
2. `gliner_prefilter` -- GLiNER NER entity density scoring
3. `extract_entities` -- Gemini Flash structured extraction by tier
4. `validate_schema` -- Pydantic v2 validation against `ConflictNode` models
5. `repair_extraction` -- Send validation errors back to Gemini (max 3 retries)
6. `extract_relationships` -- Gemini extracts edges between validated nodes
7. `resolve_coreference` -- Cross-chunk entity merging + alias matching
8. `validate_structural` -- Structural + temporal + symbolic validation
9. `compute_embeddings` -- Vertex AI `text-embedding-005` (768-dim)
10. `write_to_graph` -- Batch upsert to graph database

Conditional routing after step 4 loops to `repair_extraction` if validation fails
(up to 3 retries), then continues to step 6.

### reasoning (`packages/reasoning`)

Contains the symbolic rule engine, GraphRAG retriever, AI agents, and
hallucination detection.

**Key components:**

- `query_engine.py` -- `ConflictQueryEngine` orchestrates retrieval, symbolic
  analysis, LLM synthesis, and citation generation.
- `symbolic/` -- 9+ symbolic rule modules (escalation, trust, causal, ripeness,
  power, pattern matching, constraint engine, network metrics, inference).
- `graphrag/` -- `ConflictGraphRAGRetriever` (vector + graph traversal) and
  `ConflictContextBuilder`.
- `agents/` -- 6 AI agents (Analyst, Advisor, Comparator, Forecaster, Mediator,
  Theorist).
- `hallucination_detector.py` -- Checks every synthesis for hallucination risk.

The query engine supports 7 modes: `general`, `escalation`, `ripeness`, `trust`,
`power`, `causal`, `network`.

### api (`packages/api`)

The FastAPI application that exposes all functionality over HTTP.

**Source layout:**

```
packages/api/src/dialectica_api/
├── main.py              # Application factory (create_app)
├── config.py            # Settings via pydantic-settings
├── deps.py              # Dependency injection (graph client, etc.)
├── routers/
│   ├── health.py        # /health -- liveness and readiness
│   ├── workspaces.py    # /workspaces -- workspace CRUD
│   ├── entities.py      # /entities -- node CRUD
│   ├── relationships.py # /relationships -- edge CRUD
│   ├── extraction.py    # /extraction -- document ingestion
│   ├── graph.py         # /graph -- traversal, subgraph, stats
│   ├── reasoning.py     # /reasoning -- query engine, analysis
│   ├── theory.py        # /theory -- theory frameworks
│   ├── admin.py         # /admin -- API key management, system ops
│   ├── developers.py    # /developers -- developer portal
│   ├── sdk_info.py      # SDK metadata
│   └── benchmark.py     # JCPOA benchmark evaluation
└── middleware/
    ├── auth.py          # API key authentication
    ├── tenant.py        # Tenant context injection
    ├── rate_limit.py    # Per-key rate limiting
    ├── usage.py         # Usage tracking per key
    └── logging.py       # Structured JSON request logging
```

---

## 4. Adding New Node and Edge Types to the Ontology

### Adding a New Node Type

1. **Define the enum values** in `packages/ontology/src/dialectica_ontology/enums.py`
   if your node requires new controlled vocabularies (e.g., a new status enum or
   category enum).

2. **Create the Pydantic model** in `packages/ontology/src/dialectica_ontology/primitives.py`.
   Inherit from `ConflictNode`:

   ```python
   class MyNewNode(ConflictNode):
       """Description of the new node type and its theoretical basis."""
       label: ClassVar[str] = "MyNewNode"

       # Required fields
       name: str
       my_category: MyNewCategoryEnum

       # Optional fields with defaults
       description: str | None = None
       confidence: float = Field(default=0.5, ge=0.0, le=1.0)
   ```

3. **Register the node in a tier** by editing
   `packages/ontology/src/dialectica_ontology/tiers.py`. Add it to the
   appropriate tier(s): Essential (7 nodes), Standard (12), or Full (15). Nodes
   in lower tiers are automatically included in higher tiers.

4. **Add edge constraints** in `packages/ontology/src/dialectica_ontology/relationships.py`
   to define which edge types can connect to or from your new node. Each edge
   schema specifies valid `source_labels` and `target_labels`.

5. **Update extraction prompts** in the extraction package so that Gemini knows
   how to extract instances of your new node type from documents.

6. **Write tests** in `packages/ontology/tests/test_primitives.py` to verify
   model creation, validation, and serialization.

7. **Update the graph schema** if using Spanner, ensure the DDL in
   `infrastructure/scripts/init_spanner.py` includes the new node label. Neo4j
   handles new labels dynamically.

### Adding a New Edge Type

1. **Add the edge type** to the `EdgeType` StrEnum in
   `packages/ontology/src/dialectica_ontology/relationships.py`:

   ```python
   class EdgeType(StrEnum):
       # ... existing types ...
       MY_NEW_EDGE = "MY_NEW_EDGE"
   ```

2. **Define the edge schema** specifying valid source/target labels and
   required/optional properties:

   ```python
   EDGE_SCHEMAS[EdgeType.MY_NEW_EDGE] = EdgeSchema(
       source_labels=["Actor", "Conflict"],
       target_labels=["Event", "Outcome"],
       required_properties=["strength"],
       optional_properties=["description"],
   )
   ```

3. **Assign the edge to a tier** in `tiers.py`.

4. **Write tests** in `packages/ontology/tests/test_relationships.py` to verify
   valid and invalid source/target combinations.

---

## 5. Writing and Running Tests

### Test Structure

Each package has a `tests/` directory alongside its `src/` directory:

```
packages/ontology/tests/
├── __init__.py
├── test_primitives.py       # Node model creation and validation
├── test_relationships.py    # Edge type schemas and constraints
├── test_enums.py            # Enum completeness and serialization
├── test_theories.py         # Theory module integration
├── test_tiers.py            # Tier composition and progressive disclosure
└── test_validators.py       # Validation logic

packages/graph/tests/
├── __init__.py
├── conftest.py              # Fixtures (emulator client, mock data)
└── test_spanner.py          # Spanner client integration tests

packages/extraction/tests/
├── __init__.py
├── test_pipeline.py         # Pipeline step tests
└── test_gemini.py           # Gemini extraction tests

packages/reasoning/tests/
├── __init__.py
└── test_reasoning.py        # Query engine and symbolic rule tests

packages/api/tests/
├── __init__.py
├── conftest.py              # Test client fixtures, mock dependencies
├── test_api.py              # Router endpoint tests
├── test_benchmark.py        # Benchmark evaluation tests
└── test_hardening.py        # Security and auth hardening tests
```

### Running Tests

**All tests:**

```bash
make test
```

This runs `pytest packages/ -v --tb=short` across the entire monorepo.

**Unit tests only (no integration tests requiring external services):**

```bash
make test-unit
```

**Integration tests (requires running Spanner emulator):**

```bash
make test-integration
```

**Per-package tests:**

```bash
make test-ontology      # packages/ontology/tests/
make test-graph         # packages/graph/tests/
make test-extraction    # packages/extraction/tests/
make test-reasoning     # packages/reasoning/tests/
make test-api           # packages/api/tests/
make test-web           # apps/web (npm test)
```

**Benchmark tests:**

```bash
make test-benchmark     # packages/api/tests/test_benchmark.py
```

### Writing Tests

- Use `pytest` with `pytest-asyncio` for async tests.
- Mark integration tests with `@pytest.mark.integration` so they can be excluded
  during fast local iterations (`make test-unit`).
- Place shared fixtures in `conftest.py` files within each package's `tests/`
  directory.
- Use `pytest-mock` for mocking external services (Gemini, Spanner, Vertex AI).

**Example test for a new node type:**

```python
# packages/ontology/tests/test_primitives.py

def test_my_new_node_creation():
    node = MyNewNode(
        name="Test Node",
        my_category=MyNewCategoryEnum.CATEGORY_A,
        workspace_id="ws-001",
        tenant_id="tenant-001",
    )
    assert node.label == "MyNewNode"
    assert node.name == "Test Node"
    assert 0.0 <= node.confidence <= 1.0


def test_my_new_node_validation_rejects_invalid():
    with pytest.raises(ValidationError):
        MyNewNode(
            name="",  # Empty name should fail
            my_category="INVALID",
            workspace_id="ws-001",
            tenant_id="tenant-001",
        )
```

### CI Test Pipeline

Tests run automatically in CI (`.github/workflows/ci.yml`) on every push and PR
to `main` or `develop`. The CI job starts a Spanner emulator service container
for integration tests and uploads coverage reports.

---

## 6. API Development

### Adding a New Router

1. **Create the router file** in `packages/api/src/dialectica_api/routers/`:

   ```python
   # packages/api/src/dialectica_api/routers/my_feature.py
   from __future__ import annotations

   from fastapi import APIRouter, Depends

   from dialectica_api.deps import get_graph_client

   router = APIRouter(prefix="/v1/my-feature", tags=["My Feature"])


   @router.get("/")
   async def list_items(client=Depends(get_graph_client)):
       """List items for the current workspace."""
       # Implementation here
       return {"items": []}


   @router.post("/")
   async def create_item(client=Depends(get_graph_client)):
       """Create a new item."""
       # Implementation here
       return {"id": "new-item-id"}
   ```

2. **Register the router** in `packages/api/src/dialectica_api/main.py`:

   ```python
   from dialectica_api.routers import my_feature

   # Inside create_app():
   app.include_router(my_feature.router)
   ```

3. **Write tests** in `packages/api/tests/` using the HTTPX test client provided
   by the `conftest.py` fixtures.

### Middleware

DIALECTICA uses five middleware layers applied in LIFO order (Starlette
convention). The request flows through them in this order:

```
Request -> Logging -> Usage -> RateLimit -> Tenant -> Auth -> Router
```

To add new middleware:

1. Create a file in `packages/api/src/dialectica_api/middleware/`.
2. Implement a class inheriting from Starlette's `BaseHTTPMiddleware` or use a
   raw ASGI middleware pattern.
3. Register it in `create_app()` in `main.py` using `app.add_middleware()`.
   Remember: the **last** middleware added executes **first** (LIFO).

### Dependency Injection

Common dependencies are defined in `packages/api/src/dialectica_api/deps.py`:

- `get_graph_client` -- Returns the configured `GraphClient` instance (Spanner
  or Neo4j based on `GRAPH_BACKEND`).
- Use `Depends()` in route signatures to inject these.

### Configuration

Settings are managed via `pydantic-settings` in
`packages/api/src/dialectica_api/config.py`. Environment variables are loaded
from `.env` or the process environment. Access settings with `get_settings()`.

### API Documentation

FastAPI auto-generates OpenAPI documentation:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

Use descriptive docstrings on route functions -- they appear in the generated
docs.

### Prometheus Metrics

The API exposes Prometheus metrics at `/metrics` via
`prometheus-fastapi-instrumentator`. This is enabled automatically if the
package is installed. Excluded endpoints: `/health`, `/metrics`.

---

## 7. Code Style and Conventions

### Python

- **Formatter and linter:** Ruff (replaces Black + isort + flake8).
- **Type checker:** mypy.
- **Python version:** 3.11+ (use `from __future__ import annotations` for
  forward references).
- **Data models:** Pydantic v2 for all domain models and API schemas.
- **Async:** All graph operations and route handlers are async.
- **IDs:** ULID (Universally Unique Lexicographically Sortable Identifier) via
  `python-ulid`.
- **Enums:** Use `StrEnum` for JSON-serializable enums.
- **Imports:** Group in order: stdlib, third-party, local. Ruff enforces this.
- **Docstrings:** Use triple-double-quote docstrings on all public classes and
  functions.
- **Logging:** Structured JSON logging (no print statements). Use
  `logging.getLogger("dialectica.<module>")`.

### TypeScript (Web App)

- Next.js 14 with the App Router.
- TypeScript strict mode.
- Lint with `next lint`.

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Python packages | `snake_case` | `dialectica_ontology` |
| Python modules | `snake_case` | `primitives.py` |
| Classes | `PascalCase` | `ConflictNode`, `GraphClient` |
| Functions | `snake_case` | `upsert_node`, `extract_entities` |
| Constants | `UPPER_SNAKE_CASE` | `EDGE_SCHEMAS`, `EdgeType.PARTY_TO` |
| Env variables | `UPPER_SNAKE_CASE` | `GRAPH_BACKEND` |
| API routes | `kebab-case` | `/v1/my-feature` |
| Test files | `test_*.py` | `test_primitives.py` |

### Run Quality Checks

```bash
make lint           # Run ruff linter
make lint-fix       # Run ruff with auto-fix
make format         # Format code with ruff
make typecheck      # Run mypy type checker
make quality        # lint + typecheck combined
make quality-all    # Python + TypeScript checks
```

---

## 8. Contributing Guidelines

### Branch Strategy

- `main` -- Production-ready code. Deploys automatically on push.
- `develop` -- Integration branch. CI runs on every push/PR.
- Feature branches: `feature/<short-description>`
- Bug fixes: `fix/<short-description>`

### Development Workflow

1. Create a feature branch from `develop`.
2. Make changes in the relevant package(s).
3. Write or update tests for your changes.
4. Run quality checks locally:
   ```bash
   make format
   make quality
   make test-unit
   ```
5. Commit with a clear, descriptive message.
6. Open a PR against `develop`.
7. Ensure CI passes (lint, typecheck, tests, Docker build).
8. Request review.

### Commit Messages

Use concise, imperative-mood messages:

```
Add TrustState node to ontology with Mayer/Davis/Schoorman model
Fix Glasl stage transition logic for de-escalation paths
Update extraction pipeline to handle multi-language documents
```

### Package Dependency Rules

- **ontology** must have zero internal imports (it is the leaf dependency).
- **graph** may import only from ontology.
- **extraction** may import from ontology and graph.
- **reasoning** may import from ontology and graph.
- **api** may import from all packages.
- Never introduce circular dependencies between packages.

### Architecture Principles

- **Deterministic conclusions are never overridden by probabilistic inference.**
  Symbolic rules fire first; neural components fill gaps second.
- **TACITUS is decision-support, not autonomous resolution.** The system surfaces
  options and risks for human decision-makers.
- **Multi-tenancy is mandatory.** Every node and edge carries `tenant_id` and
  `workspace_id`. All queries must filter by these fields.
- **Confidence scores are required.** Every extracted entity and relationship
  carries a confidence score between 0.0 and 1.0.

---

## 9. Common Make Targets Reference

### Development

| Target | Description |
|--------|-------------|
| `make dev` | Start all services locally with Docker Compose |
| `make dev-build` | Build and start all services |
| `make dev-down` | Stop all services |
| `make dev-logs` | Follow logs for all services |
| `make dev-neo4j` | Start with Neo4j backend (api-neo4j on port 8081) |
| `make dev-neo4j-build` | Build and start with Neo4j backend |

### Testing

| Target | Description |
|--------|-------------|
| `make test` | Run all Python tests |
| `make test-unit` | Run unit tests only (no integration) |
| `make test-integration` | Run integration tests (requires Spanner emulator) |
| `make test-api` | Run API tests only |
| `make test-ontology` | Run ontology package tests |
| `make test-graph` | Run graph package tests |
| `make test-extraction` | Run extraction package tests |
| `make test-reasoning` | Run reasoning package tests |
| `make test-web` | Run Next.js tests |
| `make test-benchmark` | Run benchmark tests |
| `make benchmark` | Run JCPOA benchmark evaluation via live API |

### Code Quality

| Target | Description |
|--------|-------------|
| `make lint` | Run ruff linter |
| `make lint-fix` | Run ruff with auto-fix |
| `make format` | Format code with ruff |
| `make typecheck` | Run mypy type checker |
| `make typecheck-strict` | Run mypy in strict mode |
| `make tsc` | TypeScript type check for web app |
| `make web-lint` | Lint Next.js app |
| `make quality` | Run Python quality checks (lint + typecheck) |
| `make quality-all` | Run all quality checks (Python + TypeScript) |

### Database and Seed

| Target | Description |
|--------|-------------|
| `make seed` | Run all seed operations |
| `make seed-schema` | Initialize Spanner schema |
| `make seed-frameworks` | Load theory frameworks into database |
| `make seed-samples` | Load JCPOA and other sample conflict graphs |
| `make create-admin-key` | Generate and store admin API key |

### SDK

| Target | Description |
|--------|-------------|
| `make sdk-generate` | Generate TypeScript SDK from OpenAPI spec |
| `make sdk-build` | Generate and build TypeScript SDK |

### Build and Deploy

| Target | Description |
|--------|-------------|
| `make build` | Build all Docker images (API + Web) |
| `make build-api` | Build API Docker image |
| `make build-web` | Build Web Docker image |
| `make docker-push` | Push images to Artifact Registry |
| `make deploy` | Full deploy pipeline (build, push, deploy) |
| `make deploy-api` | Deploy API to Cloud Run |
| `make deploy-web` | Deploy Web to Cloud Run |

### Terraform

| Target | Description |
|--------|-------------|
| `make tf-init` | Initialize Terraform |
| `make tf-plan` | Plan Terraform changes |
| `make tf-apply` | Apply Terraform changes |
| `make tf-destroy` | Destroy Terraform resources |

### Utilities

| Target | Description |
|--------|-------------|
| `make install` | Install all Python packages (editable) |
| `make install-web` | Install web app npm dependencies |
| `make install-dev` | Install all dependencies including dev tools |
| `make publish-ontology` | Build and publish ontology package to PyPI |
| `make clean` | Clean build artifacts and caches |
| `make help` | Show all available targets with descriptions |
