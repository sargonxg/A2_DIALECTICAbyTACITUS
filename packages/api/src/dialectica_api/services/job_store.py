"""
In-memory job + progress event store for ingestion jobs.

Shared by:
- ``routers/extraction.py``        — text + document upload jobs
- ``routers/gutenberg.py``         — Project Gutenberg ingest jobs
- ``routers/extraction_stream.py`` — SSE progress streaming endpoint
- ``routers/corpus_library.py``    — list of ingested SourceDocuments per workspace

This is intentionally an in-process store. Production deployments should
replace ``JobStore`` with a Redis-backed implementation (see
``docs/ARCHITECTURE.md`` for the migration path). The interface is
designed to make that swap mechanical.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any


@dataclass
class JobProgressEvent:
    """A single progress event emitted by the extraction pipeline."""

    job_id: str
    step: str  # canonical name, e.g. "chunk_document", "extract_entities"
    status: str  # "started" | "complete" | "failed" | "info"
    message: str = ""
    counts: dict[str, int] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "step": self.step,
            "status": self.status,
            "message": self.message,
            "counts": self.counts,
            "timestamp": self.timestamp,
        }


class JobStore:
    """In-process job + progress event store with async listener support.

    Each job has:
    - a status dict (the same shape ``ExtractionJob`` returns)
    - an ordered list of ``JobProgressEvent``
    - an ``asyncio.Event`` that fires whenever a new event lands, used by
      the SSE endpoint to wake up without polling
    """

    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}
        self._events: dict[str, list[JobProgressEvent]] = {}
        self._signals: dict[str, asyncio.Event] = {}

    # ─── Job state ────────────────────────────────────────────────────────

    def upsert_job(self, job: dict[str, Any]) -> None:
        self._jobs[job["job_id"]] = job

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        return self._jobs.get(job_id)

    def list_jobs(self, workspace_id: str | None = None) -> list[dict[str, Any]]:
        jobs = list(self._jobs.values())
        if workspace_id is not None:
            jobs = [j for j in jobs if j.get("workspace_id") == workspace_id]
        return jobs

    def clear(self) -> None:
        self._jobs.clear()
        self._events.clear()
        for sig in self._signals.values():
            sig.set()
        self._signals.clear()

    # ─── Progress events ──────────────────────────────────────────────────

    def append_event(self, event: JobProgressEvent) -> None:
        self._events.setdefault(event.job_id, []).append(event)
        signal = self._signals.get(event.job_id)
        if signal is not None:
            signal.set()

    def events_for(self, job_id: str) -> list[JobProgressEvent]:
        return list(self._events.get(job_id, []))

    async def stream_events(
        self,
        job_id: str,
        *,
        from_index: int = 0,
        idle_timeout_s: float = 30.0,
    ) -> AsyncIterator[JobProgressEvent]:
        """Yield events for ``job_id`` as they arrive.

        Replays anything already buffered, then waits on the per-job signal.
        Exits when the job reaches a terminal status or after ``idle_timeout_s``
        seconds with no new events.
        """
        signal = self._signals.setdefault(job_id, asyncio.Event())
        cursor = from_index

        while True:
            buffered = self._events.get(job_id, [])
            while cursor < len(buffered):
                yield buffered[cursor]
                cursor += 1

            job = self._jobs.get(job_id)
            if job and job.get("status") in {"complete", "failed"}:
                # One final pass to flush any race-arrived events.
                buffered = self._events.get(job_id, [])
                while cursor < len(buffered):
                    yield buffered[cursor]
                    cursor += 1
                return

            signal.clear()
            try:
                await asyncio.wait_for(signal.wait(), timeout=idle_timeout_s)
            except TimeoutError:
                return


_default_store: JobStore | None = None


def get_job_store() -> JobStore:
    """Return the process-wide ``JobStore`` singleton."""
    global _default_store
    if _default_store is None:
        _default_store = JobStore()
    return _default_store


def reset_job_store_for_tests() -> None:
    """Clear the singleton; tests use this between runs."""
    global _default_store
    if _default_store is not None:
        _default_store.clear()
    _default_store = None
