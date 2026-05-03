"""
Extraction Stream Router — Server-Sent Events for live ingestion progress.

Public surface:
- ``GET /v1/workspaces/{ws}/extractions/{job_id}/stream`` — SSE stream of
  ``JobProgressEvent`` dicts, one event per line.

The stream replays buffered events on connect, then waits on a per-job
asyncio.Event for new ones. Closes when the job reaches a terminal state
or after 30s of idle silence (configurable via ``?idle=...``).
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse

from dialectica_api.deps import get_current_tenant
from dialectica_api.services.job_store import JobStore, get_job_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/workspaces/{workspace_id}", tags=["extraction"])


@router.get("/extractions/{job_id}/stream")
async def stream_extraction_progress(
    workspace_id: str,
    job_id: str,
    request: Request,
    from_index: int = Query(0, ge=0),
    idle: float = Query(30.0, ge=1.0, le=300.0),
    tenant_id: str = Depends(get_current_tenant),  # noqa: B008
    store: JobStore = Depends(get_job_store),  # noqa: B008
) -> StreamingResponse:
    """Stream live progress events for an ingestion job over SSE."""

    async def event_source() -> AsyncIterator[bytes]:
        # Always emit a "ready" event so the browser EventSource fires
        # ``onopen`` reliably, even if there are no buffered events yet.
        yield _format_sse(
            {"job_id": job_id, "step": "stream", "status": "ready"},
            event="ready",
        )

        try:
            async for event in store.stream_events(
                job_id, from_index=from_index, idle_timeout_s=idle
            ):
                if await request.is_disconnected():
                    return
                yield _format_sse(event.to_dict(), event=event.status)
        except asyncio.CancelledError:  # pragma: no cover - client disconnect
            return

        # Send a final job snapshot so the client can render terminal stats
        # without an extra fetch.
        job = store.get_job(job_id)
        if job is not None:
            yield _format_sse(
                {"job_id": job_id, "job": job},
                event="job",
            )

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def _format_sse(payload: dict, *, event: str = "message") -> bytes:
    """Encode a payload as a single SSE frame."""
    data = json.dumps(payload, default=str)
    return f"event: {event}\ndata: {data}\n\n".encode()
