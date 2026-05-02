"""Tests for the extraction SSE stream and corpus library endpoints."""

from __future__ import annotations

import asyncio
import json
import os

import pytest
from httpx import AsyncClient

from tests.conftest import (
    ADMIN_KEY,
    READONLY_KEY,
    TENANT_ALPHA_KEY,
    TENANT_BETA_KEY,
    TENANT_KEY,
    TENANT_OTHER_KEY,
)


@pytest.fixture(autouse=True)
def _restore_auth_env() -> None:
    """test_benchmark mutates auth env vars; reassert conftest values."""
    os.environ["ADMIN_API_KEY"] = ADMIN_KEY
    os.environ["API_KEYS_JSON"] = json.dumps(
        [
            {"key": ADMIN_KEY, "level": "admin", "tenant_id": "admin"},
            {"key": TENANT_KEY, "level": "standard", "tenant_id": "testuser"},
            {"key": TENANT_ALPHA_KEY, "level": "standard", "tenant_id": "alpha"},
            {"key": TENANT_BETA_KEY, "level": "standard", "tenant_id": "beta"},
            {"key": TENANT_OTHER_KEY, "level": "standard", "tenant_id": "other"},
            {"key": READONLY_KEY, "level": "readonly", "tenant_id": "reader"},
        ]
    )


@pytest.mark.asyncio
async def test_stream_emits_ready_then_events_for_known_job(
    seeded_client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """The SSE stream should at minimum emit a `ready` frame for any reachable job."""
    ws_resp = await seeded_client.post(
        "/v1/workspaces",
        json={"name": "stream", "domain": "political", "scale": "macro"},
        headers=admin_headers,
    )
    ws_id = ws_resp.json()["id"]

    # Start a job (Pub/Sub is unavailable in tests so this triggers inline runner)
    job_resp = await seeded_client.post(
        f"/v1/workspaces/{ws_id}/extract",
        json={"text": "Two factions clashed in the eastern province."},
        headers=admin_headers,
    )
    job_id = job_resp.json()["job_id"]

    # Poll the stream for a short window — we just need to see frames.
    async def consume() -> list[str]:
        chunks: list[str] = []
        url = f"/v1/workspaces/{ws_id}/extractions/{job_id}/stream?idle=2"
        async with seeded_client.stream("GET", url, headers=admin_headers) as resp:
            assert resp.status_code == 200
            async for line in resp.aiter_lines():
                chunks.append(line)
                if len(chunks) > 60:
                    break
        return chunks

    lines = await asyncio.wait_for(consume(), timeout=15.0)
    text = "\n".join(lines)
    assert "event: ready" in text
    # We should also see at least one `event:` frame beyond ready (started/complete/job)
    assert text.count("event:") >= 2


@pytest.mark.asyncio
async def test_stream_returns_404_only_via_idle_timeout(
    seeded_client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Streaming an unknown job should still open and time out cleanly (no 500)."""
    ws_resp = await seeded_client.post(
        "/v1/workspaces",
        json={"name": "stream-missing", "domain": "political", "scale": "macro"},
        headers=admin_headers,
    )
    ws_id = ws_resp.json()["id"]

    url = f"/v1/workspaces/{ws_id}/extractions/no-such-job/stream?idle=1"
    async with seeded_client.stream("GET", url, headers=admin_headers) as resp:
        assert resp.status_code == 200
        # Just drain — should close within ~1s of idle timeout.
        chunks = [chunk async for chunk in resp.aiter_text()]
    assert any("event: ready" in c for c in chunks)


@pytest.mark.asyncio
async def test_corpus_library_lists_completed_documents(
    seeded_client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    ws_resp = await seeded_client.post(
        "/v1/workspaces",
        json={"name": "corpus", "domain": "political", "scale": "macro"},
        headers=admin_headers,
    )
    ws_id = ws_resp.json()["id"]

    # Manually mark a job complete with a SourceDocument so we can verify the
    # endpoint shape independent of pipeline timing.
    from dialectica_api.services.job_store import get_job_store

    store = get_job_store()
    store.upsert_job(
        {
            "job_id": "j-1",
            "workspace_id": ws_id,
            "status": "complete",
            "created_at": "2026-05-02T12:00:00",
            "completed_at": "2026-05-02T12:01:00",
            "nodes_extracted": 10,
            "edges_extracted": 14,
            "error": None,
            "source_title": "Test corpus",
            "source_kind": "gutenberg",
            "gutenberg_book_id": "1513",
            "source_document": {
                "id": "doc-1",
                "title": "Romeo and Juliet (truncated)",
                "content_hash": "abc",
                "word_count": 1234,
                "language": "en",
                "ingested_at": "2026-05-02T12:01:00",
                "extraction_tier": "standard",
                "extraction_model": "gemini-2.5-flash",
                "nodes_extracted": 10,
                "edges_extracted": 14,
                "errors": 0,
            },
        }
    )

    resp = await seeded_client.get(
        f"/v1/workspaces/{ws_id}/corpus/documents",
        headers=admin_headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total_documents"] == 1
    assert data["total_words"] == 1234
    assert data["total_nodes"] == 10
    assert data["total_edges"] == 14
    doc = data["documents"][0]
    assert doc["title"] == "Romeo and Juliet (truncated)"
    assert doc["source_kind"] == "gutenberg"
    assert doc["gutenberg_book_id"] == "1513"


@pytest.mark.asyncio
async def test_corpus_library_skips_incomplete_jobs(
    seeded_client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    ws_resp = await seeded_client.post(
        "/v1/workspaces",
        json={"name": "corpus-empty", "domain": "political", "scale": "macro"},
        headers=admin_headers,
    )
    ws_id = ws_resp.json()["id"]

    from dialectica_api.services.job_store import get_job_store

    get_job_store().upsert_job(
        {
            "job_id": "j-x",
            "workspace_id": ws_id,
            "status": "running",
            "created_at": "2026-05-02T12:00:00",
            "completed_at": None,
            "nodes_extracted": 0,
            "edges_extracted": 0,
            "error": None,
        }
    )

    resp = await seeded_client.get(
        f"/v1/workspaces/{ws_id}/corpus/documents",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["total_documents"] == 0


def test_job_progress_event_shape() -> None:
    """Smoke test the dataclass serialisation."""
    from dialectica_api.services.job_store import JobProgressEvent

    evt = JobProgressEvent(
        job_id="abc",
        step="chunk_document",
        status="complete",
        counts={"chunks": 3},
    )
    payload = evt.to_dict()
    # Should round-trip through JSON.
    assert json.loads(json.dumps(payload, default=str))["counts"]["chunks"] == 3
