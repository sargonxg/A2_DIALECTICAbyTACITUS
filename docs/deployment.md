# DIALECTICA Deployment Guide

Comprehensive guide for deploying DIALECTICA to Google Cloud Platform.

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Google Cloud SDK | latest | `curl https://sdk.cloud.google.com \| bash` |
| Terraform | >= 1.5 | `brew install terraform` |
| Helm | >= 3.0 | `brew install helm` |
| Docker | >= 24.0 | Docker Desktop |
| UV | latest | `pip install uv` |
| kubectl | latest | `gcloud components install kubectl` |

## GCP Project Setup

```bash
# Set project
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  container.googleapis.com \
  spanner.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com \
  pubsub.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com
```

## Step 1: Terraform Infrastructure

```bash
cd infrastructure/terraform/environments/dev

# Initialize
terraform init

# Plan
terraform plan -var="project_id=$PROJECT_ID"

# Apply
terraform apply -var="project_id=$PROJECT_ID"
```

This provisions: VPC, Cloud NAT, service accounts, IAM roles, Pub/Sub topics, Secret Manager, Artifact Registry.

## Step 2: Helm Charts (if using GKE)

```bash
# Get GKE credentials
gcloud container clusters get-credentials dialectica-dev --region us-east1

# Deploy stateful services
bash infrastructure/scripts/deploy_helm.sh
```

## Step 3: Build Docker Images

```bash
# Build all images
docker build -f packages/api/Dockerfile -t $REGION-docker.pkg.dev/$PROJECT_ID/dialectica/api:latest .
docker build -f packages/extraction/Dockerfile -t $REGION-docker.pkg.dev/$PROJECT_ID/dialectica/extraction-worker:latest .
docker build -f packages/mcp/Dockerfile -t $REGION-docker.pkg.dev/$PROJECT_ID/dialectica/mcp-server:latest .

# Push to Artifact Registry
gcloud auth configure-docker $REGION-docker.pkg.dev
docker push $REGION-docker.pkg.dev/$PROJECT_ID/dialectica/api:latest
docker push $REGION-docker.pkg.dev/$PROJECT_ID/dialectica/extraction-worker:latest
docker push $REGION-docker.pkg.dev/$PROJECT_ID/dialectica/mcp-server:latest
```

## Step 4: Deploy to Cloud Run

```bash
# API
gcloud run deploy dialectica-api \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/dialectica/api:latest \
  --region $REGION --allow-unauthenticated

# Extraction Worker
gcloud run deploy dialectica-extraction-worker \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/dialectica/extraction-worker:latest \
  --region $REGION --no-allow-unauthenticated

# MCP Server
gcloud run deploy dialectica-mcp-server \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/dialectica/mcp-server:latest \
  --region $REGION --allow-unauthenticated
```

## Step 5: BigQuery Analytics Setup (Optional)

If you want longitudinal analytics on extraction quality, query patterns, and
benchmark results, enable BigQuery.

### 5.1 Terraform provisions the dataset

If you ran `terraform apply` in Step 1, the `dialectica_analytics` dataset and
three tables are already created. Verify:

```bash
bq ls --project_id=$PROJECT_ID
# Expected: dialectica_analytics

bq ls $PROJECT_ID:dialectica_analytics
# Expected: extraction_events, query_events, benchmark_results
```

### 5.2 Configure the API

Add these environment variables to your Cloud Run service:

```bash
gcloud run services update dialectica-api \
  --region=$REGION \
  --update-env-vars="BIGQUERY_ENABLED=true,BIGQUERY_DATASET=dialectica_analytics"
```

### 5.3 Verify data flow

Run an extraction and check BigQuery:

```bash
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) as events FROM \`$PROJECT_ID.dialectica_analytics.extraction_events\`"
```

---

## Step 6: Databricks Integration (Optional)

For advanced ML workloads (KGE training, graph analytics at scale), connect
DIALECTICA to a Databricks workspace.

### 6.1 Prerequisites

- Databricks workspace on GCP
- Personal access token or service account token
- Running cluster with PyTorch and PyKEEN

### 6.2 Configure

```bash
gcloud run services update dialectica-api \
  --region=$REGION \
  --update-env-vars="DATABRICKS_HOST=https://your-workspace.cloud.databricks.com,DATABRICKS_TOKEN=dapi-xxx,DATABRICKS_CLUSTER_ID=xxxx-xxxxxx-xxxxxxxx"
```

