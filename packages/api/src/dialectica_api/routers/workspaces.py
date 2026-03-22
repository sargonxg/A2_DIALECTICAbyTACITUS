"""
Workspaces Router — CRUD operations for conflict workspaces.
"""

from __future__ import annotations

import contextlib
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from dialectica_api.deps import get_current_tenant, get_graph_client

router = APIRouter(prefix="/v1/workspaces", tags=["workspaces"])


class WorkspaceCreate(BaseModel):
    name: str
    domain: str = "political"
    scale: str = "macro"
    tier: str = "standard"
    description: str = ""


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    domain: str | None = None
    scale: str | None = None
    description: str | None = None


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    domain: str
    scale: str
    tier: str
    description: str
    tenant_id: str
    created_at: str
    node_count: int = 0
    edge_count: int = 0


# In-memory workspace store (Spanner in production)
_workspaces: dict[str, dict[str, Any]] = {}


@router.post("", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    body: WorkspaceCreate,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> WorkspaceResponse:
    """Create a new conflict workspace."""
    import uuid

    workspace_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat()
    workspace = {
        "id": workspace_id,
        "name": body.name,
        "domain": body.domain,
        "scale": body.scale,
        "tier": body.tier,
        "description": body.description,
        "tenant_id": tenant_id,
        "created_at": now,
    }
    _workspaces[workspace_id] = workspace

    if graph_client:
        with contextlib.suppress(Exception):
            await graph_client.initialize_schema()

    return WorkspaceResponse(**workspace)


@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces(
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
) -> list[WorkspaceResponse]:
    """List all workspaces for the current tenant."""
    tenant_workspaces = [
        WorkspaceResponse(**ws)
        for ws in _workspaces.values()
        if ws["tenant_id"] == tenant_id or tenant_id == "admin"
    ]
    return tenant_workspaces


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> WorkspaceResponse:
    """Get a workspace by ID."""
    ws = _workspaces.get(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found.")
    if ws["tenant_id"] != tenant_id and tenant_id != "admin":
        raise HTTPException(status_code=403, detail="Access denied.")

    stats = {"node_count": 0, "edge_count": 0}
    if graph_client:
        try:
            ws_stats = await graph_client.get_workspace_stats(workspace_id)
            stats["node_count"] = getattr(ws_stats, "total_nodes", 0)
            stats["edge_count"] = getattr(ws_stats, "total_edges", 0)
        except Exception:
            pass

    return WorkspaceResponse(**{**ws, **stats})


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    body: WorkspaceUpdate,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
) -> WorkspaceResponse:
    """Update workspace metadata."""
    ws = _workspaces.get(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    if ws["tenant_id"] != tenant_id and tenant_id != "admin":
        raise HTTPException(status_code=403, detail="Access denied.")

    updates = body.model_dump(exclude_none=True)
    ws.update(updates)
    return WorkspaceResponse(**ws)


@router.delete("/{workspace_id}", status_code=204)
async def delete_workspace(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
) -> None:
    """Delete a workspace."""
    ws = _workspaces.get(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found.")
    if ws["tenant_id"] != tenant_id and tenant_id != "admin":
        raise HTTPException(status_code=403, detail="Access denied.")
    del _workspaces[workspace_id]
