"""
Dependency Injection — FastAPI dependency functions for DIALECTICA API.

  get_graph_client() -> GraphClient
    Returns configured Spanner or Neo4j client based on GRAPH_BACKEND setting.
    Cached as application state (single instance per process).

  get_tenant_context(request) -> TenantContext
    Extracts tenant_id from validated API key on request state.

  get_current_tier(workspace_id) -> OntologyTier
    Looks up workspace's ontology tier from Spanner Workspaces table.

  require_admin(request) -> None
    Validates that the current API key has admin privileges.
"""
from __future__ import annotations

# TODO: Implement in Prompt 8
