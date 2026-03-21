#!/usr/bin/env bash
set -euo pipefail

# Deploy Helm charts for DIALECTICA stateful services to GKE.
# Usage: ./deploy_helm.sh [namespace]

NAMESPACE="${1:-dialectica}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HELM_DIR="$SCRIPT_DIR/../helm"

echo "==> Creating namespace $NAMESPACE (if not exists)"
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

echo "==> Deploying Redis"
helm upgrade --install dialectica-redis "$HELM_DIR/redis" \
  --namespace "$NAMESPACE" --wait --timeout 120s

echo "==> Deploying FalkorDB"
helm upgrade --install dialectica-falkordb "$HELM_DIR/falkordb" \
  --namespace "$NAMESPACE" --wait --timeout 120s

echo "==> Deploying Qdrant"
helm upgrade --install dialectica-qdrant "$HELM_DIR/qdrant" \
  --namespace "$NAMESPACE" --wait --timeout 180s

echo "==> Deploying Neo4j"
helm upgrade --install dialectica-neo4j "$HELM_DIR/neo4j" \
  --namespace "$NAMESPACE" --wait --timeout 300s

echo "==> All Helm charts deployed to namespace $NAMESPACE"
kubectl get pods -n "$NAMESPACE"
