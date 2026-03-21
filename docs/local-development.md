# Local Development Guide

## Prerequisites

- **Python 3.12+** — `python --version`
- **UV** — `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Docker & Docker Compose** — for databases and services
- **Node.js 20+** — for the web frontend
- **Make** — for convenience targets

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/sargonxg/A2_DIALECTICAbyTACITUS.git
cd A2_DIALECTICAbyTACITUS

# 2. Copy environment config
cp .env.example .env

# 3. Start all services (Spanner emulator + Redis + FalkorDB + Qdrant + API + Web)
make dev

# 4. In another terminal, seed the database
make seed
```

Services will be available at:
- **API**: http://localhost:8080 (docs at /docs)
- **Web**: http://localhost:3000
- **FalkorDB**: localhost:6380
- **Qdrant**: localhost:6333 (REST), localhost:6334 (gRPC)
- **Redis**: localhost:6379
- **Spanner emulator**: localhost:9010

## Installing Dependencies

```bash
# Python packages (all workspace packages)
uv sync --all-packages

# Web frontend
cd apps/web && npm install
```

## Running Tests

```bash
make test                    # All Python tests
make test-ontology           # Ontology package only
make test-api                # API package only
uv run pytest packages/ontology/tests/ -x   # Single package with UV
make test-web                # Frontend tests
```

## Code Quality

```bash
make lint                    # ruff check
make format                  # ruff format
make typecheck               # mypy
make quality-all             # All checks (Python + TypeScript)
```

## Using Different Graph Backends

```bash
# Default: Spanner emulator
make dev

# Neo4j backend
make dev-neo4j

# FalkorDB is always available via docker-compose (port 6380)
```

## Common Development Tasks

### Add a new node type
1. Edit `packages/ontology/src/dialectica_ontology/primitives.py`
2. Add enums in `enums.py`
3. Add relationships in `relationships.py`
4. Update tier config in `tiers.py`
5. Add tests in `packages/ontology/tests/`

### Add a new API endpoint
1. Create or update router in `packages/api/src/dialectica_api/routers/`
2. Register in `packages/api/src/dialectica_api/main.py`
3. Add tests in `packages/api/tests/`

### Add a new symbolic rule
1. Create module in `packages/reasoning/src/dialectica_reasoning/symbolic/`
2. Register in `inference.py`
3. Add parametrized tests
