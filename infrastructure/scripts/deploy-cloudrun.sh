#!/bin/bash
set -euo pipefail

# Deploy DIALECTICA API to Google Cloud Run with Neo4j Aura
# Usage: ./deploy-cloudrun.sh PROJECT_ID [REGION]
# Prerequisites: gcloud CLI authenticated, Neo4j secrets stored via setup-secrets.sh

PROJECT_ID=${1:?"Usage: deploy-cloudrun.sh PROJECT_ID [REGION]"}
REGION=${2:-us-east1}
SERVICE_NAME=dialectica-api
REGISTRY=$REGION-docker.pkg.dev/$PROJECT_ID/dialectica

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
  --min-instances=1 \
  --max-instances=4 \
  --cpu=2 --memory=2Gi \
  --timeout=300 \
  --set-env-vars="GRAPH_BACKEND=neo4j" \
  --set-env-vars="NEO4J_DATABASE=neo4j" \
  --set-env-vars="ENVIRONMENT=production" \
  --set-env-vars="CORS_ORIGINS=*" \
  --set-env-vars="RATE_LIMIT_BACKEND=memory" \
  --set-env-vars="LOG_LEVEL=INFO" \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID" \
  --set-secrets="NEO4J_URI=dialectica-neo4j-uri:latest" \
  --set-secrets="NEO4J_USER=dialectica-neo4j-user:latest" \
  --set-secrets="NEO4J_PASSWORD=dialectica-neo4j-password:latest" \
  --set-secrets="ADMIN_API_KEY=dialectica-admin-key:latest" \
  --project=$PROJECT_ID

API_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format='value(status.url)')
echo ""
echo "==> Deployed! API URL: $API_URL"
echo "    Health: $API_URL/health"
echo "    Docs:   $API_URL/docs"
echo ""

# Verify
echo "==> Verifying deployment..."
if curl -sf "$API_URL/health" > /dev/null; then
  echo "    Health check passed!"
else
  echo "    WARNING: Health check failed. Check logs: gcloud run services logs read $SERVICE_NAME --region=$REGION"
fi
