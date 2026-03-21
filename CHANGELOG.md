# Changelog

All notable changes to DIALECTICA are documented here.

## [2.0.0] — 2026-03-21

### Architecture
- Neurosymbolic 4-layer architecture: Neural Ingestion -> Symbolic Representation -> Reasoning & Inference -> Decision Support
- Dual database strategy: FalkorDB (tenant isolation) + Neo4j (graph analytics)
- Qdrant dual vector search: semantic (768-dim) + structural (256-dim) with RRF fusion
- Symbolic firewall ensuring deterministic conclusions are never overridden by neural predictions

### Ontology
- TACITUS Core Ontology v2.0: 15 node types, 20 edge types, 25+ controlled vocabularies
- 3-tier system: Essential (5 types), Standard (10 types), Full (15 types)
- Confidence type tagging: deterministic vs probabilistic conclusions
- PLOVER 16 event type mapping with severity nuances

### Extraction
- LangGraph 10-step extraction pipeline with conditional repair loop
- Instructor + LiteLLM for Pydantic-validated structured extraction (Gemini fallback)
- GLiNER pre-filtering for entity-dense passage selection
- ConfliBERT event classifier integration
- Pub/Sub async ingestion with dead-letter queue
- ACLED, GDELT, UCDP conflict data connectors
- Cross-source entity resolver with fuzzy matching

### Reasoning
- 4-step hybrid GraphRAG retriever: vector search -> graph expansion -> temporal filter -> RRF fusion
- 9 symbolic rule modules: escalation, trust, constraints, causality, patterns, ripeness, power, network, inference
- PyKEEN KGE training pipeline (RotatE) with link prediction
- Leiden community detection at 3 resolutions with natural language summarization
- Context builder with citation markers and 30K char budget

### API & Infrastructure
- FastAPI with comprehensive middleware: auth, rate limiting, metering, observability
- MCP server with 5 tools for LLM integration
- Scoped API key management (graph:read, graph:write, extract, reason, admin)
- Domain workspace templates: human friction, warfare/political, commercial dispute
- Health endpoints: /health, /health/ready, /health/deep
- OpenTelemetry + structlog observability

### Deployment
- UV workspaces (migrated from Poetry) with PEP 621 format
- Terraform modules: GKE, Cloud Run, networking, IAM, Pub/Sub, Secret Manager
- Helm charts: Neo4j, FalkorDB, Qdrant, Redis
- UV-based multi-stage Dockerfiles for API, extraction worker, MCP server
- Path-filtered CI with cascading dependencies
- Staging/production deploy via GitHub Actions + Workload Identity

### Documentation
- CLAUDE.md project intelligence file
- 7 Architecture Decision Records (ADRs)
- Deployment guide with GCP walkthrough and cost estimation
- Local development guide
- SDK quickstart (Python, TypeScript, cURL)
- Comprehensive seed data: JCPOA, Syria, labor dispute, commercial IP dispute

## [1.0.0] — 2025-01-01

### Initial Release
- Basic ontology with Spanner Graph backend
- Manual extraction pipeline
- REST API with basic auth
