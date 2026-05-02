"""Tests for the Gutenberg picker + ingest endpoints."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from httpx import AsyncClient

# test_benchmark.py mutates ADMIN_API_KEY/API_KEYS_JSON without restoring them,
# which leaks into subsequent tests run in the same pytest session. Re-assert
# the conftest values before each test in this module so our tests are
# independent of run order. See conftest.py for the canonical values.
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
async def test_gutenberg_catalog_is_public(client: AsyncClient) -> None:
    """Catalog must be reachable without an API key (demo surface)."""
    resp = await client.get("/v1/gutenberg/catalog")
    assert resp.status_code == 200
    data = resp.json()
    assert "books" in data
    assert len(data["books"]) >= 8
    # Ensure required fields
    book = data["books"][0]
    for field in (
        "book_id",
        "title",
        "author",
        "domain",
        "subdomain",
        "summary",
        "estimated_words",
        "recommended_tier",
    ):
        assert field in book


@pytest.mark.asyncio
async def test_gutenberg_catalog_contains_known_books(client: AsyncClient) -> None:
    """Curated catalog must include the known benchmark books."""
    resp = await client.get("/v1/gutenberg/catalog")
    ids = {b["book_id"] for b in resp.json()["books"]}
    assert "1513" in ids  # Romeo & Juliet
    assert "2600" in ids  # War & Peace


@pytest.mark.asyncio
async def test_ingest_gutenberg_calls_fetcher_and_returns_job(
    seeded_client: AsyncClient,
    admin_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A successful Gutenberg fetch should kick off a job."""
    captured: dict[str, Any] = {}

    def fake_fetch(book_id: str, **kwargs: Any) -> str:
        captured["book_id"] = book_id
        captured["kwargs"] = kwargs
        return "Two households, both alike in dignity, in fair Verona where we lay our scene."

    # Patch in the router module's import site
    import dialectica_api.routers.gutenberg as gb_module

    monkeypatch.setattr(gb_module, "fetch_gutenberg_text", fake_fetch)

    # Create a workspace
    ws_resp = await seeded_client.post(
        "/v1/workspaces",
        json={"name": "GBT", "domain": "political", "scale": "macro"},
        headers=admin_headers,
    )
    ws_id = ws_resp.json()["id"]

    resp = await seeded_client.post(
        f"/v1/workspaces/{ws_id}/ingest/gutenberg",
        json={"book_id": "1513", "tier": "standard", "max_chars": 5_000},
        headers=admin_headers,
    )
    assert resp.status_code == 202, resp.text
    body = resp.json()
    assert body["book_id"] == "1513"
    assert body["fetched_chars"] > 0
    assert body["status"] in {"queued", "running", "complete"}
    assert captured["book_id"] == "1513"


@pytest.mark.asyncio
async def test_ingest_gutenberg_propagates_fetch_failure(
    seeded_client: AsyncClient,
    admin_headers: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If Gutenberg is unreachable, return 502 instead of a half-created job."""
    import dialectica_api.routers.gutenberg as gb_module

    def boom(book_id: str, **kwargs: Any) -> str:
        raise RuntimeError("Could not download Project Gutenberg book 99999: all mirrors down")

    monkeypatch.setattr(gb_module, "fetch_gutenberg_text", boom)

    ws_resp = await seeded_client.post(
        "/v1/workspaces",
        json={"name": "GB-fail", "domain": "political", "scale": "macro"},
        headers=admin_headers,
    )
    ws_id = ws_resp.json()["id"]

    resp = await seeded_client.post(
        f"/v1/workspaces/{ws_id}/ingest/gutenberg",
        json={"book_id": "99999", "tier": "lite"},
        headers=admin_headers,
    )
    assert resp.status_code == 502
    assert "all mirrors down" in resp.json()["detail"]


def test_strip_gutenberg_boilerplate_removes_framing() -> None:
    from dialectica_extraction.sources.gutenberg import strip_gutenberg_boilerplate

    raw = (
        "header text\n"
        "*** START OF THE PROJECT GUTENBERG EBOOK FOO ***\n"
        "real content here\n"
        "*** END OF THE PROJECT GUTENBERG EBOOK FOO ***\n"
        "trailing license\n"
    )
    cleaned = strip_gutenberg_boilerplate(raw)
    assert cleaned == "real content here"


def test_strip_gutenberg_boilerplate_passthrough() -> None:
    from dialectica_extraction.sources.gutenberg import strip_gutenberg_boilerplate

    raw = "no framing markers here\nsecond line"
    assert strip_gutenberg_boilerplate(raw) == raw.strip()
