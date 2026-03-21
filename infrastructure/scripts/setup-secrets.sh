#!/bin/bash
set -euo pipefail

# Store Neo4j Aura credentials in GCP Secret Manager
# Run this ONCE before deploying to Cloud Run
# Usage: ./setup-secrets.sh PROJECT_ID

PROJECT_ID=${1:?"Usage: setup-secrets.sh PROJECT_ID"}

echo "==> Setting up Neo4j Aura credentials in Secret Manager"
echo "    Project: $PROJECT_ID"
echo ""

read -p "Neo4j Aura URI (neo4j+s://xxx.databases.neo4j.io): " NEO4J_URI
read -p "Neo4j User [neo4j]: " NEO4J_USER
NEO4J_USER=${NEO4J_USER:-neo4j}
read -sp "Neo4j Password: " NEO4J_PASSWORD
echo ""

echo "==> Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

echo "==> Creating secrets..."
echo -n "$NEO4J_URI" | gcloud secrets create dialectica-neo4j-uri --data-file=- --project=$PROJECT_ID 2>/dev/null \
  || echo -n "$NEO4J_URI" | gcloud secrets versions add dialectica-neo4j-uri --data-file=- --project=$PROJECT_ID

echo -n "$NEO4J_USER" | gcloud secrets create dialectica-neo4j-user --data-file=- --project=$PROJECT_ID 2>/dev/null \
  || echo -n "$NEO4J_USER" | gcloud secrets versions add dialectica-neo4j-user --data-file=- --project=$PROJECT_ID

echo -n "$NEO4J_PASSWORD" | gcloud secrets create dialectica-neo4j-password --data-file=- --project=$PROJECT_ID 2>/dev/null \
  || echo -n "$NEO4J_PASSWORD" | gcloud secrets versions add dialectica-neo4j-password --data-file=- --project=$PROJECT_ID

echo ""
echo "==> Secrets stored in project $PROJECT_ID:"
echo "    dialectica-neo4j-uri"
echo "    dialectica-neo4j-user"
echo "    dialectica-neo4j-password"
echo ""
echo "    Next: run deploy-cloudrun.sh $PROJECT_ID"
