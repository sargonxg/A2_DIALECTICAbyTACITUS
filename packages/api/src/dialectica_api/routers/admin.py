"""
Admin Router — System administration and monitoring endpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from dialectica_api.deps import get_graph_client, get_settings, require_admin
from dialectica_api.middleware.usage import get_all_usage_stats

router = APIRouter(prefix="/v1/admin", tags=["admin"])


class SystemInfo(BaseModel):
    graph_backend: str
    version: str = "2.0.0"
    environment: str = "development"


@router.get("/system", response_model=SystemInfo)
async def get_system_info(
    _admin: None = Depends(require_admin),  # noqa: B008
    settings: Any = Depends(get_settings),  # noqa: B008
) -> SystemInfo:
    """Get system information (admin only)."""
    import os

    return SystemInfo(
        graph_backend=settings.graph_backend,
        environment=os.getenv("ENVIRONMENT", "development"),
    )


@router.get("/usage")
async def get_usage(
    _admin: None = Depends(require_admin),  # noqa: B008
) -> dict[str, Any]:
    """Get API usage statistics across all tenants (admin only)."""
    return get_all_usage_stats()


@router.post("/seed")
async def seed_data(
    _admin: None = Depends(require_admin),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> dict[str, str]:
    """Trigger seed data loading (admin only)."""
    if graph_client is None:
        return {"status": "error", "detail": "Graph client unavailable."}
    try:
        import subprocess
        import sys

        subprocess.Popen([sys.executable, "/scripts/seed_sample_data.py"])
        return {"status": "started", "detail": "Seed data loading initiated."}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}
