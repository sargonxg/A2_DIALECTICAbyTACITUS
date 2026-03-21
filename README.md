# DIALECTICA by TACITUS

### The universal data layer for human friction and warfare intelligence

[![CI](https://github.com/sargonxg/A2_DIALECTICAbyTACITUS/actions/workflows/ci.yml/badge.svg)](https://github.com/sargonxg/A2_DIALECTICAbyTACITUS/actions)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-Aura-008CC1.svg)](https://neo4j.com/cloud/aura/)
[![Google Cloud](https://img.shields.io/badge/Google_Cloud-Cloud_Run-4285F4.svg)](https://cloud.google.com/run)

> *"We make conflict computable enough for better human judgment."*

DIALECTICA is a neurosymbolic conflict intelligence platform that structures any conflict — from interpersonal workplace disputes to geopolitical armed conflicts — into a computable knowledge graph grounded in 30+ academic frameworks. It serves as the universal data backbone for TACITUS products and as a developer API platform.

---

## Quick Start

### Prerequisites
- **Docker & Docker Compose** (for local development)
- **Python 3.12+** and [UV](https://docs.astral.sh/uv/) (for running tests / scripts directly)
- **Node.js 20+** (for the frontend)
- **GCP account** + `gcloud` CLI (for production deployment)
- **Neo4j Aura account** (free tier available — [neo4j.com/cloud/aura](https://neo4j.com/cloud/aura/))

### Local Development (Docker — fastest)

```bash
git clone https://github.com/sargonxg/A2_DIALECTICAbyTACITUS.git
cd A2_DIALECTICAbyTACITUS

# 1. Configure environment
cp .env.example .env
# Edit .env if needed (defaults work for local Docker)

# 2. Start minimal stack: Neo4j + Redis + API
make dev-local
# Wait ~60s for Neo4j to become healthy

# 3. Seed sample data (6 conflict scenarios, 114 nodes, 126 edges)
make seed

# 4. Verify
curl http://localhost:8080/health
curl -H "X-API-Key: dev-admin-key-local" http://localhost:8080/v1/workspaces
```

**What's running:**
| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8080 | FastAPI with Swagger docs at /docs |
| Neo4j Browser | http://localhost:7474 | Graph visualization (neo4j/dialectica-dev) |
| Redis | localhost:6379 | Rate limiting and caching |

### Local Development (without Docker)

```bash
# Install UV
pip install uv

# Install all Python packages (without heavy ML deps)
uv sync --all-packages

# Run API directly (requires Neo4j running somewhere)
NEO4J_URI=bolt://localhost:7687 NEO4J_PASSWORD=dialectica-dev \
  uv run uvicorn dialectica_api.main:app --host 0.0.0.0 --port 8080

# Seed data
uv run python infrastructure/scripts/seed_sample_data.py
```

### Frontend

```bash
cd apps/web
npm install
npm run dev
# http://localhost:3000
```

**Key pages:**
| Route | Description |
|-------|-------------|
| `/` | Marketing landing page |
| `/demo` | Paste-and-see demo (works offline with fallback data) |
| `/demo/investor` | 5-step guided investor walkthrough |
| `/workspaces` | Workspace list |
| `/workspaces/[id]` | Workspace detail with Graph, Entities, Timeline, Analysis, Query tabs |
| `/theory` | 15 theory frameworks browser |
| `/developers` | API documentation and playground |
| `/login` / `/signup` | Authentication |

---

## Deployment

### Step 1: Set Up Neo4j Aura (Production Database)

1. Go to [Neo4j Aura](https://neo4j.com/cloud/aura/) and create a free instance
2. Note your connection URI (`neo4j+s://xxxxx.databases.neo4j.io`), username, and password
3. Store credentials in GCP Secret Manager:

```bash
# Interactive — prompts for URI, user, password
bash infrastructure/scripts/setup-secrets.sh YOUR_GCP_PROJECT_ID
```

This creates three secrets:
- `dialectica-neo4j-uri`
- `dialectica-neo4j-user`
- `dialectica-neo4j-password`

### Step 2: Deploy API to Google Cloud Run

```bash
# One-command deploy: build, push, deploy, verify
bash infrastructure/scripts/deploy-cloudrun.sh YOUR_GCP_PROJECT_ID us-east1
```

**What this script does:**
1. Enables Cloud Run, Artifact Registry, Secret Manager APIs
2. Creates an Artifact Registry Docker repository
3. Builds a slim Docker image (~400MB, no torch/gliner) via Cloud Build
4. Creates an admin API key secret (random 64-char hex)
5. Deploys to Cloud Run with:
   - 1-4 instances, 2 vCPU, 2GB RAM
   - Neo4j credentials injected from Secret Manager
   - Public access (unauthenticated — API key auth handled by the app)
6. Prints the API URL and verifies the health endpoint

**Configuration (environment variables set automatically):**
| Variable | Value | Source |
|----------|-------|--------|
| `GRAPH_BACKEND` | `neo4j` | Set in deploy script |
| `NEO4J_URI` | `neo4j+s://...` | Secret Manager |
| `NEO4J_USER` | `neo4j` | Secret Manager |
| `NEO4J_PASSWORD` | `***` | Secret Manager |
| `ADMIN_API_KEY` | random hex | Secret Manager |
| `ENVIRONMENT` | `production` | Set in deploy script |
| `RATE_LIMIT_BACKEND` | `memory` | Set in deploy script |

### Step 3: Seed Production Data

```bash
# Set your API URL and admin key
export API_URL=https://dialectica-api-xxxxx-uc.a.run.app
export API_KEY=your-admin-key

# Seed via API (proves full stack works)
uv run python infrastructure/scripts/seed_via_api.py
```

### Step 4: Deploy Frontend to Vercel

```bash
cd apps/web

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

**Set these environment variables in the Vercel dashboard:**
| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | Your Cloud Run API URL (e.g., `https://dialectica-api-xxxxx-uc.a.run.app`) |

The Next.js app proxies `/api/v1/*` requests to the backend API, avoiding CORS issues.

### Step 5: Verify Everything

```bash
API_URL=https://dialectica-api-xxxxx-uc.a.run.app
API_KEY=your-admin-key

# Health check
curl $API_URL/health
# → {"status":"healthy","version":"2.0.0","graph_backend":"neo4j",...}

# List workspaces
curl -H "X-API-Key: $API_KEY" $API_URL/v1/workspaces
# → {"items":[...],"total":6}

# Swagger docs
open $API_URL/docs
```

### CI/CD (Automatic Deploys)

**GitHub Actions CI** runs on every push to `main` and every PR:
- Lint (ruff check + format)
- Test: ontology (420), API (72), extraction (75), reasoning (29)
- Frontend: TypeScript check

**Cloud Build** (optional): `cloudbuild.yaml` provides test → build → push → deploy → verify pipeline:
```bash
# Set up Cloud Build trigger
gcloud builds triggers create github \
  --repo-owner=sargonxg \
  --repo-name=A2_DIALECTICAbyTACITUS \
  --branch-pattern=main \
  --build-config=cloudbuild.yaml \
  --project=YOUR_PROJECT_ID
```

---

## Architecture

```mermaid
graph TB
    subgraph "Layer 1: Neural Ingestion"
        A[Raw Text / Documents] --> B[GLiNER Pre-filter]
        B --> C[Gemini Flash Extractor]
        C --> D[Pydantic Validation + Repair]
    end

    subgraph "Layer 2: Symbolic Representation"
        D --> E[Conflict Grammar\n15 Node Types x 20 Edge Types]
        E --> F[Neo4j Aura\nCypher + Vector Search]
        E --> G[25+ Controlled Vocabularies]
    end

    subgraph "Layer 3: Reasoning & Inference"
        F --> H[GraphRAG Retriever]
        F --> I[Symbolic Rule Engine\n25+ deterministic rules]
        H --> J[Context Builder]
        I --> K[Glasl Escalation\nZartman Ripeness\nTrust Analysis\nCausal Chains]
        J --> L[Gemini Pro Synthesis]
        K --> L
    end

    subgraph "Layer 4: Decision Support"
        L --> M[Structured Analysis Response]
        M --> N[Analyst Agent]
        M --> O[Mediator Agent]
        M --> P[Forecaster Agent]
        N & O & P --> Q[Human Decision-Makers]
        Q -->|Validation Loop| F
    end

    style A fill:#18181b,color:#fafafa
    style F fill:#0d9488,color:#fafafa
    style Q fill:#6366f1,color:#fafafa
```

---

## Ontology Overview

DIALECTICA implements the **TACITUS Core Ontology v2.0** — the Conflict Grammar.

### 15 Node Types

| Node | Description | Tier |
|------|-------------|------|
| **Actor** | Any entity with agency (person, org, state, coalition) | Essential |
| **Conflict** | Sustained friction pattern with Glasl stage + Kriesberg phase | Essential |
| **Event** | Discrete occurrence (PLOVER 16-type coding) | Essential |
| **Issue** | Subject matter / incompatibility (what it's ABOUT) | Essential |
| **Interest** | Underlying need/fear (the WHY) — Fisher/Ury core | Essential |
| **Norm** | Rules, laws, contracts, policies | Standard |
| **Process** | ADR mechanisms (negotiation, mediation, arbitration) | Standard |
| **Outcome** | Results of processes | Standard |
| **Narrative** | Dominant/alternative/counter frames | Standard |
| **PowerDynamic** | French/Raven power bases with temporal versioning | Standard |
| **EmotionalState** | Plutchik 8-primary emotions with dyads | Full |
| **TrustState** | Mayer/Davis/Schoorman ability x benevolence x integrity | Full |
| **Location** | Hierarchical geography (ACLED/UCDP spatial coding) | Full |
| **Evidence** | Supporting material with reliability scores | Full |
| **Role** | Contextual role reification (claimant, mediator, etc.) | Full |

### 20 Edge Types

`PARTY_TO` `PARTICIPATES_IN` `HAS_INTEREST` `PART_OF` `CAUSED` `AT_LOCATION` `WITHIN` `GOVERNED_BY` `VIOLATES` `RESOLVED_THROUGH` `PRODUCES` `ALLIED_WITH` `OPPOSED_TO` `HAS_POWER_OVER` `MEMBER_OF` `EXPERIENCES` `TRUSTS` `PROMOTES` `ABOUT` `EVIDENCED_BY`

---

## Database Options

### Primary: Neo4j Aura (TACITUS is in Neo4j Startup Program)
- **Cypher** query language (ISO GQL compatible)
- **65+ graph algorithms** via Graph Data Science
- **Native vector search** (since Neo4j 5.11)
- **Managed service** on GCP — zero ops, automatic backups
- Configure: `GRAPH_BACKEND=neo4j`

### Alternative: Google Cloud Spanner Graph
- Unified graph (GQL) + relational (SQL) + vector search
- 99.999% availability, global consistency
- Configure: `GRAPH_BACKEND=spanner`

### Development: FalkorDB
- OpenCypher compatible, GraphBLAS performance
- Configure: `GRAPH_BACKEND=falkordb`

The `GraphClient` interface (packages/graph/src/dialectica_graph/interface.py) makes backends swappable.

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.12+, TypeScript |
| **Package Manager** | UV (Python), npm (TypeScript) |
| **API Framework** | FastAPI (async, 14 routers, OpenAPI) |
| **Graph Database** | Neo4j Aura (primary), FalkorDB, Spanner |
| **Vector Store** | Qdrant (768d semantic + 256d structural) |
| **LLM** | Gemini 2.5 Flash (extraction), Gemini 2.5 Pro (synthesis) |
| **NER** | GLiNER (optional, falls back to keyword matching) |
| **Pipeline** | LangGraph (10-step extraction DAG) |
| **Frontend** | Next.js 15, React 19, Tailwind CSS, D3.js, Radix UI |
| **State** | TanStack React Query, Zustand |
| **Cache/Rate Limit** | Redis (production), in-memory (development) |
| **Deploy API** | Google Cloud Run |
| **Deploy Frontend** | Vercel |
| **CI/CD** | GitHub Actions, Cloud Build |
| **Secrets** | GCP Secret Manager |
| **IaC** | Terraform |

---

## Repository Structure

```
A2_DIALECTICAbyTACITUS/
├── packages/
│   ├── ontology/          # Core Conflict Grammar (15 nodes, 20 edges, 25+ enums, 15 theories, 25+ symbolic rules)
│   ├── graph/             # Database abstraction (Neo4j, FalkorDB, Spanner clients)
│   ├── extraction/        # LangGraph extraction pipeline + Gemini + GLiNER
│   ├── reasoning/         # GraphRAG + symbolic rule engine + 6 AI agents + KGE
│   ├── api/               # FastAPI service (14 routers, auth, rate limiting, health)
│   ├── mcp/               # MCP server for Claude Desktop (5 tools)
│   └── sdk-typescript/    # @tacitus/dialectica-sdk TypeScript client
├── apps/
│   └── web/               # Next.js 15 frontend (demo, workspaces, theory, admin, developers)
│       ├── src/app/demo/          # Paste-and-see demo + investor walkthrough
│       ├── src/app/workspaces/    # Workspace detail with 5 tabs
│       ├── src/components/        # 32 reusable components (graph, analysis, timeline, etc.)
│       ├── e2e/                   # Playwright E2E tests
│       └── vercel.json            # Vercel deploy config
├── infrastructure/
│   ├── terraform/         # GCP infrastructure as code
│   ├── scripts/
│   │   ├── deploy-cloudrun.sh     # One-command Cloud Run deployment
│   │   ├── setup-secrets.sh       # Store Neo4j Aura creds in Secret Manager
│   │   ├── seed_sample_data.py    # Load sample data into Neo4j (async)
│   │   └── seed_via_api.py        # Seed via REST API (validates full stack)
│   ├── cloudrun/          # Cloud Run service configs
│   └── helm/              # Kubernetes Helm charts
├── data/
│   └── seed/
│       ├── samples/       # 6 conflict scenarios (HR, JCPOA, Syria, commercial, labor, IP)
│       ├── frameworks.json
│       └── symbolic_rules.json
├── docs/
│   ├── mcp-setup.md       # Claude Desktop MCP integration guide
│   └── ...                # Architecture, ontology, deployment guides
├── .github/workflows/
│   └── ci.yml             # GitHub Actions: lint, test (4 packages), frontend typecheck
├── docker-compose.yml         # Full stack (Neo4j + Redis + API + Web + Qdrant + FalkorDB + MCP)
├── docker-compose.local.yml   # Minimal dev stack (Neo4j + Redis + API)
├── cloudbuild.yaml            # Cloud Build: test -> build -> push -> deploy -> verify
├── pyproject.toml             # UV workspace root
├── Makefile                   # 40+ targets for dev, test, build, deploy
└── .env.example               # All configuration variables documented
```

---

## API Reference

### Authentication
All requests require `X-API-Key` header. Public endpoints: `/health`, `/health/live`, `/health/ready`, `/docs`, `/v1/waitlist`.

### Key Endpoints

```
Health & Status
  GET    /health                              Full health with dependency checks
  GET    /health/live                         Liveness probe (always 200)
  GET    /health/ready                        Readiness probe (200 when Neo4j connected)

Workspaces
  POST   /v1/workspaces                       Create workspace
  GET    /v1/workspaces                       List workspaces (paginated)
  GET    /v1/workspaces/{id}                  Get workspace detail
  DELETE /v1/workspaces/{id}                  Delete workspace

Entities & Relationships
  GET    /v1/workspaces/{id}/entities         List entities (filter by ?type=Actor)
  GET    /v1/workspaces/{id}/entities/{eid}   Get entity detail
  GET    /v1/workspaces/{id}/relationships    List relationships

Extraction
  POST   /v1/workspaces/{id}/extract          Extract from text
  POST   /v1/workspaces/{id}/extract/document Upload PDF/DOCX

Graph
  GET    /v1/workspaces/{id}/graph            Full graph (nodes + edges)
  GET    /v1/workspaces/{id}/graph/subgraph   Subgraph from node with depth

Reasoning & Analysis
  POST   /v1/workspaces/{id}/analyze          Full conflict analysis
  POST   /v1/workspaces/{id}/reasoning        Specific mode (escalation, ripeness, trust, power, causal)

Theory
  GET    /v1/theory/frameworks                List 15 frameworks
  POST   /v1/theory/match                     Match frameworks to workspace

Admin
  GET    /v1/admin/system                     System info (admin only)
  GET    /v1/admin/usage                      Usage statistics

Developers
  POST   /v1/developers/keys                  Create API key
  GET    /v1/developers/keys                  List API keys

Waitlist
  POST   /v1/waitlist                         Join early access (public, no auth)
```

### Example: Extract from Text

```bash
curl -X POST http://localhost:8080/v1/workspaces/ws_hr/extract \
  -H "X-API-Key: dev-admin-key-local" \
  -H "Content-Type: application/json" \
  -d '{"text": "Sarah and Marcus are in a workplace dispute...", "tier": "standard"}'
```

---

## Testing

**596 tests across 4 Python packages:**

| Package | Tests | Coverage | What's tested |
|---------|-------|----------|---------------|
| ontology | 420 | 80% | Enums, primitives, relationships, tiers, symbolic rules, neurosymbolic, theory graph |
| api | 72 | — | Health, workspaces, entities, extraction, graph, reasoning, theory, admin, auth, tenancy |
| extraction | 75 | — | Pipeline chunking, GLiNER fallback, keyword detection, density, priority |
| reasoning | 29 | — | Escalation, ripeness, trust, firewall, power analysis, KGE availability |

```bash
make test              # Run all tests
make test-ontology     # Ontology only
make test-api          # API only
make test-extraction   # Extraction only
make test-reasoning    # Reasoning only
make test-e2e          # Playwright E2E (requires frontend running)
make quality-all       # lint + typecheck + tsc + web-lint
```

---

## MCP Server (Claude Desktop Integration)

DIALECTICA provides an MCP server with 5 conflict intelligence tools. See [docs/mcp-setup.md](docs/mcp-setup.md) for setup.

```json
{
  "mcpServers": {
    "dialectica": {
      "command": "python",
      "args": ["-m", "dialectica_mcp.server"],
      "env": {
        "GRAPH_BACKEND": "neo4j",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_PASSWORD": "your-password"
      }
    }
  }
}
```

**Tools:** `query_conflict_graph`, `get_actor_analysis`, `get_escalation_status`, `compare_conflicts`, `ingest_document`

---

## SDKs

### Python (ontology types)
```bash
pip install dialectica-ontology
```
```python
from dialectica_ontology import Actor, Conflict, Event
actor = Actor(name="Party A", actor_type="person")
```

### TypeScript
```bash
npm install @tacitus/dialectica-sdk
```
```typescript
import { createDialecticaClient } from "@tacitus/dialectica-sdk";
const client = createDialecticaClient({ apiKey: "dk_..." });
const workspaces = await client.workspaces.list();
```

---

## Feature Matrix

| Feature | Status | Description |
|---------|--------|-------------|
| Conflict Grammar Ontology | **Done** | 15 node types, 20 edge types, 25+ vocabularies, 80% test coverage |
| Multi-database support | **Done** | Neo4j Aura (primary) + FalkorDB + Spanner |
| Symbolic rules engine | **Done** | 25+ rules, firewall, escalation, ripeness, trust, power, causal |
| 6 AI agents | **Done** | Analyst, Advisor, Comparator, Forecaster, Mediator, Theorist |
| LangGraph extraction pipeline | **Done** | 10-step DAG with repair loop and validation |
| GraphRAG retrieval | **Done** | Hybrid: vector + graph + temporal + RRF |
| Sample data seeder | **Done** | 6 scenarios (HR, JCPOA, Syria, commercial, labor, IP), 114 nodes, 126 edges |
| FastAPI with auth | **Done** | 14 routers, rate limiting, multi-tenant, 72+ tests |
| Demo page (paste-and-see) | **Done** | ForceGraph visualization, 3 sample texts, fallback mode |
| Investor demo | **Done** | 5-step guided walkthrough with typewriter effect |
| Marketing landing page | **Done** | Hero, credibility, how-it-works, use cases, developer section |
| Auth (login/signup) | **Done** | localStorage-based (production-ready for Supabase/Clerk migration) |
| MCP server | **Done** | 5 tools for Claude Desktop integration |
| Cloud Run deployment | **Done** | Slim Dockerfile (<500MB), deploy script, Cloud Build pipeline |
| Vercel frontend deploy | **Done** | vercel.json, API proxy rewrites, SEO metadata |
| Health endpoints | **Done** | /health, /health/live, /health/ready with dependency checks |
| Waitlist/email capture | **Done** | POST /v1/waitlist (public endpoint) |
| CI/CD | **Done** | GitHub Actions (lint + 4 test suites) + Cloud Build |
| E2E tests | **Done** | Playwright: demo journey, landing page, sample texts |
| TypeScript SDK | **Done** | @tacitus/dialectica-sdk package configured |
| PLOVER event coding | **Done** | 16 types with severity nuances |
| Dual vector search | In Progress | Qdrant semantic (768d) + structural (256d) |
| PyKEEN KGE embeddings | In Progress | RotatE code exists, optional dep (requires torch) |
| ConfliBERT classifier | In Progress | Integration code exists, needs model deployment |
| ACLED/GDELT/UCDP connectors | In Progress | Connector code exists, needs live data integration |

---

## Environment Variables

See `.env.example` for the complete list. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `GRAPH_BACKEND` | `neo4j` | Graph database: `neo4j`, `spanner`, `falkordb` |
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection URI (use `neo4j+s://` for Aura) |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `dialectica-dev` | Neo4j password |
| `NEO4J_DATABASE` | `neo4j` | Neo4j database name |
| `ADMIN_API_KEY` | `dev-admin-key-...` | Admin API key (generate random for production) |
| `ENVIRONMENT` | `development` | `development` or `production` |
| `RATE_LIMIT_BACKEND` | `memory` | `memory` (dev) or `redis` (production) |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `CORS_ORIGINS` | `*` | Allowed CORS origins (comma-separated) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `GCP_PROJECT_ID` | `local-project` | GCP project for Vertex AI, Pub/Sub, etc. |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8080` | Backend API URL for the frontend |

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Follow conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `infra:`
4. Ensure `make quality-all` passes
5. Submit a pull request

---

## License

Apache 2.0 — see [LICENSE](LICENSE)

---

*DIALECTICA by TACITUS — Making conflict computable enough for better human judgment.*
