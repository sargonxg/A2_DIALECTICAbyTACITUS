# Cloud Run Deployment

Last updated: 2026-05-03

## Runtime Model

Dialectica API is stateless on Cloud Run. Neo4j must be external, typically
Neo4j Aura via `neo4j+s://...`. Cloud SQL is the durable metadata and pipeline
audit store: it tracks ingestion runs, source chunks, dynamic ontology profiles,
graph object mirrors, graph edge mirrors, and partial failures. The optional
graph reasoning subsystem stores source-of-truth graph data in Neo4j, writes
Graphiti-compatible temporal episode metadata into the same Neo4j database, and
keeps Cozo as a rebuildable reasoning mirror.

Cloud Run must not depend on local persistent disk. `COZO_SNAPSHOT_PATH` is only
for local development. Use Neo4j as the durable recovery source.

## Required Secrets

Create these Secret Manager secrets before deploy:

```bash
printf '%s' 'neo4j+s://YOUR-AURA.databases.neo4j.io' | \
  gcloud secrets create dialectica-neo4j-uri --data-file=-

printf '%s' 'neo4j' | \
  gcloud secrets create dialectica-neo4j-user --data-file=-

printf '%s' 'neo4j' | \
  gcloud secrets create dialectica-neo4j-username --data-file=-

printf '%s' 'YOUR_NEO4J_PASSWORD' | \
  gcloud secrets create dialectica-neo4j-password --data-file=-

printf '%s' 'neo4j' | \
  gcloud secrets create dialectica-neo4j-database --data-file=-

printf '%s' 'YOUR_GEMINI_API_KEY' | \
  gcloud secrets create dialectica-gemini-api-key --data-file=-

openssl rand -hex 32 | \
  gcloud secrets create dialectica-admin-key --data-file=-

printf '%s' 'postgresql+asyncpg://dialectica:PASSWORD@/dialectica?host=/cloudsql/PROJECT:REGION:INSTANCE' | \
  gcloud secrets create dialectica-database-url --data-file=-
```

## Required Env Vars

- `ENVIRONMENT=production`
- `GRAPH_BACKEND=neo4j`
- `DATABASE_URL=<Secret Manager: dialectica-database-url>`
- `CLOUD_SQL_CONNECTION_NAME=PROJECT:REGION:INSTANCE`
- `NEO4J_DATABASE=<Secret Manager: dialectica-neo4j-database>`
- `NEO4J_USER=<Secret Manager: dialectica-neo4j-user>`
- `NEO4J_USERNAME=<Secret Manager: dialectica-neo4j-username>`
- `GEMINI_API_KEY=<Secret Manager: dialectica-gemini-api-key>`
- `GOOGLE_AI_API_KEY=<Secret Manager: dialectica-gemini-api-key>`
- `RATE_LIMIT_BACKEND=memory` or `redis` if Redis is provisioned
- `GRAPHITI_USE_NATIVE=false` unless native Graphiti LLM/embedder credentials are configured
- `OPENAI_API_KEY=<secret>` if Graphiti's default native clients are used
- `COZO_USE_EMBEDDED=true` for the embedded Cozo relation mirror, or `false` for the in-process fallback
- `COZO_ENGINE=mem`
- `COZO_PATH=` empty on Cloud Run
- `COZO_OPTIONS={}`
- `COZO_SNAPSHOT_PATH=` empty on Cloud Run
- `GRAPH_REASONING_CHUNK_CHARS=6000`
- `NEO4J_CONNECTION_TIMEOUT=5`
- `CORS_ORIGINS=<allowed origins>`
- `GCP_PROJECT_ID=<project id>`

## Build And Deploy

