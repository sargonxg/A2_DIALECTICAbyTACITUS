"""
Dependency Injection — FastAPI dependency functions for DIALECTICA API.

Provides cached singletons for graph client and query engine,
plus request-scoped tenant/admin guards.
"""
from __future__ import annotations

import functools
from typing import Any

from fastapi import Depends, HTTPException, Request, status

from dialectica_api.config import Settings, get_settings as _get_settings


@functools.lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached application settings singleton."""
    return _get_settings()


_graph_client_instance: Any | None = None


def get_graph_client(settings: Settings = Depends(get_settings)) -> Any:
    """Create or return cached GraphClient based on config.

    Returns the client or None if the graph package is unavailable.
    """
    global _graph_client_instance
    if _graph_client_instance is not None:
        return _graph_client_instance

    try:
        from dialectica_graph import create_graph_client

        config: dict[str, Any] = {}
        if settings.graph_backend == "spanner":
            config = {
                "project_id": settings.gcp_project_id,
                "instance_id": settings.spanner_instance_id,
                "database_id": settings.spanner_database_id,
            }
            if settings.spanner_emulator_host:
                config["emulator_host"] = settings.spanner_emulator_host
        elif settings.graph_backend == "neo4j":
            config = {
                "uri": settings.neo4j_uri,
                "username": settings.neo4j_user,
                "password": settings.neo4j_password,
            }

        _graph_client_instance = create_graph_client(
            backend=settings.graph_backend,
            config=config,
        )
        return _graph_client_instance
    except Exception:
        # Graph package may not be installed or backend unreachable
        return None


def get_query_engine(
    graph_client: Any = Depends(get_graph_client),
) -> Any:
    """Create a ConflictQueryEngine with the graph client.

    Returns the engine or None if the reasoning package is unavailable.
    """
    if graph_client is None:
        return None
    try:
        from dialectica_reasoning import ConflictQueryEngine

        return ConflictQueryEngine(graph_client=graph_client)
    except Exception:
        return None


def get_current_tenant(request: Request) -> str:
    """Extract tenant_id from request state (set by auth middleware)."""
    tenant_id: str | None = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required — provide X-API-Key header.",
        )
    return tenant_id


def require_admin(request: Request) -> None:
    """Validate that the current request has admin privileges."""
    is_admin: bool = getattr(request.state, "is_admin", False)
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )


def reset_graph_client() -> None:
    """Reset the cached graph client (for testing)."""
    global _graph_client_instance
    _graph_client_instance = None
