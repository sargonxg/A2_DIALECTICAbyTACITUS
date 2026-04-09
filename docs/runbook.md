# DIALECTICA Production Deployment Runbook

Complete step-by-step guide for deploying DIALECTICA to production on Google
Cloud Platform with Neo4j Aura, Vercel, and optional BigQuery/Databricks
integrations.

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| GCP Project | Billing enabled, Owner or Editor role |
| Neo4j Aura | Account created (TACITUS is in Neo4j Startup Program) |
| Vercel | Account with team access for frontend deployment |
| GitHub | Repository access with push permissions to `main` |
| Google Cloud SDK | `gcloud` CLI installed and authenticated |
| Terraform | >= 1.5 installed |
| Docker | >= 24.0 installed |
| UV | Latest (`pip install uv`) |
| Node.js | >= 18 (for frontend build) |

### Verify prerequisites

```bash
gcloud --version          # Google Cloud SDK
terraform --version       # Terraform >= 1.5
docker --version          # Docker >= 24.0
uv --version              # UV package manager
node --version            # Node.js >= 18
```

---

## Step 1: GCP Project Setup

### 1.1 Select or create project

```bash
export PROJECT_ID=your-project-id
export REGION=us-east1

gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION
```

### 1.2 Enable required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  aiplatform.googleapis.com \
  pubsub.googleapis.com \
  storage.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com
```

Expected output: each API prints `Operation "..." finished successfully.`

### 1.3 Set up Workload Identity Federation for GitHub Actions

This allows GitHub Actions to authenticate to GCP without service account keys.

```bash
# Create Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Create OIDC provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub OIDC" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Grant the pool access to deploy
export WIF_POOL=$(gcloud iam workload-identity-pools describe github-pool \
  --location="global" --format="value(name)")

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="principalSet://iam.googleapis.com/$WIF_POOL/attribute.repository/sargonxg/dialectica" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="principalSet://iam.googleapis.com/$WIF_POOL/attribute.repository/sargonxg/dialectica" \
  --role="roles/artifactregistry.writer"
```

---

## Step 2: Infrastructure Provisioning (Terraform)

### 2.1 Initialize Terraform

```bash
cd infrastructure/terraform

# Create your tfvars from the example
cat > terraform.tfvars <<EOF
project_id = "$PROJECT_ID"
region     = "$REGION"
environment = "production"
EOF

terraform init
```

Expected output: `Terraform has been successfully initialized!`

### 2.2 Plan and review

```bash
terraform plan -out=tfplan
```

Review the plan output. It provisions:
- Artifact Registry repository (`dialectica`)
- Secret Manager secrets (Neo4j credentials, admin API key)
- Pub/Sub topics and subscriptions (extraction pipeline, DLQ)
- Cloud Storage bucket (document uploads)
- Cloud Run services (API + Web)
- IAM service accounts and bindings
- Cloud Monitoring alert policies

### 2.3 Apply

```bash
terraform apply tfplan
```

Expected output: `Apply complete! Resources: N added, 0 changed, 0 destroyed.`

Note the outputs:

```bash
terraform output
# api_url = "https://dialectica-api-xxxxx-ue.a.run.app"
# web_url = "https://dialectica-web-xxxxx-ue.a.run.app"
# artifact_registry = "us-east1-docker.pkg.dev/your-project/dialectica"
```

---

## Step 3: Neo4j Aura Configuration

### 3.1 Create Neo4j Aura instance

1. Log in to [Neo4j Aura Console](https://console.neo4j.io/)
2. Create a new AuraDB instance:
   - Plan: Free / Professional / Enterprise (TACITUS Startup Program tier)
   - Region: `us-east-1` (match GCP region)
   - Name: `dialectica-production`
3. Save the connection credentials (URI, username, password)

The URI format is: `neo4j+s://xxxxxxxx.databases.neo4j.io`

### 3.2 Store credentials in GCP Secret Manager

```bash
make setup-secrets
```

This runs `infrastructure/scripts/setup-secrets.sh` interactively. It prompts
for:
- Neo4j URI
- Neo4j username
- Neo4j password

Alternatively, set secrets manually:

```bash
echo -n "neo4j+s://xxxxxxxx.databases.neo4j.io" | \
  gcloud secrets create NEO4J_URI --data-file=-

echo -n "neo4j" | \
  gcloud secrets create NEO4J_USER --data-file=-

echo -n "your-aura-password" | \
  gcloud secrets create NEO4J_PASSWORD --data-file=-
```

