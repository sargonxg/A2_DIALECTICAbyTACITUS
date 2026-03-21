# ADR-006: Qdrant Over Vertex AI Vector Search

**Status:** Accepted
**Date:** 2025-03-05

## Context
DIALECTICA needs dual vector spaces (semantic 768d + structural 256d). Options: Vertex AI Vector Search (managed, GCP-native), Qdrant (self-hosted/cloud, named vectors), Pinecone (managed).

## Decision
Use Qdrant for its named vectors feature (semantic + structural in one collection), payload filtering for tenant isolation, and hybrid search with RRF fusion support.

## Consequences
- **Positive:** Named vectors natively support dual embedding spaces; payload filtering for multi-tenancy; open-source; GDPR delete support
- **Negative:** Must manage Qdrant infrastructure (or use Qdrant Cloud); not GCP-native
- **Mitigation:** Helm chart provided; Qdrant Cloud available as managed option; Docker Compose for dev
