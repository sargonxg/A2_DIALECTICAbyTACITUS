"""Graph reasoning subsystem routes."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.graph_reasoning.schema import IngestResult, IngestTextRequest
from app.graph_reasoning.sql_store import GraphReasoningSqlStore
from app.graph_reasoning.sync_service import GraphReasoningService
from dialectica_api.database.deps import get_db

router = APIRouter(tags=["graph_reasoning"])

_service: GraphReasoningService | None = None


def get_graph_reasoning_service() -> GraphReasoningService:
    global _service
    if _service is None:
        _service = GraphReasoningService()
    return _service


@router.post("/ingest/text", response_model=IngestResult)
async def ingest_text(
    body: IngestTextRequest,
    request: Request,
    service: GraphReasoningService = Depends(get_graph_reasoning_service),  # noqa: B008
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> IngestResult:
    tenant_id = getattr(request.state, "tenant_id", "default")
    try:
        return await service.ingest_text(
            text=body.text,
            workspace_id=body.workspace_id,
            tenant_id=tenant_id,
            source_title=body.source_title,
            source_uri=body.source_uri,
            source_type=body.source_type,
            objective=body.objective,
            ontology_profile=body.ontology_profile,
            occurred_at=body.occurred_at,
            force=body.force,
            db_session=db,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/graph/actor/{actor_id}")
async def get_actor(
    actor_id: str,
    workspace_id: str | None = None,
    service: GraphReasoningService = Depends(get_graph_reasoning_service),  # noqa: B008
) -> dict[str, Any]:
    actor = await service.actor(actor_id, workspace_id=workspace_id)
    if actor is None:
        raise HTTPException(status_code=404, detail=f"Actor {actor_id!r} not found")
    return actor


@router.get("/graph/search")
async def search_graph(
    q: str = Query(..., min_length=1),
    workspace_id: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    service: GraphReasoningService = Depends(get_graph_reasoning_service),  # noqa: B008
) -> dict[str, Any]:
    return {"results": await service.search(q, workspace_id=workspace_id, limit=limit)}


@router.get("/reasoning/actor/{actor_id}")
async def reasoning_actor(
    actor_id: str,
    workspace_id: str | None = None,
    service: GraphReasoningService = Depends(get_graph_reasoning_service),  # noqa: B008
) -> dict[str, Any]:
    return await service.reasoning_actor(actor_id, workspace_id=workspace_id)


@router.get("/reasoning/constraints/{actor_id}")
async def reasoning_constraints(
    actor_id: str,
    workspace_id: str | None = None,
    service: GraphReasoningService = Depends(get_graph_reasoning_service),  # noqa: B008
) -> dict[str, Any]:
    return service.reasoning.indirect_constraints(actor_id, workspace_id=workspace_id)


@router.get("/reasoning/leverage/{actor_id}")
async def reasoning_leverage(
    actor_id: str,
    workspace_id: str | None = None,
    service: GraphReasoningService = Depends(get_graph_reasoning_service),  # noqa: B008
) -> dict[str, Any]:
    return service.reasoning.leverage_map(actor_id, workspace_id=workspace_id)


@router.get("/reasoning/provenance/{object_id}")
async def reasoning_provenance(
    object_id: str,
    workspace_id: str | None = None,
    service: GraphReasoningService = Depends(get_graph_reasoning_service),  # noqa: B008
) -> dict[str, Any]:
    return service.reasoning.provenance_trace(object_id, workspace_id=workspace_id)


@router.get("/reasoning/timeline")
async def reasoning_timeline(
    actor_ids: str = Query(""),
    start: str | None = None,
    end: str | None = None,
    workspace_id: str | None = None,
    service: GraphReasoningService = Depends(get_graph_reasoning_service),  # noqa: B008
) -> dict[str, Any]:
    ids = [item.strip() for item in actor_ids.split(",") if item.strip()]
    return service.reasoning.timeline(ids, start=start, end=end, workspace_id=workspace_id)


@router.get("/reasoning/changed-since")
async def reasoning_changed_since(
    timestamp: datetime,
    workspace_id: str | None = None,
    service: GraphReasoningService = Depends(get_graph_reasoning_service),  # noqa: B008
) -> dict[str, Any]:
    return await service.changed_since(timestamp, workspace_id=workspace_id)


@router.get("/pipeline/runs")
async def pipeline_runs(
    workspace_id: str | None = None,
    limit: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict[str, Any]:
    runs = await GraphReasoningSqlStore(db).list_runs(
        workspace_id=workspace_id,
        limit=limit,
    )
    return {"runs": runs}


@router.get("/pipeline/runs/{run_id}")
async def pipeline_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> dict[str, Any]:
    payload = await GraphReasoningSqlStore(db).get_run(run_id)
    if payload is None:
        raise HTTPException(status_code=404, detail=f"Pipeline run {run_id!r} not found")
    return payload
