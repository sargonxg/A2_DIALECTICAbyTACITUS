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