### 3.3 Create and store admin API key

```bash
python infrastructure/scripts/create_admin_key.py
# Outputs: sk-admin-xxxxxxxxxxxxxxxx

echo -n "sk-admin-xxxxxxxxxxxxxxxx" | \
  gcloud secrets create ADMIN_API_KEY --data-file=-
```

### 3.4 Verify connectivity

```bash
# Quick check from local machine (requires .env configured)
cp .env.example .env
# Edit .env with your Neo4j Aura credentials

python -c "
from neo4j import GraphDatabase
import os
driver = GraphDatabase.driver(
    os.environ['NEO4J_URI'],
    auth=(os.environ['NEO4J_USER'], os.environ['NEO4J_PASSWORD'])
)
driver.verify_connectivity()
print('Neo4j Aura connected successfully')
driver.close()
"
```

---

## Step 4: Database Seeding

### 4.1 Configure local environment

Ensure `.env` has the production Neo4j Aura credentials:

```bash
GRAPH_BACKEND=neo4j
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-aura-password
```

### 4.2 Seed sample data

```bash
make seed
```

This runs three steps:
1. `seed-schema` -- Initialize Neo4j indexes and constraints
2. `seed-frameworks` -- Load 15 theory frameworks into the graph
3. `seed-samples` -- Load 6 sample conflict scenarios (114 nodes, 126 edges)

The 6 sample scenarios:
- `jcpoa.json` -- Iran nuclear deal (geopolitical)
- `syria_civil_war.json` -- Syrian conflict (armed)
- `commercial_dispute.json` -- Business contract dispute
- `commercial_ip_dispute.json` -- Intellectual property dispute
- `hr_mediation.json` -- Workplace harassment mediation
- `labor_dispute.json` -- Union-management negotiation

### 4.3 Verify seeding

```bash
# Check workspace count
curl -s http://localhost:8080/v1/workspaces \
  -H "X-API-Key: $ADMIN_API_KEY" | python -m json.tool

# Expected: 6 workspaces, one per sample scenario
```

---

## Step 5: API Deployment (Cloud Run)

### 5.1 Build and push Docker image

```bash
# Authenticate Docker with Artifact Registry
gcloud auth configure-docker $REGION-docker.pkg.dev

# Build the production image (< 500MB, no torch/gliner)
docker build -f packages/api/Dockerfile.cloudrun \
  -t $REGION-docker.pkg.dev/$PROJECT_ID/dialectica/api:latest .

# Push to Artifact Registry
docker push $REGION-docker.pkg.dev/$PROJECT_ID/dialectica/api:latest
```

### 5.2 Deploy to Cloud Run

```bash
make deploy
# Or manually:
bash infrastructure/scripts/deploy-cloudrun.sh $PROJECT_ID $REGION
```

The deploy script:
1. Builds the Docker image
2. Pushes to Artifact Registry
3. Deploys to Cloud Run with:
   - 2 CPU / 2 Gi memory
   - Min 0, max 10 instances (autoscale)
   - Secrets injected from Secret Manager
   - Startup probe on `/health`
   - Liveness probe on `/health/live`
   - `--no-allow-unauthenticated` (requires IAM)

### 5.3 Verify API health

```bash
export API_URL=$(gcloud run services describe dialectica-api \
  --region=$REGION --format="value(status.url)")

# Health check
curl -s $API_URL/health | python -m json.tool
# Expected: {"status": "healthy", "version": "1.0.0", ...}

# Liveness probe
curl -s $API_URL/health/live
# Expected: {"status": "alive"}

# Readiness probe (checks Neo4j connectivity)
curl -s $API_URL/health/ready
# Expected: {"status": "ready", "graph_backend": "neo4j", ...}
```

### 5.4 Verify API docs

Open in browser: `$API_URL/docs` (Swagger UI)

---

## Step 6: Frontend Deployment (Vercel)

### 6.1 Configure environment

```bash
cd apps/web
```

Set the following environment variables in Vercel:
- `NEXT_PUBLIC_API_URL` = your Cloud Run API URL (e.g., `https://dialectica-api-xxxxx-ue.a.run.app`)

### 6.2 Deploy

```bash
npx vercel --prod
```

Or connect the GitHub repository in the Vercel dashboard:
1. Import the repository
2. Set root directory to `apps/web`
3. Framework: Next.js (auto-detected)
4. Set environment variables
5. Deploy

### 6.3 Verify frontend

