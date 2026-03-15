"""
DIALECTICA API — FastAPI service for the Universal Data Layer for Human Friction.

Provides REST API endpoints for:
  /workspaces    — Conflict workspace management
  /extract       — Document ingestion and entity extraction
  /entities      — Node CRUD operations
  /relationships — Edge CRUD operations
  /graph         — Graph traversal and search
  /reasoning     — Natural language queries, analysis, mediation
  /theory        — Theory framework assessments
  /admin         — Platform administration
  /developers    — Self-service API key management
  /health        — Health and readiness checks

Authentication: API key via X-API-Key header or Authorization: Bearer
Multi-tenancy: Tenant derived from API key, injected into all operations
Rate limiting: Per-key sliding window (configurable)
"""
