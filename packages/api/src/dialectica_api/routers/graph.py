"""
Graph Router — Graph traversal, search, and stats endpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from dialectica_api.deps import get_current_tenant, get_graph_client, require_admin

router = APIRouter(prefix="/v1/workspaces/{workspace_id}/graph", tags=["graph"])


class GraphStatsResponse(BaseModel):
    workspace_id: str
    total_nodes: int = 0
    total_edges: int = 0
    node_type_counts: dict[str, int] = {}
    edge_type_counts: dict[str, int] = {}


class SubgraphResponse(BaseModel):
    center_id: str
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    hops: int = 2


class SearchResult(BaseModel):
    node_id: str
    label: str
    name: str
    score: float


@router.get("", response_model=dict[str, Any])
async def get_full_graph(
    workspace_id: str,
    limit: int = Query(200, le=1000),
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> dict[str, Any]:
    """Return full workspace graph (nodes + edges)."""
    if graph_client is None:
        return {"nodes": [], "edges": []}
    nodes = await graph_client.get_nodes(workspace_id, limit=limit)
    edges = await graph_client.get_edges(workspace_id)

    return {
        "nodes": [
            {
                "id": n.id,
                "label": getattr(n, "label", n.__class__.__name__),
                "name": getattr(n, "name", n.id),
                "confidence": getattr(n, "confidence", 1.0),
            }
            for n in nodes
        ],
        "edges": [
            {
                "id": e.id,
                "type": str(e.type),
                "source": e.source_id,
                "target": e.target_id,
                "weight": e.weight or 1.0,
            }
            for e in edges
        ],
    }


@router.get("/stats", response_model=GraphStatsResponse)
async def get_graph_stats(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> GraphStatsResponse:
    """Get workspace graph statistics."""
    if graph_client is None:
        return GraphStatsResponse(workspace_id=workspace_id)

    try:
        stats = await graph_client.get_workspace_stats(workspace_id)
        return GraphStatsResponse(
            workspace_id=workspace_id,
            total_nodes=getattr(stats, "total_nodes", 0),
            total_edges=getattr(stats, "total_edges", 0),
            node_type_counts=getattr(stats, "node_type_counts", {}),
            edge_type_counts=getattr(stats, "edge_type_counts", {}),
        )
    except Exception:
        return GraphStatsResponse(workspace_id=workspace_id)


@router.get("/subgraph", response_model=SubgraphResponse)
async def get_subgraph(
    workspace_id: str,
    center_id: str = Query(...),
    hops: int = Query(2, ge=1, le=4),
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> SubgraphResponse:
    """Get N-hop subgraph centered on a node."""
    if graph_client is None:
        return SubgraphResponse(center_id=center_id)

    try:
        result = await graph_client.traverse(center_id, workspace_id, hops=hops)
        nodes = [
            {"id": n.id, "label": getattr(n, "label", ""), "name": getattr(n, "name", n.id)}
            for n in getattr(result, "nodes", [])
        ]
        edges = [
            {"id": e.id, "type": str(e.type), "source": e.source_id, "target": e.target_id}
            for e in getattr(result, "edges", [])
        ]
        return SubgraphResponse(center_id=center_id, nodes=nodes, edges=edges, hops=hops)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/search", response_model=list[SearchResult])
async def search_graph(
    workspace_id: str,
    q: str = Query(..., min_length=1),
    limit: int = Query(20, le=100),
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> list[SearchResult]:
    """Semantic/keyword search in the workspace graph."""
    if graph_client is None:
        return []

    results: list[SearchResult] = []

    # Try vector search first
    try:
        if hasattr(graph_client, "vector_search"):
            scored = await graph_client.vector_search(
                query_text=q, workspace_id=workspace_id, top_k=limit
            )
            for s in scored:
                node = getattr(s, "node", None)
                if node:
                    results.append(
                        SearchResult(
                            node_id=node.id,
                            label=getattr(node, "label", ""),
                            name=getattr(node, "name", node.id),
                            score=float(getattr(s, "score", 0.5)),
                        )
                    )
    except Exception:
        pass

    # Fallback: keyword match
    if not results:
        nodes = await graph_client.get_nodes(workspace_id, limit=500)
        q_lower = q.lower()
        for n in nodes:
            name = getattr(n, "name", "") or ""
            if q_lower in name.lower():
                results.append(
                    SearchResult(
                        node_id=n.id,
                        label=getattr(n, "label", ""),
                        name=name,
                        score=0.7,
                    )
                )
        results = results[:limit]

    return results


@router.post("/query", response_model=dict[str, Any])
async def raw_query(
    workspace_id: str,
    body: dict[str, Any],
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    _admin: None = Depends(require_admin),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> dict[str, Any]:
    """Execute raw GQL/Cypher query (admin only)."""
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")
    query = body.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="'query' field required.")
    try:
        result = await graph_client.execute_query(workspace_id=workspace_id, query=query)
        return {"result": result, "query": query}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