Check the deployed URL:
- Landing page: `https://your-domain.vercel.app/`
- Demo page: `https://your-domain.vercel.app/demo`
- Investor demo: `https://your-domain.vercel.app/demo/investor`
- Admin benchmarks: `https://your-domain.vercel.app/admin/benchmarks`

### 6.4 Custom domain (optional)

If using `dialectica.tacitus.ai`:
1. Add domain in Vercel project settings
2. Configure DNS: CNAME record pointing to `cname.vercel-dns.com`
3. SSL is provisioned automatically

---

## Step 7: Monitoring and Alerts

### 7.1 Verify Cloud Monitoring

Terraform provisions a monitoring dashboard. Check it in the GCP Console:
1. Go to Cloud Monitoring > Dashboards
2. Find the "DIALECTICA" dashboard
3. Verify panels show:
   - Cloud Run request count and latency
   - Error rate (4xx, 5xx)
   - Instance count and CPU utilization

### 7.2 Check Prometheus metrics

```bash
curl -s $API_URL/metrics | head -20
# Expected: Prometheus-format metrics (request_count, request_latency, etc.)
```

### 7.3 Check Cloud Run logs

```bash
gcloud run services logs read dialectica-api --region=$REGION --limit=20
```

### 7.4 Configure alerting (recommended)

Set up alert policies for:
- Error rate > 5% over 5 minutes
- P95 latency > 2s over 5 minutes
- Instance count at max (autoscale ceiling)
- Neo4j connection failures

```bash
# Example: create error rate alert
gcloud monitoring policies create --policy-from-file=infrastructure/terraform/alert-policies/error-rate.json
```

---

## Step 8: Benchmarking Baseline

After deployment, establish performance baselines with the benchmarking system.

### 8.1 Run JCPOA benchmark

```bash
curl -s -X POST $API_URL/v1/admin/benchmark/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ADMIN_API_KEY" \
  -d '{
    "corpus_id": "jcpoa",
    "tier": "standard",
    "include_graph_augmented": true
  }' | python -m json.tool
```

Expected output includes:
- `entity_f1`: F1 score for entity extraction (target: >= 0.75)
- `entity_precision`: Precision score
- `entity_recall`: Recall score
- `relationship_f1`: F1 score for relationship extraction
- `hallucination_rate`: Rate of hallucinated entities (target: < 0.10)

### 8.2 Run all benchmark corpora

```bash
for corpus in jcpoa romeo_juliet crime_punishment war_peace; do
  echo "=== Benchmarking: $corpus ==="
  curl -s -X POST $API_URL/v1/admin/benchmark/run \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $ADMIN_API_KEY" \
    -d "{\"corpus_id\":\"$corpus\",\"tier\":\"standard\"}" | python -m json.tool
done
```

### 8.3 Record baseline

Save benchmark results for future comparison. The frontend dashboard at
`/admin/benchmarks` provides a visual overview with trend charts.

See `docs/benchmarking.md` for full details on the benchmarking system.

---

## Step 9: BigQuery Analytics (Optional)

### 9.1 Enable BigQuery

Terraform provisions the BigQuery dataset automatically. Verify:

```bash
bq ls --project_id=$PROJECT_ID
# Expected: dialectica_analytics dataset

bq ls $PROJECT_ID:dialectica_analytics
# Expected tables: extraction_events, query_events, benchmark_results
```

### 9.2 Configure API for BigQuery

Set these environment variables in Cloud Run (or Secret Manager):

```bash
BIGQUERY_ENABLED=true
BIGQUERY_DATASET=dialectica_analytics
```

### 9.3 Verify data flow

After running a few extractions:

```bash
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) as events FROM \`$PROJECT_ID.dialectica_analytics.extraction_events\`"
# Expected: non-zero count
```

### 9.4 BigQuery tables schema

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `extraction_events` | Every extraction pipeline run | workspace_id, corpus_id, tier, entity_count, edge_count, duration_ms, timestamp |
| `query_events` | Every reasoning query | workspace_id, query_mode, token_count, latency_ms, timestamp |
| `benchmark_results` | Benchmark run results | corpus_id, tier, entity_f1, relationship_f1, hallucination_rate, timestamp |

---

## Step 10: Databricks Integration (Optional)

### 10.1 Prerequisites

- Databricks workspace linked to your GCP project
- Service account with Databricks access

### 10.2 Configure

Set environment variables:

```bash
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi-xxxxxxxxxxxxxxxx
DATABRICKS_CLUSTER_ID=xxxx-xxxxxx-xxxxxxxx
```

### 10.3 Test graph export

