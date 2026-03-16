"""
Relationships Router — CRUD for conflict graph edges.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from dialectica_api.deps import get_graph_client, get_current_tenant

router = APIRouter(prefix="/v1/workspaces/{workspace_id}/relationships", tags=["relationships"])


class EdgeResponse(BaseModel):
    id: str
    type: str
    source_id: str
    target_id: str
    properties: dict[str, Any] = {}
    weight: float = 1.0


@router.get("", response_model=list[EdgeResponse])
async def list_relationships(
    workspace_id: str,
    edge_type: str | None = Query(None),
    limit: int = Query(100, le=1000),
    tenant_id: str = Depends(get_current_tenant),
    graph_client: Any = Depends(get_graph_client),
) -> list[EdgeResponse]:
    """List edges in a workspace with optional type filter."""
    if graph_client is None:
        return []
    edges = await graph_client.get_edges(workspace_id, edge_type=edge_type)
    return [
        EdgeResponse(
            id=e.id,
            type=str(e.type),
            source_id=e.source_id,
            target_id=e.target_id,
            properties=e.properties or {},
            weight=float(e.weight) if e.weight else 1.0,
        )
        for e in edges[:limit]
    ]


@router.delete("/{edge_id}", status_code=204)
async def delete_relationship(
    workspace_id: str,
    edge_id: str,
    tenant_id: str = Depends(get_current_tenant),
    graph_client: Any = Depends(get_graph_client),
) -> None:
    """Delete a relationship."""
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")
    # Edge deletion is backend-specific; use execute_query for direct deletion
    try:
        await graph_client.execute_query(
            workspace_id=workspace_id,
            query=f"DELETE FROM edges WHERE id = '{edge_id}'",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
