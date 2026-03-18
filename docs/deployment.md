# DIALECTICA Deployment Guide

Comprehensive guide for deploying DIALECTICA locally and to Google Cloud Platform.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Environment Variables Reference](#environment-variables-reference)
4. [Docker Compose Services](#docker-compose-services)
5. [GCP Deployment](#gcp-deployment)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Monitoring and Observability](#monitoring-and-observability)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| Python | 3.11+ (3.12 recommended) | API server, extraction pipeline, reasoning engine |
| Node.js | 18+ (20 recommended) | Next.js web application |
| Docker | 24+ | Container builds and local development |
| Docker Compose | v2+ | Multi-service local orchestration |
| Google Cloud SDK (`gcloud`) | Latest | GCP authentication and deployment |
| Terraform | 1.5.0+ | Infrastructure provisioning |

### Optional Software

| Tool | Purpose |
|------|---------|
| `ruff` | Python linting and formatting |
| `mypy` | Python type checking |
| `pytest` | Python test runner |
| `make` | Build automation via Makefile targets |

### GCP Account Requirements

- A Google Cloud project with billing enabled.
- Owner or Editor role on the project (for initial Terraform provisioning).
- The following APIs will be enabled automatically by Terraform:
  - Cloud Run (`run.googleapis.com`)
  - Cloud Spanner (`spanner.googleapis.com`)
  - Secret Manager (`secretmanager.googleapis.com`)
  - Cloud Storage (`storage.googleapis.com`)
  - Pub/Sub (`pubsub.googleapis.com`)
  - Artifact Registry (`artifactregistry.googleapis.com`)
  - Cloud Monitoring (`monitoring.googleapis.com`)
  - Cloud Logging (`logging.googleapis.com`)
  - Cloud Trace (`cloudtrace.googleapis.com`)
  - Vertex AI (`aiplatform.googleapis.com`)
  - IAM (`iam.googleapis.com`)

---

## Local Development Setup

### Quick Start

```bash
# 1. Clone the repository
git clone <repository-url>
cd A2_DIALECTICAbyTACITUS

# 2. Copy environment template
cp .env.example .env
# Edit .env with your values (see Environment Variables Reference below)

# 3. Start all services
make dev
```

This launches the Spanner emulator, Redis, initializes the database schema, starts the API on port 8080, and the web app on port 3000.

### Make Targets

#### Development

| Target | Description |
|--------|-------------|
| `make dev` | Start all services with docker-compose |
| `make dev-build` | Build images and start all services |
| `make dev-down` | Stop all services |
| `make dev-logs` | Follow logs for all services |
| `make dev-neo4j` | Start with Neo4j backend (API on port 8081) |
| `make dev-neo4j-build` | Build and start with Neo4j backend |

#### Installation

| Target | Description |
|--------|-------------|
| `make install` | Install all Python packages as editable (`pip install -e`) |
| `make install-web` | Install web app npm dependencies |
| `make install-dev` | Install all dependencies including dev tools (ruff, mypy, pytest) |

#### Testing

| Target | Description |
|--------|-------------|
| `make test` | Run all Python tests |
| `make test-unit` | Run unit tests only (excludes integration) |
| `make test-integration` | Run integration tests (requires Spanner emulator) |
| `make test-api` | Run API tests only |
| `make test-ontology` | Run ontology package tests |
| `make test-graph` | Run graph package tests |
| `make test-extraction` | Run extraction package tests |
| `make test-reasoning` | Run reasoning package tests |
| `make test-web` | Run Next.js tests |
| `make test-benchmark` | Run benchmark tests |
| `make benchmark` | Run JCPOA benchmark evaluation via live API |

#### Code Quality

| Target | Description |
|--------|-------------|
| `make lint` | Run ruff linter |
| `make lint-fix` | Run ruff linter with auto-fix |
| `make format` | Format code with ruff |
| `make typecheck` | Run mypy type checker |
| `make typecheck-strict` | Run mypy in strict mode |
| `make tsc` | TypeScript type check for web app |
| `make web-lint` | Lint Next.js app |
| `make quality` | Run all Python quality checks (lint + typecheck) |
| `make quality-all` | Run all quality checks (Python + TypeScript) |

#### Database and Seed Data

| Target | Description |
|--------|-------------|
| `make seed-schema` | Initialize Spanner schema |
| `make seed-frameworks` | Load theory frameworks into database |
| `make seed-samples` | Load JCPOA and other sample conflict graphs |
| `make seed` | Run all seed operations (schema + frameworks + samples) |
| `make create-admin-key` | Generate and store admin API key |

#### Build and Deploy

| Target | Description |
|--------|-------------|
| `make build-api` | Build API Docker image |
| `make build-web` | Build web Docker image |
| `make build` | Build all Docker images |
| `make docker-push` | Push images to Artifact Registry |
| `make deploy-api` | Deploy API to Cloud Run |
| `make deploy-web` | Deploy Web to Cloud Run |
| `make deploy` | Full deploy pipeline (build + push + deploy) |
| `make tf-init` | Initialize Terraform |
| `make tf-plan` | Plan Terraform changes |
| `make tf-apply` | Apply Terraform changes |
| `make tf-destroy` | Destroy Terraform resources |

#### Utilities

| Target | Description |
|--------|-------------|
| `make sdk-generate` | Generate TypeScript SDK from OpenAPI spec |
| `make sdk-build` | Generate and build TypeScript SDK |
| `make publish-ontology` | Build and publish ontology package to PyPI |
| `make clean` | Clean build artifacts (__pycache__, .mypy_cache, .next, etc.) |
| `make help` | Show all available targets |

### Running Without Docker

If you prefer to run services directly on your host machine:

```bash
# Install Python packages
make install
make install-dev

# Start Spanner emulator separately
docker run -p 9010:9010 -p 9020:9020 gcr.io/cloud-spanner-emulator/emulator:latest

# Set emulator env vars
export SPANNER_EMULATOR_HOST=localhost:9010
export GCP_PROJECT_ID=local-project
export SPANNER_INSTANCE_ID=dialectica-graph
export SPANNER_DATABASE_ID=dialectica

# Initialize schema
make seed-schema

# Start the API
cd packages/api && uvicorn dialectica_api.main:app --host 0.0.0.0 --port 8080 --reload

# In another terminal, start the web app
cd apps/web && npm install && npm run dev
```

---

## Environment Variables Reference

Copy `.env.example` to `.env` and configure the following variables. Never commit `.env` to version control.

### Google Cloud Platform

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GCP_PROJECT_ID` | Yes | — | Your GCP project ID |
| `GOOGLE_APPLICATION_CREDENTIALS` | Dev only | — | Path to service account key file. In Cloud Run, use Workload Identity instead. |

### Cloud Spanner

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SPANNER_INSTANCE_ID` | No | `dialectica-graph` | Spanner instance ID |
| `SPANNER_DATABASE_ID` | No | `dialectica` | Spanner database ID |
| `SPANNER_EMULATOR_HOST` | Dev only | — | Set to `localhost:9010` for local emulator (docker-compose sets this automatically) |

### Vertex AI

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VERTEX_AI_LOCATION` | No | `us-east1` | Vertex AI region |
| `GEMINI_FLASH_MODEL` | No | `gemini-2.5-flash-001` | Gemini Flash model for entity extraction |
| `GEMINI_PRO_MODEL` | No | `gemini-2.5-pro-001` | Gemini Pro model for reasoning synthesis |
| `EMBEDDING_MODEL` | No | `text-embedding-005` | Text embedding model |
| `EMBEDDING_DIMENSIONS` | No | `768` | Embedding vector dimensions |

### Graph Backend

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GRAPH_BACKEND` | No | `spanner` | Primary backend: `spanner` or `neo4j` |
| `NEO4J_URI` | If neo4j | `bolt://localhost:7687` | Neo4j Bolt connection URI |
| `NEO4J_USER` | If neo4j | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | If neo4j | — | Neo4j password |
| `FALKORDB_HOST` | Optional | `localhost` | FalkorDB host (alternative backend) |
| `FALKORDB_PORT` | Optional | `6379` | FalkorDB port |

### API Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ADMIN_API_KEY` | Yes (prod) | `dev-admin-key-change-in-production` | Admin API key. Must be changed in production. |
| `LOG_LEVEL` | No | `INFO` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated allowed CORS origins |
| `RATE_LIMIT_DEFAULT` | No | `60` | Default rate limit (requests per minute per key) |
| `RATE_LIMIT_EXTRACT` | No | `10` | Extraction endpoint rate limit |
| `RATE_LIMIT_REASON` | No | `20` | Reasoning endpoint rate limit |

### Environment and Auth Hardening

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | No | `development` | `development` or `production`. In production, default admin key is rejected. |
| `RATE_LIMIT_BACKEND` | No | `memory` | `memory` (single process, dev) or `redis` (production) |
| `REDIS_URL` | If redis | `redis://localhost:6379` | Redis connection URL |
| `API_KEYS_JSON` | No | `[]` | JSON array of API key definitions. Each entry: `{"key": "...", "level": "admin|standard|readonly", "tenant_id": "...", "expires_at": null}` |

### Web Application

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | No | `http://localhost:8080` | API URL for the web app |
| `NODE_ENV` | No | `development` | Node environment |

### Pub/Sub (Async Extraction)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PUBSUB_EXTRACTION_TOPIC` | No | `dialectica-extraction-requests` | Topic for async extraction jobs |
| `PUBSUB_EXTRACTION_SUBSCRIPTION` | No | `dialectica-extraction-worker` | Subscription for extraction workers |
| `PUBSUB_DLQ_TOPIC` | No | `dialectica-extraction-dlq` | Dead letter queue topic |

### Cloud Storage

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GCS_DOCUMENTS_BUCKET` | No | `${GCP_PROJECT_ID}-dialectica-documents` | Bucket for uploaded documents |

### GLiNER (Entity Pre-filtering)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GLINER_MODEL` | No | `gliner-community/gliner_medium-v2.5` | GLiNER model name (~500 MB, downloads on first use) |
| `GLINER_THRESHOLD` | No | `0.4` | Entity detection confidence threshold |
| `GLINER_ENABLED` | No | `true` | Enable/disable GLiNER pre-filtering |

### Extraction Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEFAULT_EXTRACTION_TIER` | No | `standard` | Default ontology tier: `essential`, `standard`, `full` |
| `MAX_DOCUMENT_SIZE` | No | `10485760` (10 MB) | Maximum document size in bytes |
| `CHUNK_SIZE` | No | `2000` | Chunk size for large document processing |
| `CHUNK_OVERLAP` | No | `200` | Overlap between chunks |
| `MAX_EXTRACTION_RETRIES` | No | `3` | Maximum extraction retries on validation failure |

---

## Docker Compose Services

The `docker-compose.yml` defines the following services on the `dialectica-network` Docker network.

### Default Services

| Service | Image | Ports | Role |
|---------|-------|-------|------|
| `redis` | `redis:7-alpine` | 6379 | Rate limiting and caching. Configured with 128 MB max memory and LRU eviction. |
| `spanner-emulator` | `gcr.io/cloud-spanner-emulator/emulator:latest` | 9010 (gRPC), 9020 (REST) | Local Cloud Spanner emulator for development. |
| `spanner-init` | `python:3.12-slim` (one-shot) | — | Runs `init_spanner.py` to create instance, database, and schema. Exits after completion. |
| `api` | Built from `packages/api/Dockerfile` | 8080 | DIALECTICA FastAPI server. Depends on Spanner emulator and Redis being healthy. |
| `web` | Built from `apps/web/Dockerfile` | 3000 | Next.js web application. Depends on API being healthy. |

### Neo4j Profile Services

Activated with `docker-compose --profile neo4j up` or `make dev-neo4j`.

| Service | Image | Ports | Role |
|---------|-------|-------|------|
| `neo4j` | `neo4j:5-community` | 7474 (Browser), 7687 (Bolt) | Neo4j graph database with APOC plugin. |
| `api-neo4j` | Built from `packages/api/Dockerfile` | 8081 | API variant configured with `GRAPH_BACKEND=neo4j`. Runs on port 8081 to avoid conflict with default API. |

### Health Checks

All persistent services have health checks configured:

- **Redis**: `redis-cli ping` every 10 seconds.
- **Spanner emulator**: HTTP GET to REST endpoint every 10 seconds.
- **API**: HTTP GET to `/health` every 15 seconds (30-second start period).
- **Neo4j**: Cypher shell `RETURN 1` every 15 seconds (30-second start period).

### Service Dependency Chain

```
redis ─────────────────┐
                       ├──> api ──> web
spanner-emulator ──> spanner-init ─┘
```

The `spanner-init` container waits for the emulator to be healthy, initializes the schema, then exits. The API waits for both the emulator and Redis to be healthy before starting. The web app waits for the API health check to pass.

---

## GCP Deployment

### Infrastructure Overview

All GCP resources are defined in Terraform under `infrastructure/terraform/`. The deployment targets the following GCP services:

| Resource | Terraform File | Description |
|----------|---------------|-------------|
| Artifact Registry | `main.tf` | Docker image repository at `{region}-docker.pkg.dev/{project}/dialectica` |
| Cloud Run (API) | `cloud_run.tf` | FastAPI service: 2 CPU, 2 Gi memory, autoscale 1-10 instances |
| Cloud Run (Web) | `cloud_run.tf` | Next.js app: 1 CPU, 512 Mi memory, autoscale 1-5 instances |
| Cloud Spanner | `spanner.tf` | Instance `dialectica-graph` with configurable processing units (default: 100 PU) |
| Secret Manager | `secrets.tf` | Stores `dialectica-admin-api-key` with automatic replication |
| Cloud Storage | `storage.tf` | Two buckets: `{project}-dialectica-documents` (365-day Nearline lifecycle) and `{project}-dialectica-exports` (90-day deletion) |
| Pub/Sub | `pubsub.tf` | Topics for async extraction (`dialectica-extraction-jobs`) and ingest events, with dead letter policy (5 max delivery attempts) |
| Cloud Monitoring | `monitoring.tf` | Operations dashboard (p99 latency, request count) and 5xx error rate alert policy |
| IAM | `iam.tf` | Dedicated service accounts for API and Web with least-privilege roles |

### IAM Configuration

Two service accounts are created with the following roles:

**API Service Account** (`dialectica-api`):
- `roles/spanner.databaseUser` -- Read/write access to Spanner
- `roles/secretmanager.secretAccessor` -- Read secrets from Secret Manager
- `roles/aiplatform.user` -- Access Vertex AI models
- `roles/pubsub.publisher` -- Publish to Pub/Sub topics
- `roles/storage.objectAdmin` -- Read/write to Cloud Storage
- `roles/logging.logWriter` -- Write to Cloud Logging
- `roles/cloudtrace.agent` -- Write to Cloud Trace

**Web Service Account** (`dialectica-web`):
- No additional IAM roles (communicates with API over HTTP)

### Terraform Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `project_id` | Yes | — | GCP project ID |
| `region` | No | `us-east1` | Primary GCP region |
| `environment` | No | `prod` | `dev`, `staging`, or `prod` |
| `image_tag` | No | `latest` | Docker image tag to deploy |
| `api_min_instances` | No | `1` | Minimum Cloud Run instances for API |
| `api_max_instances` | No | `10` | Maximum Cloud Run instances for API |
| `web_min_instances` | No | `1` | Minimum Cloud Run instances for Web |
| `web_max_instances` | No | `5` | Maximum Cloud Run instances for Web |
| `spanner_processing_units` | No | `100` | Spanner processing units (100 = minimum billable) |
| `admin_api_key` | Yes | — | Admin API key (stored in Secret Manager, marked sensitive) |
| `cors_origins` | No | Web service URL | Allowed CORS origins |
| `gemini_flash_model` | No | `gemini-2.5-flash-001` | Vertex AI Gemini Flash model ID |
| `gemini_pro_model` | No | `gemini-2.5-pro-001` | Vertex AI Gemini Pro model ID |
| `vertex_ai_location` | No | `us-east1` | Vertex AI location |

### Step-by-Step GCP Deployment

#### 1. Authenticate with GCP

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

#### 2. Initialize Terraform

```bash
make tf-init
# or
cd infrastructure/terraform && terraform init
```

To use a remote state backend for team collaboration, uncomment the `backend "gcs"` block in `main.tf` and create the state bucket first:

```bash
gsutil mb gs://dialectica-terraform-state
```

#### 3. Create a Terraform Variables File

Create `infrastructure/terraform/terraform.tfvars`:

```hcl
project_id    = "your-gcp-project-id"
region        = "us-east1"
environment   = "prod"
admin_api_key = "your-secure-random-api-key"
```

Never commit `terraform.tfvars` to version control.

#### 4. Plan and Apply Infrastructure

```bash
make tf-plan
# Review the plan carefully, then:
make tf-apply
```

This provisions all GCP resources: Spanner instance, Cloud Storage buckets, Pub/Sub topics, Secret Manager secrets, Artifact Registry, monitoring dashboards, and alert policies.

#### 5. Build and Push Docker Images

```bash
# Configure Docker for Artifact Registry
gcloud auth configure-docker us-east1-docker.pkg.dev

# Build and push
make build docker-push
```

#### 6. Deploy to Cloud Run

```bash
make deploy-api deploy-web
# or the combined target:
make deploy
```

#### 7. Initialize the Database Schema

After deploying, run the schema initialization against the production Spanner instance:

```bash
# Ensure SPANNER_EMULATOR_HOST is NOT set
unset SPANNER_EMULATOR_HOST
export GCP_PROJECT_ID=your-gcp-project-id
export SPANNER_INSTANCE_ID=dialectica-graph
export SPANNER_DATABASE_ID=dialectica

make seed-schema
make seed-frameworks
```

#### 8. Verify Deployment

```bash
# Get the API URL
gcloud run services describe dialectica-api --region us-east1 --format 'value(status.url)'

# Check health
curl https://YOUR_API_URL/health
```

### Terraform Outputs

After `terraform apply`, the following outputs are available:

| Output | Description |
|--------|-------------|
| `api_url` | DIALECTICA API Cloud Run URL |
| `web_url` | DIALECTICA Web Cloud Run URL |
| `spanner_instance` | Cloud Spanner instance name |
| `spanner_database` | Cloud Spanner database name |
| `artifact_registry` | Artifact Registry repository URL |
| `documents_bucket` | GCS bucket name for document uploads |
| `api_service_account` | API service account email |

```bash
cd infrastructure/terraform && terraform output
```

### Cloud Run Configuration Details

**API Service** (`dialectica-api`):
- Container port: 8080
- Resources: 2 CPU, 2 Gi memory
- CPU idle enabled (scales to zero CPU between requests)
- Startup CPU boost enabled
- Startup probe: HTTP GET `/health:8080`, 10s initial delay, 3 failure threshold
- Liveness probe: HTTP GET `/health:8080`, 30s initial delay, 3 failure threshold
- Secrets injected via `secret_key_ref` (not environment variables)
- Ingress: all traffic
- Authentication: application-level API key auth (IAM set to allUsers for Cloud Run invoker)

**Web Service** (`dialectica-web`):
- Container port: 3000
- Resources: 1 CPU, 512 Mi memory
- CPU idle enabled
- `NEXT_PUBLIC_API_URL` automatically set to the API service URI
- Authentication: public (allUsers)

---

## CI/CD Pipeline

### CI Workflow (`.github/workflows/ci.yml`)

Triggers on push or pull request to `main` and `develop` branches. Uses concurrency groups to cancel in-progress runs on the same branch.

| Job | Runs On | Description |
|-----|---------|-------------|
| `python-lint` | ubuntu-latest | Runs `ruff check`, `ruff format --check`, and `mypy` (non-blocking) against `packages/` |
| `python-tests` | ubuntu-latest | Runs `pytest` with Spanner emulator service container, generates coverage XML, uploads to Codecov |
| `frontend-lint` | ubuntu-latest | Runs TypeScript type check (`tsc --noEmit`) and Next.js lint |
| `frontend-build` | ubuntu-latest | Builds the Next.js app (`npm run build`). Depends on `frontend-lint`. |
| `sdk-verify` | ubuntu-latest | Generates OpenAPI spec from the FastAPI app, generates TypeScript types, and type-checks the SDK |
| `docker-build` | ubuntu-latest | Builds API and Web Docker images (no push). Only on `push` events. Depends on `python-tests` and `frontend-build`. Uses GitHub Actions cache. |

#### CI Environment

- Python version: 3.12
- Node.js version: 20
- Spanner emulator runs as a GitHub Actions service container on ports 9010/9020.

### Deploy Workflow (`.github/workflows/deploy.yml`)

Triggers on push to `main` or version tags (`v*`). Uses concurrency groups with `cancel-in-progress: false` to ensure deployments complete.

#### Deploy Steps

1. **Authenticate** via Workload Identity Federation (no service account key files). Requires `GCP_WORKLOAD_IDENTITY_PROVIDER` and `GCP_SERVICE_ACCOUNT` as repository secrets.
2. **Configure Docker** for Artifact Registry.
3. **Determine image tag**: version tag (`v1.0.0`) or `latest-{short-sha}` for branch pushes.
4. **Build and push API image** to Artifact Registry with registry-level build cache.
5. **Build and push Web image** with `NEXT_PUBLIC_API_URL` build arg.
6. **Deploy API to Cloud Run** with `--no-allow-unauthenticated`, dedicated service account, Spanner config, and secret injection.
7. **Get API URL** from the deployed service.
8. **Deploy Web to Cloud Run** with `--allow-unauthenticated` and `NEXT_PUBLIC_API_URL` set to the API URL.
9. **Post-deployment health check**: 5 retries with 10-second intervals against `/health`.
10. **Output deployment URLs** to the GitHub Actions step summary.

### Required GitHub Configuration

#### Repository Secrets

| Secret | Description |
|--------|-------------|
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | Workload Identity Federation provider (e.g., `projects/123/locations/global/workloadIdentityPools/github/providers/github`) |
| `GCP_SERVICE_ACCOUNT` | GCP service account email for CI/CD |

#### Repository Variables

| Variable | Description |
|----------|-------------|
| `GCP_PROJECT_ID` | GCP project ID |
| `GCP_REGION` | GCP region (defaults to `us-east1`) |
| `CLOUD_RUN_DOMAIN` | Custom domain suffix for Cloud Run URLs (used in build args) |

### Setting Up Workload Identity Federation

To avoid storing service account keys in GitHub, configure Workload Identity Federation:

```bash
# Create a Workload Identity Pool
gcloud iam workload-identity-pools create github \
  --location="global" \
  --display-name="GitHub Actions"

# Create a Provider
gcloud iam workload-identity-pools providers create-oidc github \
  --location="global" \
  --workload-identity-pool="github" \
  --display-name="GitHub" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Allow the GitHub repo to impersonate the service account
gcloud iam service-accounts add-iam-policy-binding \
  YOUR_SERVICE_ACCOUNT@YOUR_PROJECT.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github/attribute.repository/YOUR_ORG/YOUR_REPO"
```

---

## Monitoring and Observability

### Health Endpoints

The API exposes a `/health` endpoint used by:
- Docker Compose health checks (every 15 seconds)
- Cloud Run startup probe (10-second initial delay, 10-second period)
- Cloud Run liveness probe (30-second initial delay, 30-second period)
- Post-deployment verification in the CI/CD pipeline

### Cloud Monitoring Dashboard

Terraform provisions a "DIALECTICA Operations Dashboard" with two tiles:

1. **API Request Latency (p99)** -- 99th percentile request latency for the `dialectica-api` Cloud Run service, aligned at 60-second intervals.
2. **API Request Count** -- Request rate for the `dialectica-api` Cloud Run service, aligned at 60-second intervals.

Access the dashboard at: `https://console.cloud.google.com/monitoring/dashboards` in your GCP project.

### Alert Policies

A **High Error Rate** alert policy fires when the 5xx error rate for `dialectica-api` exceeds 1% over a 5-minute window. Configure notification channels (email, Slack, PagerDuty) in the GCP console or by adding channel IDs to the `notification_channels` list in `monitoring.tf`.

### Structured Logging

The API uses `LoggingMiddleware` that outputs structured JSON logs. In production on Cloud Run, these logs are automatically ingested into Cloud Logging. Query logs at:

```
https://console.cloud.google.com/logs/query;query=resource.type%3D%22cloud_run_revision%22%20resource.labels.service_name%3D%22dialectica-api%22
```

### Cloud Trace

The API service account has `roles/cloudtrace.agent` for distributed tracing. Traces are viewable in the Cloud Trace console.

### Application-Level Metrics

- **Rate limiting**: The `RateLimitMiddleware` tracks per-key request counts. With `RATE_LIMIT_BACKEND=redis`, counts are shared across instances.
- **Usage tracking**: The `UsageMiddleware` records API usage per key.
- **Extraction pipeline**: Each pipeline step reports timing and entity counts in logs.

### Key Metrics to Monitor

| Metric | Source | Warning Threshold |
|--------|--------|-------------------|
| API p99 latency | Cloud Monitoring | > 5 seconds |
| 5xx error rate | Cloud Monitoring alert | > 1% |
| Cloud Run instance count | Cloud Run metrics | Approaching `max_instances` |
| Spanner CPU utilization | Spanner metrics | > 75% |
| Spanner storage | Spanner metrics | Check billing implications |
| Pub/Sub dead letter count | Pub/Sub metrics | Any messages in DLQ |

---

## Troubleshooting

### Local Development

#### Spanner emulator fails to start

```
ERROR: spanner-emulator health check failed
```

- Ensure ports 9010 and 9020 are not in use: `lsof -i :9010` and `lsof -i :9020`.
- Try restarting with a clean state: `make dev-down && docker volume prune -f && make dev`.
- Check Docker has sufficient memory allocated (at least 4 GB recommended).

#### `spanner-init` container keeps restarting

The init container depends on the emulator being healthy. If it fails:
- Check logs: `docker logs dialectica-spanner-init`.
- The container installs `google-cloud-spanner` on every run. If your network is slow, it may time out.
- The container will retry on failure (`restart: on-failure`). Give it a few attempts.

#### API cannot connect to Spanner emulator

- Verify `SPANNER_EMULATOR_HOST` is set correctly. Inside Docker Compose, it should be `spanner-emulator:9010` (service name, not `localhost`).
- If running the API outside Docker, use `localhost:9010`.

#### Redis connection refused

- Ensure Redis is running: `docker ps | grep dialectica-redis`.
- For local development without Docker, start Redis manually or set `RATE_LIMIT_BACKEND=memory` in `.env`.

#### CORS errors in the browser

- Check that `CORS_ORIGINS` includes your frontend URL (default: `http://localhost:3000`).
- Ensure you are not mixing `http` and `https` or including trailing slashes.

#### GLiNER model download is slow or fails

- The GLiNER model (~500 MB) downloads on first use.
- Set `GLINER_ENABLED=false` to skip pre-filtering during development.
- If behind a proxy, configure `HTTP_PROXY` and `HTTPS_PROXY` environment variables.

#### Neo4j profile: API on port 8081 not starting

- Ensure Neo4j is healthy first: visit `http://localhost:7474` in your browser.
- Default credentials are `neo4j/dialectica-dev`.
- Check logs: `docker logs dialectica-api-neo4j`.

### GCP Deployment

#### Terraform `apply` fails with API not enabled

```
Error: Error when reading or editing Resource: googleapi: Error 403: ... has not been used in project ... before or it is disabled.
```

Terraform enables APIs automatically, but propagation can take a few minutes. Re-run `make tf-apply`.

#### Cloud Run deployment fails with permission denied

- Verify the deploying account has `roles/run.admin` and `roles/iam.serviceAccountUser`.
- For CI/CD, verify Workload Identity Federation is configured correctly and the service account has the required roles.

#### API returns 503 after deployment

- The API has a 30-second startup period. Wait and retry.
- Check Cloud Run logs: `gcloud run services logs read dialectica-api --region us-east1`.
- Verify the Spanner instance exists and the service account has `roles/spanner.databaseUser`.

#### Secret Manager access denied

```
Error: Permission denied on resource 'projects/.../secrets/dialectica-admin-api-key'
```

Ensure the API service account has `roles/secretmanager.secretAccessor`:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT \
  --member="serviceAccount:dialectica-api@YOUR_PROJECT.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

#### Spanner connection timeout in production

- Ensure `SPANNER_EMULATOR_HOST` is NOT set in production. This variable forces the client to connect to the emulator instead of real Spanner.
- Verify the Spanner instance is in the same region as Cloud Run.
- Check that the database schema has been initialized (`make seed-schema` against production).

#### Images fail to push to Artifact Registry

```
denied: Permission "artifactregistry.repositories.uploadArtifacts" denied
```

- Configure Docker authentication: `gcloud auth configure-docker us-east1-docker.pkg.dev`.
- Ensure the Artifact Registry repository exists (created by Terraform).
- Verify the pushing account has `roles/artifactregistry.writer`.

#### Pub/Sub messages accumulating in dead letter queue

- Check the extraction worker logs for errors.
- Messages retry up to 5 times with exponential backoff (10s to 300s).
- Investigate the DLQ topic `dialectica-ingest-events` for failed message payloads.

#### High Spanner costs

- The default 100 processing units is the minimum billable amount.
- For development/staging, consider using the Spanner emulator instead of a real instance.
- Spanner deletion protection is enabled in `prod` environment. Set `environment = "dev"` or `"staging"` for non-production to allow teardown with `terraform destroy`.
