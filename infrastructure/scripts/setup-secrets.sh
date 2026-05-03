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
read -p "Neo4j Database [neo4j]: " NEO4J_DATABASE
NEO4J_DATABASE=${NEO4J_DATABASE:-neo4j}
read -p "Aura Instance ID [optional]: " AURA_INSTANCEID
read -p "Aura Instance Name [optional]: " AURA_INSTANCENAME
read -sp "Gemini API Key [optional]: " GEMINI_API_KEY
echo ""
read -p "Cloud SQL connection name [optional, PROJECT:REGION:INSTANCE]: " CLOUD_SQL_CONNECTION_NAME
DATABASE_URL=""
if [[ -n "$CLOUD_SQL_CONNECTION_NAME" ]]; then
  read -p "Cloud SQL database name [dialectica]: " CLOUD_SQL_DATABASE
  CLOUD_SQL_DATABASE=${CLOUD_SQL_DATABASE:-dialectica}
  read -p "Cloud SQL user [dialectica]: " CLOUD_SQL_USER
  CLOUD_SQL_USER=${CLOUD_SQL_USER:-dialectica}
  read -sp "Cloud SQL password: " CLOUD_SQL_PASSWORD
  echo ""
  DATABASE_URL="postgresql+asyncpg://$CLOUD_SQL_USER:$CLOUD_SQL_PASSWORD@/$CLOUD_SQL_DATABASE?host=/cloudsql/$CLOUD_SQL_CONNECTION_NAME"
fi

echo "==> Enabling Secret Manager API..."
gcloud services enable secretmanager.googleapis.com --project=$PROJECT_ID

echo "==> Creating secrets..."
echo -n "$NEO4J_URI" | gcloud secrets create dialectica-neo4j-uri --data-file=- --project=$PROJECT_ID 2>/dev/null \
  || echo -n "$NEO4J_URI" | gcloud secrets versions add dialectica-neo4j-uri --data-file=- --project=$PROJECT_ID

echo -n "$NEO4J_USER" | gcloud secrets create dialectica-neo4j-user --data-file=- --project=$PROJECT_ID 2>/dev/null \
  || echo -n "$NEO4J_USER" | gcloud secrets versions add dialectica-neo4j-user --data-file=- --project=$PROJECT_ID

echo -n "$NEO4J_USER" | gcloud secrets create dialectica-neo4j-username --data-file=- --project=$PROJECT_ID 2>/dev/null \
  || echo -n "$NEO4J_USER" | gcloud secrets versions add dialectica-neo4j-username --data-file=- --project=$PROJECT_ID

echo -n "$NEO4J_PASSWORD" | gcloud secrets create dialectica-neo4j-password --data-file=- --project=$PROJECT_ID 2>/dev/null \
  || echo -n "$NEO4J_PASSWORD" | gcloud secrets versions add dialectica-neo4j-password --data-file=- --project=$PROJECT_ID

echo -n "$NEO4J_DATABASE" | gcloud secrets create dialectica-neo4j-database --data-file=- --project=$PROJECT_ID 2>/dev/null \
  || echo -n "$NEO4J_DATABASE" | gcloud secrets versions add dialectica-neo4j-database --data-file=- --project=$PROJECT_ID

if [[ -n "$AURA_INSTANCEID" ]]; then
  echo -n "$AURA_INSTANCEID" | gcloud secrets create dialectica-aura-instanceid --data-file=- --project=$PROJECT_ID 2>/dev/null \
    || echo -n "$AURA_INSTANCEID" | gcloud secrets versions add dialectica-aura-instanceid --data-file=- --project=$PROJECT_ID
fi

if [[ -n "$AURA_INSTANCENAME" ]]; then
  echo -n "$AURA_INSTANCENAME" | gcloud secrets create dialectica-aura-instancename --data-file=- --project=$PROJECT_ID 2>/dev/null \
    || echo -n "$AURA_INSTANCENAME" | gcloud secrets versions add dialectica-aura-instancename --data-file=- --project=$PROJECT_ID
fi

if [[ -n "$GEMINI_API_KEY" ]]; then
  echo -n "$GEMINI_API_KEY" | gcloud secrets create dialectica-gemini-api-key --data-file=- --project=$PROJECT_ID 2>/dev/null \
    || echo -n "$GEMINI_API_KEY" | gcloud secrets versions add dialectica-gemini-api-key --data-file=- --project=$PROJECT_ID
fi

if [[ -n "$DATABASE_URL" ]]; then
  echo -n "$DATABASE_URL" | gcloud secrets create dialectica-database-url --data-file=- --project=$PROJECT_ID 2>/dev/null \
    || echo -n "$DATABASE_URL" | gcloud secrets versions add dialectica-database-url --data-file=- --project=$PROJECT_ID
fi

echo ""
echo "==> Secrets stored in project $PROJECT_ID:"
echo "    dialectica-neo4j-uri"
echo "    dialectica-neo4j-user"
echo "    dialectica-neo4j-username"
echo "    dialectica-neo4j-password"
echo "    dialectica-neo4j-database"
if [[ -n "$AURA_INSTANCEID" ]]; then
  echo "    dialectica-aura-instanceid"
fi
if [[ -n "$AURA_INSTANCENAME" ]]; then
  echo "    dialectica-aura-instancename"
fi
if [[ -n "$GEMINI_API_KEY" ]]; then
  echo "    dialectica-gemini-api-key"
fi
if [[ -n "$DATABASE_URL" ]]; then
  echo "    dialectica-database-url"
fi
echo ""
echo "    Next: run deploy-cloudrun.sh $PROJECT_ID"
