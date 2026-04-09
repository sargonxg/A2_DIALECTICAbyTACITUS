"""
Integration Router — TACITUS inter-app communication endpoints.

Machine-to-machine endpoints for TACITUS ecosystem apps (Praxis, Top-level Query,
Trust Graph). All endpoints require admin authentication.

Endpoints:
  - GET /v1/integration/graph/{workspace_id} — Full graph snapshot
  - GET /v1/integration/context/{workspace_id} — Structured conflict context for Praxis
  - POST /v1/integration/query — Execute conflict query for TACITUS query layer
"""

from __future__ import annotations

import logging
import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from dialectica_api.deps import get_graph_client, get_query_engine, require_admin

logger = logging.getLogger("dialectica.integration")

router = APIRouter(prefix="/v1/integration", tags=["integration"])

# ── Validation helpers ───────────────────────────────────────────────────────

_WORKSPACE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")


def _validate_workspace_id(workspace_id: str) -> str:
    """Validate workspace_id format."""
    if not _WORKSPACE_ID_PATTERN.match(workspace_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Invalid workspace_id format. "
                "Must be 1-128 alphanumeric, dash, or underscore characters."
            ),
        )
    return workspace_id


# ── Response models ──────────────────────────────────────────────────────────


class GraphNodeResponse(BaseModel):
    id: str
    label: str = ""
    name: str = ""
    properties: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0


class GraphEdgeResponse(BaseModel):
    id: str
    type: str = ""
    source_id: str = ""
    target_id: str = ""
    weight: float = 0.0


class GraphSnapshotResponse(BaseModel):
    workspace_id: str
    nodes: list[GraphNodeResponse] = Field(default_factory=list)
    edges: list[GraphEdgeResponse] = Field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0
    subdomain: str | None = None
    escalation_stage: int | None = None
    ripeness_score: float | None = None


class ContextResponse(BaseModel):
    workspace_id: str
    context_text: str = ""
    key_actors: list[str] = Field(default_factory=list)
    key_issues: list[str] = Field(default_factory=list)
    escalation_summary: str = ""
    theory_recommendation: str = ""


class QueryRequest(BaseModel):
    workspace_id: str
    query: str = Field(..., min_length=1, max_length=10000)
    mode: str = "general"


class QueryResponse(BaseModel):
    answer: str = ""
    confidence: float = 0.0
    citations: list[dict[str, Any]] = Field(default_factory=list)
    reasoning_trace: list[str] = Field(default_factory=list)
    escalation_stage: int | None = None
    patterns_detected: list[str] = Field(default_factory=list)


# ── Endpoints ────────────────────────────────────────────────────────────────


@router.get("/graph/{workspace_id}", response_model=GraphSnapshotResponse)
async def get_graph_snapshot(
    workspace_id: str,
    _admin: None = Depends(require_admin),
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> GraphSnapshotResponse:
    """Return full graph snapshot (all nodes + edges) for a workspace.

    Used by TACITUS Trust Graph layer and Praxis for graph state sync.
    """
    workspace_id = _validate_workspace_id(workspace_id)

    if graph_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Graph client unavailable.",
        )

    try:
        nodes = await graph_client.get_nodes(workspace_id, limit=10000)
        edges = await graph_client.get_edges(workspace_id)
    except Exception as exc:
        logger.error(
            '{"event":"graph_snapshot_error","workspace":"%s","error":"%s"}',
            workspace_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to retrieve graph data: {exc}",
        ) from exc

    node_responses = [
        GraphNodeResponse(
            id=getattr(n, "id", ""),
            label=getattr(n, "label", ""),
            name=getattr(n, "name", ""),
            properties=getattr(n, "properties", {}),
            confidence=getattr(n, "confidence", 0.0),
        )
        for n in nodes
    ]

    edge_responses = [
        GraphEdgeResponse(
            id=getattr(e, "id", ""),
            type=str(getattr(e, "type", "")),
            source_id=getattr(e, "source_id", ""),
            target_id=getattr(e, "target_id", ""),
            weight=getattr(e, "weight", 0.0),
        )
        for e in edges
    ]

    # Attempt to get escalation data
    escalation_stage: int | None = None
    ripeness_score: float | None = None
    try:
        esc = await graph_client.get_escalation_trajectory(workspace_id)
        escalation_stage = esc.current_stage
    except Exception:
        pass

    return GraphSnapshotResponse(
        workspace_id=workspace_id,
        nodes=node_responses,
        edges=edge_responses,
        node_count=len(node_responses),
        edge_count=len(edge_responses),
        escalation_stage=escalation_stage,
        ripeness_score=ripeness_score,
    )


