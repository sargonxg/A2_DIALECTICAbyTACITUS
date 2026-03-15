"""
API Configuration — Pydantic Settings for DIALECTICA API.

All settings load from environment variables with sensible defaults.
Validated at startup — missing required settings fail fast.

Required:
  GCP_PROJECT_ID: Google Cloud project
  SPANNER_INSTANCE_ID: Spanner instance (default: dialectica-graph)
  SPANNER_DATABASE_ID: Spanner database (default: dialectica)
  ADMIN_API_KEY: Initial bootstrap admin key

Optional:
  GRAPH_BACKEND: "spanner" (default) or "neo4j"
  VERTEX_AI_LOCATION: GCP region (default: us-east1)
  NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD: Neo4j connection (if backend=neo4j)
  CORS_ORIGINS: Comma-separated allowed origins
"""
from __future__ import annotations

# TODO: Implement in Prompt 8
# from pydantic_settings import BaseSettings
