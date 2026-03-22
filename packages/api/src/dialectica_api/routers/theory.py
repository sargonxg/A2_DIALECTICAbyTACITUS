"""
Theory Router — Theory framework assessment endpoints.
"""

from __future__ import annotations

import json
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from dialectica_api.deps import get_current_tenant, get_graph_client

router = APIRouter(tags=["theory"])

_FRAMEWORKS_PATH = os.path.join(
    os.path.dirname(__file__), "../../../../../../data/seed/frameworks.json"
)


def _load_frameworks() -> list[dict[str, Any]]:
    try:
        with open(_FRAMEWORKS_PATH) as f:
            data = json.load(f)
        return data.get("frameworks", [])
    except Exception:
        return []


@router.get("/v1/theory/frameworks", response_model=list[dict[str, Any]])
async def list_frameworks(
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
) -> list[dict[str, Any]]:
    """List all 15 conflict theory frameworks."""
    return _load_frameworks()


@router.get("/v1/theory/frameworks/{framework_id}", response_model=dict[str, Any])
async def get_framework(
    framework_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
) -> dict[str, Any]:
    """Get a specific theory framework by ID."""
    frameworks = _load_frameworks()
    framework = next((f for f in frameworks if f.get("id") == framework_id), None)
    if not framework:
        raise HTTPException(status_code=404, detail=f"Framework '{framework_id}' not found.")
    return framework


@router.get("/v1/workspaces/{workspace_id}/theory")
async def apply_all_theories(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> dict[str, Any]:
    """Apply all 15 frameworks and rank their applicability to the workspace."""
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")
    from dialectica_reasoning.agents.theorist import TheoristAgent

    agent = TheoristAgent(graph_client)
    report = await agent.run(workspace_id)
    return {
        "workspace_id": workspace_id,
        "top_framework": report.top_framework,
        "synthesis": report.synthesis,
        "assessments": [
            {
                "framework_id": a.framework_id,
                "name": a.framework_name,
                "applicability": a.applicability_score,
                "insights": a.key_insights,
                "indicators": a.indicators_present,
            }
            for a in report.assessments
        ],
    }


@router.get("/v1/workspaces/{workspace_id}/theory/{framework_id}")
async def apply_framework(
    workspace_id: str,
    framework_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
) -> dict[str, Any]:
    """Apply a specific framework to the workspace."""
    if graph_client is None:
        raise HTTPException(status_code=503, detail="Graph client unavailable.")
    from dialectica_reasoning.agents.theorist import TheoristAgent

    agent = TheoristAgent(graph_client)
    report = await agent.run(workspace_id)
    assessment = next((a for a in report.assessments if a.framework_id == framework_id), None)
    if not assessment:
        raise HTTPException(status_code=404, detail=f"Framework '{framework_id}' not found.")
    return {
        "framework_id": assessment.framework_id,
        "name": assessment.framework_name,
        "applicability": assessment.applicability_score,
        "insights": assessment.key_insights,
        "indicators": assessment.indicators_present,
        "limitations": assessment.limitations,
    }
