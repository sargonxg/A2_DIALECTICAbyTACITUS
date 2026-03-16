"""
Entities Router — CRUD for conflict graph nodes.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from dialectica_api.deps import get_graph_client, get_current_tenant

router = APIRouter(prefix="/v1/workspaces/{workspace_id}/entities", tags=["entities"])


class NodeResponse(BaseModel):
    id: str
    label: str
    name: str
    properties: dict[str, Any] = {}
    confidence: float = 1.0


class NodeCreate(BaseModel):
    label: str
    name: str
    properties: dict[str, Any] = {}
    confidence: float = 1.0


@router.get("", response_model=list[NodeResponse])
async def list_entities(
    workspace_id: str,
    label: str | None = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    tenant_id: str = Depends(get_current_tenant),
    graph_client: Any = Depends(get_graph_client),
) -> list[NodeResponse]:
    """List entities in a workspace with optional label filter."""
    if graph_client is None:
        return []
    nodes = await graph_client.get_nodes(workspace_id, label=label, limit=limit, offset=offset)
    return [
        NodeResponse(
            id=n.id,
            label=getattr(n, "label", n.__class__.__name__),
            name=getattr(n, "name", n.id),
            properties={
                k: v for k, v in (n.model_dump() if hasattr(n, "model_dump") else vars(n)).items()
                if k not in ("id", "label", "name", "tenant_id", "workspace_id")
            },
            confidence=float(getattr(n, "confidence", 1.0)),
        )
        for n in nodes
    ]


@router.get("/{entity_id}", response_model=NodeResponse)
async def get_entity(
    workspace_id: str,
    entity_id: str,
    tenant_id: str = Depends(get_current_tenant),
    graph_client: Any = Depends(get_graph_client),
) -> NodeResponse:
    """Get a single entity by ID."""
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")
    node = await graph_client.get_node(entity_id, workspace_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Entity '{entity_id}' not found.")
    return NodeResponse(
        id=node.id,
        label=getattr(node, "label", node.__class__.__name__),
        name=getattr(node, "name", node.id),
        properties={},
        confidence=float(getattr(node, "confidence", 1.0)),
    )


@router.delete("/{entity_id}", status_code=204)
async def delete_entity(
    workspace_id: str,
    entity_id: str,
    hard: bool = Query(False),
    tenant_id: str = Depends(get_current_tenant),
    graph_client: Any = Depends(get_graph_client),
) -> None:
    """Delete an entity (soft delete by default)."""
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")
    deleted = await graph_client.delete_node(entity_id, workspace_id, hard=hard)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Entity '{entity_id}' not found.")
