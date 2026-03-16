"""
Extraction Router — Text and document extraction endpoints.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from dialectica_api.deps import get_graph_client, get_current_tenant

router = APIRouter(prefix="/v1/workspaces/{workspace_id}", tags=["extraction"])

# In-memory job store
_jobs: dict[str, dict[str, Any]] = {}


class ExtractRequest(BaseModel):
    text: str
    source_url: str = ""
    source_title: str = ""
    tier: str = "standard"


class ExtractionJob(BaseModel):
    job_id: str
    workspace_id: str
    status: str  # "pending" | "running" | "complete" | "failed"
    created_at: str
    completed_at: str | None = None
    nodes_extracted: int = 0
    edges_extracted: int = 0
    error: str | None = None


@router.post("/extract", response_model=ExtractionJob, status_code=202)
async def extract_text(
    workspace_id: str,
    body: ExtractRequest,
    tenant_id: str = Depends(get_current_tenant),
    graph_client: Any = Depends(get_graph_client),
) -> ExtractionJob:
    """Extract conflict entities from text and add to workspace graph."""
    job_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat()
    job: dict[str, Any] = {
        "job_id": job_id,
        "workspace_id": workspace_id,
        "status": "pending",
        "created_at": now,
        "completed_at": None,
        "nodes_extracted": 0,
        "edges_extracted": 0,
        "error": None,
    }
    _jobs[job_id] = job

    # Attempt extraction via pipeline if available
    if graph_client and body.text:
        try:
            from dialectica_extraction import ExtractionPipeline  # type: ignore[import-not-found]
            pipeline = ExtractionPipeline(graph_client=graph_client)
            job["status"] = "running"
            result = await pipeline.extract(
                text=body.text,
                workspace_id=workspace_id,
                tenant_id=tenant_id,
                tier=body.tier,
            )
            job["status"] = "complete"
            job["nodes_extracted"] = getattr(result, "nodes_created", 0)
            job["edges_extracted"] = getattr(result, "edges_created", 0)
            job["completed_at"] = datetime.utcnow().isoformat()
        except ImportError:
            job["status"] = "complete"
            job["completed_at"] = datetime.utcnow().isoformat()
            job["error"] = "Extraction pipeline not configured (Gemini/Vertex AI required)."
        except Exception as exc:
            job["status"] = "failed"
            job["error"] = str(exc)[:200]
    else:
        job["status"] = "complete"
        job["completed_at"] = datetime.utcnow().isoformat()

    return ExtractionJob(**job)


@router.post("/extract/document", response_model=ExtractionJob, status_code=202)
async def extract_document(
    workspace_id: str,
    file: UploadFile = File(...),
    tier: str = "standard",
    tenant_id: str = Depends(get_current_tenant),
    graph_client: Any = Depends(get_graph_client),
) -> ExtractionJob:
    """Extract conflict entities from an uploaded document."""
    content = await file.read()
    text = content.decode("utf-8", errors="replace")
    job_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat()
    job: dict[str, Any] = {
        "job_id": job_id,
        "workspace_id": workspace_id,
        "status": "complete",
        "created_at": now,
        "completed_at": now,
        "nodes_extracted": 0,
        "edges_extracted": 0,
        "error": f"Document '{file.filename}' received ({len(text)} chars). LLM pipeline required.",
    }
    _jobs[job_id] = job
    return ExtractionJob(**job)


@router.get("/extractions", response_model=list[ExtractionJob])
async def list_jobs(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),
) -> list[ExtractionJob]:
    """List extraction jobs for a workspace."""
    return [
        ExtractionJob(**j)
        for j in _jobs.values()
        if j["workspace_id"] == workspace_id
    ]


@router.get("/extractions/{job_id}", response_model=ExtractionJob)
async def get_job(
    workspace_id: str,
    job_id: str,
    tenant_id: str = Depends(get_current_tenant),
) -> ExtractionJob:
    """Get status of an extraction job."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return ExtractionJob(**job)
