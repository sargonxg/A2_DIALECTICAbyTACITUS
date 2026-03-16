"""
Health Router — DIALECTICA API health check endpoints.
"""
from __future__ import annotations

import os
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from dialectica_api.deps import get_graph_client, get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str = "1.0.0"


class DependencyHealth(BaseModel):
    graph_backend: str
    graph_connected: bool
    graph_status: str


@router.get("/health", response_model=HealthResponse, include_in_schema=True)
async def health_check() -> HealthResponse:
    """Basic liveness check."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/health/dependencies", response_model=DependencyHealth)
async def health_dependencies(
    settings=Depends(get_settings),
    graph_client=Depends(get_graph_client),
) -> DependencyHealth:
    """Check connectivity to backing services."""
    connected = False
    status = "disconnected"

    if graph_client is not None:
        try:
            # Try a lightweight operation
            await graph_client.get_nodes("__health__", limit=1)
            connected = True
            status = "connected"
        except Exception as exc:
            status = f"error: {str(exc)[:80]}"

    return DependencyHealth(
        graph_backend=settings.graph_backend,
        graph_connected=connected,
        graph_status=status,
    )