```bash
PROJECT_ID=your-project
REGION=us-central1
SERVICE=dialectica-api
REPO=dialectica
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/api:latest"

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  sqladmin.googleapis.com \
  --project "$PROJECT_ID"

gcloud artifacts repositories create "$REPO" \
  --repository-format=docker \
  --location "$REGION" \
  --project "$PROJECT_ID" || true

gcloud builds submit \
  --tag "$IMAGE" \
  --project "$PROJECT_ID" \
  -f packages/api/Dockerfile.cloudrun .

gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 1 \
  --concurrency 40 \
  --cpu 1 \
  --memory 1Gi \
  --cpu-throttling \
  --no-cpu-boost \
  --timeout 300 \
  --add-cloudsql-instances "$PROJECT_ID:$REGION:dialectica" \
  --set-env-vars "ENVIRONMENT=production,GRAPH_BACKEND=neo4j,NEO4J_CONNECTION_TIMEOUT=5,RATE_LIMIT_BACKEND=memory,GRAPHITI_USE_NATIVE=false,COZO_USE_EMBEDDED=true,COZO_ENGINE=mem,COZO_PATH=,COZO_OPTIONS={},COZO_SNAPSHOT_PATH=,GRAPH_REASONING_CHUNK_CHARS=6000,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:dialectica,GCP_PROJECT_ID=$PROJECT_ID" \
  --set-secrets "DATABASE_URL=dialectica-database-url:latest,NEO4J_URI=dialectica-neo4j-uri:latest,NEO4J_USER=dialectica-neo4j-user:latest,NEO4J_USERNAME=dialectica-neo4j-username:latest,NEO4J_PASSWORD=dialectica-neo4j-password:latest,NEO4J_DATABASE=dialectica-neo4j-database:latest,GEMINI_API_KEY=dialectica-gemini-api-key:latest,GOOGLE_AI_API_KEY=dialectica-gemini-api-key:latest,ADMIN_API_KEY=dialectica-admin-key:latest" \
  --project "$PROJECT_ID"
```

The helper scripts support the same setup:

```bash
bash infrastructure/scripts/setup-secrets.sh "$PROJECT_ID"
CLOUD_SQL_CONNECTION_NAME="$PROJECT_ID:$REGION:dialectica" \
  bash infrastructure/scripts/deploy-cloudrun.sh "$PROJECT_ID" "$REGION"
```

The Docker command uses `${PORT:-8080}`, so it is compatible with Cloud Run's
runtime port injection.

## Smoke Tests

```bash
API_URL="$(gcloud run services describe dialectica-api \
  --region us-central1 \
  --project "$PROJECT_ID" \
  --format='value(status.url)')"

curl "$API_URL/health"

ADMIN_API_KEY="$(gcloud secrets versions access latest \
  --secret dialectica-admin-key \
  --project "$PROJECT_ID")"

curl -X POST "$API_URL/ingest/text" \
  -H "X-API-Key: $ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id":"cloudrun-demo","source_title":"smoke","text":"Alice will meet Bob. Bob must accept the deadline."}'

curl "$API_URL/graph/search?q=Alice&workspace_id=cloudrun-demo" \
  -H "X-API-Key: $ADMIN_API_KEY"

curl "$API_URL/pipeline/runs?workspace_id=cloudrun-demo" \
  -H "X-API-Key: $ADMIN_API_KEY"
```

Expected `/health` checks include:

- `graph_reasoning:neo4j`
- `graph_reasoning:graphiti`
- `graph_reasoning:cozo`
- `cloud_sql`

## Known Limitations

- Native Graphiti is optional. In compatibility mode, the subsystem writes
  temporal episode/provenance records directly to Neo4j. Native mode should only
  be enabled after LLM/embedder credentials are configured.
- Native CozoDB is available through `cozo-embedded`. In Cloud Run, use `mem`
  unless you add an explicit snapshot hydrate/flush flow. Neo4j remains authoritative.
- With multiple Cloud Run instances, each instance has its own mirror cache.
  Reasoning endpoints refresh from Neo4j when the requested data is missing.
- Cloud SQL is not a graph source of truth. It is the audit/control plane and
  rebuild ledger for ingestion. Stopping Cloud SQL saves idle spend but disables
  durable run history until it is started again.

## Cost Controls

The deployment defaults are cold-start safe and cost-first:

- Cloud Run uses `--min-instances 0`, so idle API cost is zero.
- Cloud Run uses `--max-instances 1` by default to prevent runaway traffic spend.
- CPU is throttled between requests and startup CPU boost is disabled.
- Cozo runs as a rebuildable in-memory mirror. Do not attach persistent disk on
  Cloud Run for Cozo.
- Neo4j Aura is the durable graph store. Cloud SQL should be one small shared
  instance without HA/read replicas for the durable audit/control plane.
- Databricks is optional for lakehouse-scale batch work. The API can chunk and
  ingest large text directly without Databricks, then later replay from Cloud
  SQL/Neo4j into Databricks if needed.
- Spanner, Redis, BigQuery, and Vertex endpoints are not required for the
  cost-saver backend.

Do not use the full Terraform stack for a cost-saver deploy unless you intend to
pay for its billable resources. The direct Cloud Run script deploys only Cloud
Run, Artifact Registry, and Secret Manager plus external Neo4j.
