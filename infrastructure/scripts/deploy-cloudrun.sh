#!/bin/bash
set -euo pipefail

# Deploy DIALECTICA API to Google Cloud Run with Neo4j Aura
# Usage: ./deploy-cloudrun.sh PROJECT_ID [REGION]
# Prerequisites: gcloud CLI authenticated, Neo4j secrets stored via setup-secrets.sh

PROJECT_ID=${1:?"Usage: deploy-cloudrun.sh PROJECT_ID [REGION]"}
REGION=${2:-us-central1}
SERVICE_NAME=dialectica-api
REGISTRY=$REGION-docker.pkg.dev/$PROJECT_ID/dialectica
CLOUD_SQL_CONNECTION_NAME=${CLOUD_SQL_CONNECTION_NAME:-}
DATABASE_URL_SECRET=${DATABASE_URL_SECRET:-dialectica-database-url}
GEMINI_API_KEY_SECRET=${GEMINI_API_KEY_SECRET:-dialectica-gemini-api-key}
NEO4J_URI_SECRET=${NEO4J_URI_SECRET:-dialectica-neo4j-uri}
NEO4J_USER_SECRET=${NEO4J_USER_SECRET:-dialectica-neo4j-user}
NEO4J_USERNAME_SECRET=${NEO4J_USERNAME_SECRET:-dialectica-neo4j-username}
NEO4J_PASSWORD_SECRET=${NEO4J_PASSWORD_SECRET:-dialectica-neo4j-password}
NEO4J_DATABASE_SECRET=${NEO4J_DATABASE_SECRET:-dialectica-neo4j-database}
AURA_INSTANCEID_SECRET=${AURA_INSTANCEID_SECRET:-dialectica-aura-instanceid}
AURA_INSTANCENAME_SECRET=${AURA_INSTANCENAME_SECRET:-dialectica-aura-instancename}

EXTRA_DEPLOY_ARGS=()
if [[ -n "$CLOUD_SQL_CONNECTION_NAME" ]]; then
  EXTRA_DEPLOY_ARGS+=(--add-cloudsql-instances="$CLOUD_SQL_CONNECTION_NAME")
  EXTRA_DEPLOY_ARGS+=(--set-env-vars="CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME")
  EXTRA_DEPLOY_ARGS+=(--set-secrets="DATABASE_URL=$DATABASE_URL_SECRET:latest")
fi

echo "==> Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  --project=$PROJECT_ID

echo "==> Creating Artifact Registry (if needed)..."
gcloud artifacts repositories create dialectica \
  --repository-format=docker \
  --location=$REGION \
  --project=$PROJECT_ID 2>/dev/null || true

echo "==> Building and pushing image via Cloud Build..."
gcloud builds submit \
  --tag $REGISTRY/api:latest \
  --project=$PROJECT_ID \
  --gcs-log-dir=gs://${PROJECT_ID}_cloudbuild/logs \
  -f packages/api/Dockerfile.cloudrun .

echo "==> Creating admin key secret (if needed)..."
echo -n "${ADMIN_API_KEY:-$(openssl rand -hex 32)}" | \
  gcloud secrets create dialectica-admin-key --data-file=- --project=$PROJECT_ID 2>/dev/null || true

echo "==> Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image=$REGISTRY/api:latest \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=1 \
  --concurrency=40 \
  --cpu=1 --memory=1Gi \
  --cpu-throttling \
  --no-cpu-boost \
  --timeout=300 \
  --set-env-vars="GRAPH_BACKEND=neo4j" \
  --set-env-vars="NEO4J_CONNECTION_TIMEOUT=5" \
  --set-env-vars="ENVIRONMENT=production" \
  --set-env-vars="CORS_ORIGINS=*" \
  --set-env-vars="RATE_LIMIT_BACKEND=memory" \
  --set-env-vars="LOG_LEVEL=INFO" \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID" \
  --set-env-vars="GRAPHITI_USE_NATIVE=false" \
  --set-env-vars="COZO_USE_EMBEDDED=true" \
  --set-env-vars="COZO_ENGINE=mem" \
  --set-env-vars="COZO_PATH=" \
  --set-env-vars="COZO_OPTIONS={}" \
  --set-env-vars="COZO_SNAPSHOT_PATH=" \
  --set-env-vars="GRAPH_REASONING_CHUNK_CHARS=6000" \
  --set-secrets="NEO4J_URI=$NEO4J_URI_SECRET:latest" \
  --set-secrets="NEO4J_USER=$NEO4J_USER_SECRET:latest" \
  --set-secrets="NEO4J_USERNAME=$NEO4J_USERNAME_SECRET:latest" \
  --set-secrets="NEO4J_PASSWORD=$NEO4J_PASSWORD_SECRET:latest" \
  --set-secrets="NEO4J_DATABASE=$NEO4J_DATABASE_SECRET:latest" \
  --set-secrets="GEMINI_API_KEY=$GEMINI_API_KEY_SECRET:latest" \
  --set-secrets="GOOGLE_AI_API_KEY=$GEMINI_API_KEY_SECRET:latest" \
  --set-secrets="AURA_INSTANCEID=$AURA_INSTANCEID_SECRET:latest" \
  --set-secrets="AURA_INSTANCENAME=$AURA_INSTANCENAME_SECRET:latest" \
  --set-secrets="ADMIN_API_KEY=dialectica-admin-key:latest" \
  "${EXTRA_DEPLOY_ARGS[@]}" \
  --project=$PROJECT_ID

API_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format='value(status.url)')
echo ""
echo "==> Deployed! API URL: $API_URL"
echo "    Health: $API_URL/health"
echo "    Docs:   $API_URL/docs"
echo ""

# Verify
echo "==> Verifying deployment..."
if curl -sf "$API_URL/health/live" > /dev/null; then
  echo "    Health check passed!"
else
  echo "    WARNING: Health check failed. Check logs: gcloud run services logs read $SERVICE_NAME --region=$REGION"
fi
