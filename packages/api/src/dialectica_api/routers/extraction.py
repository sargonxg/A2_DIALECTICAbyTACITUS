"""
Extraction Router — Text and document extraction endpoints.

Public surface:
- ``POST /v1/workspaces/{ws}/extract``           — inline text -> queued job
- ``POST /v1/workspaces/{ws}/extract/document``  — file upload -> queued job
- ``GET  /v1/workspaces/{ws}/extractions``       — list jobs in workspace
- ``GET  /v1/workspaces/{ws}/extractions/{id}``  — fetch single job

Job state lives in ``services.job_store.JobStore``. SSE progress streaming
is handled by ``routers/extraction_stream.py``.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from collections.abc import Iterator, ValuesView
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from dialectica_api.deps import get_current_tenant, get_graph_client
from dialectica_api.services.job_store import JobStore, get_job_store
from dialectica_api.services.pipeline_runner import run_pipeline_with_progress

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/workspaces/{workspace_id}", tags=["extraction"])

PUBSUB_TOPIC = os.getenv("PUBSUB_EXTRACTION_TOPIC", "dialectica-extraction-requests")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")


# Backwards-compat re-export — older tests and conftest reach into ``_jobs``
# directly. Expose it as a property of the singleton store.
class _JobsProxy:
    def __getitem__(self, key: str) -> dict[str, Any]:
        return get_job_store()._jobs[key]

    def __contains__(self, key: str) -> bool:
        return key in get_job_store()._jobs

    def __iter__(self) -> Iterator[str]:
        return iter(get_job_store()._jobs)

    def values(self) -> ValuesView[dict[str, Any]]:
        return get_job_store()._jobs.values()

    def clear(self) -> None:
        get_job_store().clear()


_jobs = _JobsProxy()


class ExtractRequest(BaseModel):
    text: str = ""
    gcs_uri: str = ""
    source_url: str = ""
    source_title: str = ""
    tier: str = "standard"
    priority: int = 0


class ExtractionJob(BaseModel):
    job_id: str
    workspace_id: str
    status: str  # "queued" | "running" | "complete" | "failed"
    created_at: str
    completed_at: str | None = None
    nodes_extracted: int = 0
    edges_extracted: int = 0
    error: str | None = None
    source_title: str = ""
    source_kind: str = "text"  # "text" | "document" | "gutenberg"


# ─── Helpers ──────────────────────────────────────────────────────────────


def _publish_to_pubsub(message: dict[str, Any]) -> bool:
    """Publish a message to the extraction Pub/Sub topic."""
    try:
        from google.cloud import pubsub_v1

        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(GCP_PROJECT_ID, PUBSUB_TOPIC)
        data = json.dumps(message).encode("utf-8")
        publisher.publish(topic_path, data)
        return True
    except Exception as e:
        logger.warning("Pub/Sub publish failed: %s", e)
        return False


def _new_job(
    workspace_id: str,
    *,
    source_title: str = "",
    source_kind: str = "text",
) -> dict[str, Any]:
    job_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat()
    return {
        "job_id": job_id,
        "workspace_id": workspace_id,
        "status": "queued",
        "created_at": now,
        "completed_at": None,
        "nodes_extracted": 0,
        "edges_extracted": 0,
        "error": None,
        "source_title": source_title,
        "source_kind": source_kind,
    }


def _schedule_extraction(
    job: dict[str, Any],
    *,
    text: str,
    tier: str,
    tenant_id: str,
    workspace_id: str,
    source_title: str,
    source_kind: str,
    graph_client: Any,
    store: JobStore,
) -> None:
    """Either publish to Pub/Sub or run inline; either way persist + return."""
    pubsub_msg = {
        "document_id": job["job_id"],
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "tier": tier,
        "priority": 0,
        "text": text[:50_000] if text else "",
        "source_title": source_title,
        "source_kind": source_kind,
    }
    published = _publish_to_pubsub(pubsub_msg)

    if published:
        store.upsert_job(job)
        return

    # Pub/Sub unavailable — run inline in a background task so the HTTP
    # response can return immediately while the SSE stream observes
    # progress events live.
    if not text:
        job["status"] = "complete"
        job["completed_at"] = datetime.utcnow().isoformat()
        store.upsert_job(job)
        return

    store.upsert_job(job)
    asyncio.create_task(
        run_pipeline_with_progress(
            job_id=job["job_id"],
            text=text,
            tier=tier,
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            source_title=source_title,
            source_kind=source_kind,
            graph_client=graph_client,
            store=store,
        )
    )


# ─── Endpoints ────────────────────────────────────────────────────────────


@router.post("/extract", response_model=ExtractionJob, status_code=202)
async def extract_text(
    workspace_id: str,
    body: ExtractRequest,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
    store: JobStore = Depends(get_job_store),  # noqa: B008
) -> ExtractionJob:
    """Extract conflict entities from text — queues for async processing."""
    job = _new_job(
        workspace_id,
        source_title=body.source_title,
        source_kind="text",
    )
    _schedule_extraction(
        job,
        text=body.text,
        tier=body.tier,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        source_title=body.source_title,
        source_kind="text",
        graph_client=graph_client,
        store=store,
    )
    return ExtractionJob(**store.get_job(job["job_id"]) or job)


@router.post("/extract/document", response_model=ExtractionJob, status_code=202)
async def extract_document(
    workspace_id: str,
    file: UploadFile = File(...),  # noqa: B008
    tier: str = "standard",
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
    store: JobStore = Depends(get_job_store),  # noqa: B008
) -> ExtractionJob:
    """Extract conflict entities from an uploaded document."""
    content = await file.read()
    text = content.decode("utf-8", errors="replace")
    job = _new_job(
        workspace_id,
        source_title=file.filename or "uploaded document",
        source_kind="document",
    )
    _schedule_extraction(
        job,
        text=text,
        tier=tier,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        source_title=file.filename or "uploaded document",
        source_kind="document",
        graph_client=graph_client,
        store=store,
    )
    return ExtractionJob(**store.get_job(job["job_id"]) or job)


@router.get("/extractions", response_model=list[ExtractionJob])
async def list_jobs(
    workspace_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    store: JobStore = Depends(get_job_store),  # noqa: B008
) -> list[ExtractionJob]:
    """List extraction jobs for a workspace."""
    return [ExtractionJob(**j) for j in store.list_jobs(workspace_id=workspace_id)]


@router.get("/extractions/{job_id}", response_model=ExtractionJob)
async def get_job(
    workspace_id: str,
    job_id: str,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    store: JobStore = Depends(get_job_store),  # noqa: B008
) -> ExtractionJob:
    """Get status of an extraction job."""
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return ExtractionJob(**job)