The DatabricksConnector (in `packages/reasoning/`) supports:
- Exporting conflict graphs as DataFrames for analysis
- Running KGE (Knowledge Graph Embedding) training on Databricks clusters
- Retrieving predictions back into the reasoning pipeline

```bash
curl -s -X POST $API_URL/v1/admin/databricks/test \
  -H "X-API-Key: $ADMIN_API_KEY" | python -m json.tool
# Expected: {"status": "connected", "cluster_state": "RUNNING"}
```

---

## Step 11: TACITUS Integration (Optional)

If integrating with other TACITUS platform components:

### 11.1 Integration endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/integration/graph` | POST | Push/pull conflict graphs between TACITUS apps |
| `/v1/integration/context` | GET | Retrieve contextual data for a workspace |
| `/v1/integration/query` | POST | Execute cross-app reasoning queries |

### 11.2 Configure

Set the TACITUS integration API key in the calling application:

```bash
TACITUS_DIALECTICA_URL=https://dialectica-api-xxxxx-ue.a.run.app
TACITUS_DIALECTICA_API_KEY=sk-integration-xxxxxxxx
```

---

## Troubleshooting

### API not starting

```bash
# Check Cloud Run logs
gcloud run services logs read dialectica-api --region=$REGION --limit=50

# Common causes:
# 1. NEO4J_URI not reachable from Cloud Run
#    Fix: verify Neo4j Aura is running, check URI format (neo4j+s://)
# 2. Missing secrets in Secret Manager
#    Fix: run `make setup-secrets` or check `gcloud secrets list`
# 3. Image too large (> 2GB)
#    Fix: use Dockerfile.cloudrun (no torch/gliner), target < 500MB
```

### Extraction failing

```bash
# Check Vertex AI permissions
gcloud ai models list --region=$REGION

# Common causes:
# 1. GOOGLE_APPLICATION_CREDENTIALS not set or invalid
#    Fix: use Workload Identity in Cloud Run (automatic)
# 2. Vertex AI API not enabled
#    Fix: gcloud services enable aiplatform.googleapis.com
# 3. Gemini model not available in region
#    Fix: verify VERTEX_AI_LOCATION matches available regions
```

### Frontend 500 errors

```bash
# Common causes:
# 1. NEXT_PUBLIC_API_URL not set or wrong
#    Fix: verify env var in Vercel dashboard, must match Cloud Run URL
# 2. CORS not configured
#    Fix: add Vercel domain to CORS_ORIGINS env var on the API
# 3. API not reachable
#    Fix: check API health endpoint, verify Cloud Run is running
```

### Rate limiting issues

```bash
# Check current limits
curl -s $API_URL/health -H "X-API-Key: $ADMIN_API_KEY" -v 2>&1 | grep -i rate

# Common causes:
# 1. Redis not connected (rate limiter falls back to memory)
#    Fix: set REDIS_URL and RATE_LIMIT_BACKEND=redis
# 2. Default limits too low for production
#    Fix: adjust RATE_LIMIT_DEFAULT, RATE_LIMIT_EXTRACT, RATE_LIMIT_REASON
```

### Neo4j Aura connection drops

```bash
# Test connectivity
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('neo4j+s://xxx.databases.neo4j.io', auth=('neo4j', 'xxx'))
driver.verify_connectivity()
print('OK')
"

# Common causes:
# 1. Aura instance paused (free tier auto-pauses after inactivity)
#    Fix: resume in Neo4j Aura console
# 2. Credentials rotated
#    Fix: update Secret Manager, redeploy Cloud Run
# 3. Network/firewall
#    Fix: Cloud Run has internet access by default, check VPC connector if using one
```

---

## Post-Deployment Checklist

- [ ] API health endpoint returns `{"status": "healthy"}`
- [ ] Neo4j Aura connectivity verified via `/health/ready`
- [ ] 6 sample scenarios seeded and visible via `/v1/workspaces`
- [ ] Frontend loads at production URL
- [ ] Demo page (`/demo`) can extract entities from pasted text
- [ ] Investor demo (`/demo/investor`) completes all 5 steps
- [ ] Swagger UI accessible at `/docs`
- [ ] Prometheus metrics available at `/metrics`
- [ ] Cloud Monitoring dashboard shows request data
- [ ] JCPOA benchmark passes with F1 >= 0.75
- [ ] Admin API key works for protected endpoints
- [ ] CORS configured for production frontend domain
- [ ] Rate limiting active (test with rapid requests)
- [ ] Workload Identity Federation working for CI/CD