### 6.3 Test

```bash
curl -s -X POST https://$API_URL/v1/admin/databricks/test \
  -H "X-API-Key: $ADMIN_API_KEY"
# Expected: {"status": "connected", "cluster_state": "RUNNING"}
```

---

## Step 7: TACITUS Integration Configuration (Optional)

If connecting DIALECTICA to other TACITUS platform applications:

### 7.1 Create integration API key

```bash
curl -s -X POST https://$API_URL/v1/admin/api-keys \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ADMIN_API_KEY" \
  -d '{"level": "integration", "tenant_id": "tacitus-platform", "description": "TACITUS platform integration"}'
```

### 7.2 Configure calling applications

In the TACITUS application that needs to call DIALECTICA:

```bash
TACITUS_DIALECTICA_URL=https://dialectica-api-xxxxx-ue.a.run.app
TACITUS_DIALECTICA_API_KEY=sk-integration-xxxxxxxx
```

### 7.3 Integration endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/integration/graph` | POST | Push/pull conflict graphs |
| `/v1/integration/context` | GET | Retrieve workspace context |
| `/v1/integration/query` | POST | Execute reasoning queries |

---

## Production Runbook

For a complete step-by-step production deployment guide including Neo4j Aura
setup, monitoring, benchmarking baselines, and post-deployment checklist, see
**[docs/runbook.md](runbook.md)**.

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GCP_PROJECT_ID` | Yes | - | Google Cloud project ID |
| `GRAPH_BACKEND` | No | `spanner` | `spanner`, `neo4j`, or `falkordb` |
| `ADMIN_API_KEY` | Yes | - | Admin API key |
| `REDIS_URL` | No | `redis://localhost:6379` | Redis connection |
| `VERTEX_AI_LOCATION` | No | `us-east1` | Vertex AI region |
| `GEMINI_FLASH_MODEL` | No | `gemini-2.5-flash-001` | Fast extraction model |
| `GEMINI_PRO_MODEL` | No | `gemini-2.5-pro-001` | Complex synthesis model |
| `EMBEDDING_BACKEND` | No | `vertex` | `vertex` or `fastembed` |
| `ENVIRONMENT` | No | `development` | `development` or `production` |
| `LOG_LEVEL` | No | `INFO` | Python log level |
| `CORS_ORIGINS` | No | - | Comma-separated origins |
| `BIGQUERY_ENABLED` | No | `false` | Enable BigQuery analytics logging |
| `BIGQUERY_DATASET` | No | `dialectica_analytics` | BigQuery dataset name |
| `DATABRICKS_HOST` | No | - | Databricks workspace URL |
| `DATABRICKS_TOKEN` | No | - | Databricks access token |
| `DATABRICKS_CLUSTER_ID` | No | - | Databricks cluster ID |
| `NEO4J_URI` | Yes* | - | Neo4j connection URI (*when GRAPH_BACKEND=neo4j) |
| `NEO4J_USER` | Yes* | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | Yes* | - | Neo4j password |

## Cost Estimation

| Environment | Compute | Databases | AI/ML | Total |
|-------------|---------|-----------|-------|-------|
| **Dev** | Cloud Run ~$30 | FalkorDB (self-hosted) | Vertex AI ~$50 | **~$175/mo** |
| **Staging** | Cloud Run ~$120 | Neo4j + Qdrant ~$150 | Vertex AI ~$100 | **~$500/mo** |
| **Production** | GKE ~$500 | Neo4j + Spanner ~$600 | Vertex AI ~$400 | **~$1,500-2,100/mo** |

## Troubleshooting

### Cloud Run deployment fails
- Check Artifact Registry permissions: `gcloud auth configure-docker`
- Verify image exists: `gcloud artifacts docker images list`
- Check build logs: `gcloud builds log <BUILD_ID>`

### API returns 503
- Check health endpoint: `curl <URL>/health/deep`
- Verify graph backend is reachable from Cloud Run VPC
- Check logs: `gcloud run services logs read dialectica-api`

### Extraction worker not processing
- Check Pub/Sub subscription: `gcloud pubsub subscriptions list`
- Verify DLQ isn't accumulating: check `dialectica-extraction-dlq`
- Check worker logs for authentication errors
