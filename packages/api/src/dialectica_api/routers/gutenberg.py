"""
Gutenberg Router — Project Gutenberg book picker + ingest endpoints.

Public surface:
- ``GET  /v1/gutenberg/catalog``                                — curated 8-book list
- ``POST /v1/workspaces/{ws}/ingest/gutenberg``                 — fetch + queue ingest

The ``catalog`` endpoint is added to ``_PUBLIC_PATHS`` so the demo page
can render the picker without an API key.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from dialectica_api.deps import get_current_tenant, get_graph_client
from dialectica_api.routers.extraction import _new_job
from dialectica_api.services.job_store import (
    JobProgressEvent,
    JobStore,
    get_job_store,
)
from dialectica_api.services.pipeline_runner import run_pipeline_with_progress
from dialectica_extraction.sources.gutenberg import (
    GUTENBERG_CATALOG,
    fetch_gutenberg_text,
    get_book,
)

logger = logging.getLogger(__name__)

# Keep the catalog endpoint at the global prefix and the ingest endpoint
# under the workspace prefix so workspace_id is path-bound.
catalog_router = APIRouter(prefix="/v1/gutenberg", tags=["gutenberg"])
ingest_router = APIRouter(prefix="/v1/workspaces/{workspace_id}", tags=["gutenberg"])

# Demos shouldn't pull a 600k-word book by default. Hard cap inline ingestion
# so a single click can't accidentally OOM the dev container.
DEFAULT_MAX_CHARS = 60_000
HARD_MAX_CHARS = 500_000


class GutenbergCatalogEntry(BaseModel):
    book_id: str
    title: str
    author: str
    domain: str
    subdomain: str
    summary: str
    estimated_words: int
    recommended_tier: str


class GutenbergCatalogResponse(BaseModel):
    books: list[GutenbergCatalogEntry]


class GutenbergIngestRequest(BaseModel):
    book_id: str = Field(..., description="Project Gutenberg numeric ID, e.g. '1513'.")
    title: str = ""
    tier: str = "standard"
    max_chars: int = Field(
        DEFAULT_MAX_CHARS,
        ge=0,
        le=HARD_MAX_CHARS,
        description=(
            "Truncate the fetched text to this many characters. 0 means no "
            f"truncation (capped at {HARD_MAX_CHARS} regardless)."
        ),
    )


class GutenbergIngestResponse(BaseModel):
    job_id: str
    workspace_id: str
    book_id: str
    title: str
    status: str
    fetched_chars: int
    estimated_words: int
    created_at: str


# ─── Endpoints ────────────────────────────────────────────────────────────


@catalog_router.get("/catalog", response_model=GutenbergCatalogResponse)
async def list_catalog() -> GutenbergCatalogResponse:
    """Return the curated Project Gutenberg book catalog."""
    return GutenbergCatalogResponse(
        books=[GutenbergCatalogEntry(**b.to_dict()) for b in GUTENBERG_CATALOG]
    )


@ingest_router.post(
    "/ingest/gutenberg",
    response_model=GutenbergIngestResponse,
    status_code=202,
)
async def ingest_gutenberg(
    workspace_id: str,
    body: GutenbergIngestRequest,
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    graph_client: Any = Depends(get_graph_client),  # noqa: B008
    store: JobStore = Depends(get_job_store),  # noqa: B008
) -> GutenbergIngestResponse:
    """Fetch a Project Gutenberg book and enqueue it for extraction.

    Always runs the inline progress-emitting runner so the SSE stream has
    something to observe — Pub/Sub paths are reserved for production
    workloads that ingest GCS-stored documents.
    """
    book_meta = get_book(body.book_id)
    title = body.title or (book_meta.title if book_meta else f"Gutenberg #{body.book_id}")

    try:
        text = await asyncio.to_thread(
            fetch_gutenberg_text,
            body.book_id,
            max_chars=body.max_chars or HARD_MAX_CHARS,
            strip_boilerplate=True,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Gutenberg fetch failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Gutenberg fetch failed: {exc!s}",
        ) from exc

    job = _new_job(
        workspace_id,
        source_title=title,
        source_kind="gutenberg",
    )
    job["gutenberg_book_id"] = body.book_id
    store.upsert_job(job)

    store.append_event(
        JobProgressEvent(
            job_id=job["job_id"],
            step="fetch_gutenberg",
            status="complete",
            message=f"Fetched {len(text):,} chars from Gutenberg #{body.book_id}",
            counts={"chars": len(text)},
        )
    )

    asyncio.create_task(
        run_pipeline_with_progress(
            job_id=job["job_id"],
            text=text,
            tier=body.tier,
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            source_title=title,
            source_kind="gutenberg",
            graph_client=graph_client,
            store=store,
        )
    )

    return GutenbergIngestResponse(
        job_id=job["job_id"],
        workspace_id=workspace_id,
        book_id=body.book_id,
        title=title,
        status=job["status"],
        fetched_chars=len(text),
        estimated_words=book_meta.estimated_words if book_meta else len(text.split()),
        created_at=job["created_at"] or datetime.utcnow().isoformat(),
    )
