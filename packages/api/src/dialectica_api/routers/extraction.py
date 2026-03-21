"""
Extraction Router — Text and document extraction endpoints.

POST /v1/extract publishes to Pub/Sub for async processing.
GET /v1/extract/{job_id}/status checks job state in Redis.
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from dialectica_api.deps import get_graph_client, get_current_tenant

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/workspaces/{workspace_id}", tags=["extraction"])

# In-memory job store (Redis in production)
_jobs: dict[str, dict[str, Any]] = {}

PUBSUB_TOPIC = os.getenv("PUBSUB_EXTRACTION_TOPIC", "dialectica-extraction-requests")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")


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


def _store_job(job: dict[str, Any]) -> None:
    """Store job state (in-memory; use Redis in production)."""
    _jobs[job["job_id"]] = job


def _get_job(job_id: str) -> dict[str, Any] | None:
    """Retrieve job state."""
    return _jobs.get(job_id)


@router.post("/extract", response_model=ExtractionJob, status_code=202)
async def extract_text(
    workspace_id: str,
    body: ExtractRequest,
    tenant_id: str = Depends(get_current_tenant),
    graph_client: Any = Depends(get_graph_client),
) -> ExtractionJob:
    """Extract conflict entities from text — queues for async processing."""
    job_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat()

    job: dict[str, Any] = {
        "job_id": job_id,
        "workspace_id": workspace_id,
        "status": "queued",
        "created_at": now,
        "completed_at": None,
        "nodes_extracted": 0,
        "edges_extracted": 0,
        "error": None,
    }

    # Try async Pub/Sub first
    pubsub_msg = {
        "document_id": job_id,
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "gcs_uri": body.gcs_uri,
        "tier": body.tier,
        "priority": body.priority,
        "text": body.text[:50000] if body.text else "",  # Limit inline text
    }

    published = _publish_to_pubsub(pubsub_msg)

    if not published:
        # Fallback: synchronous extraction
        if graph_client and body.text:
            try:
                from dialectica_extraction.pipeline import ExtractionPipeline
                from dialectica_ontology.tiers import OntologyTier

                pipeline = ExtractionPipeline()
                job["status"] = "running"
                result = pipeline.run(
                    text=body.text,
                    tier=OntologyTier(body.tier),
                    workspace_id=workspace_id,
                    tenant_id=tenant_id,
                )
                job["status"] = "complete"
                stats = result.get("ingestion_stats", {})
                job["nodes_extracted"] = stats.get("nodes_written", 0)
                job["edges_extracted"] = stats.get("edges_written", 0)
                job["completed_at"] = datetime.utcnow().isoformat()
            except Exception as exc:
                job["status"] = "failed"
                job["error"] = str(exc)[:200]
        else:
            job["status"] = "complete"
            job["completed_at"] = datetime.utcnow().isoformat()

    _store_job(job)
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
        "status": "queued",
        "created_at": now,
        "completed_at": None,
        "nodes_extracted": 0,
        "edges_extracted": 0,
        "error": None,
    }

    pubsub_msg = {
        "document_id": job_id,
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "gcs_uri": "",
        "tier": tier,
        "priority": 0,
        "text": text[:50000],
    }
    _publish_to_pubsub(pubsub_msg)
    _store_job(job)
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
    job = _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return ExtractionJob(**job)