@router.get("/context/{workspace_id}", response_model=ContextResponse)
async def get_conflict_context(
    workspace_id: str,
    _admin: None = Depends(require_admin),
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> ContextResponse:
    """Return structured conflict context for Praxis integration.

    Builds a context summary including key actors, issues, escalation state,
    and theory recommendations suitable for downstream TACITUS apps.
    """
    workspace_id = _validate_workspace_id(workspace_id)

    if graph_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Graph client unavailable.",
        )

    try:
        nodes = await graph_client.get_nodes(workspace_id, limit=10000)
        edges = await graph_client.get_edges(workspace_id)
    except Exception as exc:
        logger.error('{"event":"context_error","workspace":"%s","error":"%s"}', workspace_id, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to retrieve graph data: {exc}",
        ) from exc

    # Extract key actors
    key_actors = [
        getattr(n, "name", getattr(n, "id", ""))
        for n in nodes
        if getattr(n, "label", "") == "Actor"
    ]

    # Extract key issues
    key_issues = [
        getattr(n, "name", getattr(n, "id", ""))
        for n in nodes
        if getattr(n, "label", "") in ("Issue", "Conflict", "Grievance")
    ]

    # Get escalation summary
    escalation_summary = "Unknown"
    try:
        esc = await graph_client.get_escalation_trajectory(workspace_id)
        escalation_summary = (
            f"Stage {esc.current_stage}, direction: {esc.direction}, "
            f"velocity: {round(esc.velocity, 2)}"
        )
    except Exception:
        pass

    # Build context text
    context_parts = [
        f"Conflict workspace: {workspace_id}",
        f"Actors ({len(key_actors)}): {', '.join(key_actors[:20])}",
        f"Issues ({len(key_issues)}): {', '.join(key_issues[:20])}",
        f"Graph: {len(nodes)} nodes, {len(edges)} edges",
        f"Escalation: {escalation_summary}",
    ]
    context_text = "\n".join(context_parts)

    # Attempt theory recommendation
    theory_recommendation = ""
    try:
        from dialectica_reasoning.graphrag import ConflictContextBuilder

        builder = ConflictContextBuilder()
        theory_recommendation = builder.get_theory_recommendation(workspace_id)
    except Exception:
        theory_recommendation = "Theory recommendation unavailable."

    return ContextResponse(
        workspace_id=workspace_id,
        context_text=context_text,
        key_actors=key_actors[:50],
        key_issues=key_issues[:50],
        escalation_summary=escalation_summary,
        theory_recommendation=theory_recommendation,
    )


@router.post("/query", response_model=QueryResponse)
async def query_conflict(
    body: QueryRequest,
    _admin: None = Depends(require_admin),
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
    query_engine: Any = Depends(get_query_engine),  # noqa: B008
) -> QueryResponse:
    """Execute a conflict analysis query for the TACITUS top-level query layer.

    Runs the full ConflictQueryEngine analysis pipeline including retrieval,
    symbolic reasoning, and synthesis.
    """
    _validate_workspace_id(body.workspace_id)

    if graph_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Graph client unavailable.",
        )

    if query_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Query engine unavailable — reasoning package may not be installed.",
        )

    try:
        result = await query_engine.analyze(
            query=body.query,
            workspace_id=body.workspace_id,
            mode=body.mode,
        )
    except Exception as exc:
        logger.error(
            '{"event":"query_error","workspace":"%s","error":"%s"}',
            body.workspace_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Query execution failed: {exc}",
        ) from exc

    # Convert reasoning_trace items to strings (they may be ReasoningStep objects)
    raw_trace = getattr(result, "reasoning_trace", [])
    reasoning_trace = [str(step) for step in raw_trace]

    return QueryResponse(
        answer=getattr(result, "answer", str(result)),
        confidence=getattr(result, "confidence", 0.5),
        citations=getattr(result, "citations", []),
        reasoning_trace=reasoning_trace,
        escalation_stage=getattr(result, "escalation_stage", None),
        patterns_detected=getattr(result, "patterns_detected", []),
    )
