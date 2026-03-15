# DIALECTICA Architecture

## Four-Layer Neurosymbolic System

TODO: Full architecture documentation in Prompt 10.

## Overview

DIALECTICA implements a four-layer neurosymbolic architecture:

1. **Neural Ingestion** — GLiNER pre-filter + Gemini extraction + Pydantic validation
2. **Symbolic Representation** — Conflict Grammar (15 nodes × 20 edges) in Spanner Graph
3. **Reasoning/Inference** — GraphRAG + symbolic rules + GNN inference
4. **Decision Support** — Analyst/Mediator/Forecaster agents + human feedback loop

## Database Architecture

### Primary: Google Cloud Spanner Graph
- Enterprise edition, 100 Processing Units, us-east1
- Unified: GQL + SQL + vector search in one engine
- Dynamic labels: ONE Nodes table for all 15 node types
- Native 768-dim vector index (COSINE_DISTANCE)

### Secondary: Neo4j Aura
- For Graph Data Science algorithm needs
- 65+ algorithms: PageRank, community detection, centrality
- Cypher query language

## GCP Services

| Service | Purpose | Config |
|---------|---------|--------|
| Cloud Spanner | Graph database | Enterprise 100PU us-east1 |
| Vertex AI Gemini 2.5 Flash | Entity extraction | Flash model |
| Vertex AI Gemini 2.5 Pro | Reasoning synthesis | Pro model |
| Vertex AI Embeddings | Semantic search | text-embedding-005, 768-dim |
| Cloud Run (API) | FastAPI service | 1CPU 1Gi, 1-10 instances |
| Cloud Run (Web) | Next.js app | 1CPU 512Mi, 0-5 instances |
| Cloud Pub/Sub | Async extraction | dialectica-extraction-requests |
| Cloud Storage | Documents | {project}-dialectica-documents |
| Secret Manager | API keys | ADMIN_API_KEY |
