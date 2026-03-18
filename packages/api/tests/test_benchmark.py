"""
Tests for the DIALECTICA benchmark endpoint.

Covers:
- POST /v1/admin/benchmark/run returns 200 with valid scores
- Non-admin requests get 403
- Invalid corpus_id returns 422
- GET /history and GET /{benchmark_id} endpoints
- Benchmark runner comparison logic
"""
from __future__ import annotations

import json
import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ADMIN_KEY = "dev-admin-key-change-in-production"
TENANT_KEY = "tenant-testuser-secret123"


@pytest.fixture()
def admin_headers() -> dict[str, str]:
    return {"X-API-Key": ADMIN_KEY}


@pytest.fixture()
def tenant_headers() -> dict[str, str]:
    return {"X-API-Key": TENANT_KEY}


@pytest_asyncio.fixture()
async def client() -> AsyncClient:
    # Configure auth keys via environment so middleware recognises both keys
    os.environ["ADMIN_API_KEY"] = ADMIN_KEY
    os.environ["API_KEYS_JSON"] = json.dumps([
        {"key": ADMIN_KEY, "level": "admin", "tenant_id": "admin"},
        {"key": TENANT_KEY, "level": "standard", "tenant_id": "testuser"},
    ])

    from dialectica_api.main import create_app
    from dialectica_api.deps import get_graph_client

    test_app = create_app()
    test_app.dependency_overrides[get_graph_client] = lambda: None

    # Reset the auth middleware's cached keys so it picks up our env vars
    for middleware in getattr(test_app, "user_middleware", []):
        if hasattr(middleware, "cls"):
            pass  # Starlette middleware stack
    # The AuthMiddleware lazily caches keys; force reload by clearing _keys
    # We walk the middleware stack to find it
    app_ref = test_app
    while hasattr(app_ref, "app"):
        if hasattr(app_ref, "_keys"):
            app_ref._keys = None
        app_ref = app_ref.app

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    test_app.dependency_overrides.clear()

    # Clear in-memory benchmark history between tests
    from dialectica_api.routers.benchmark import _benchmark_history
    _benchmark_history.clear()


# ---------------------------------------------------------------------------
# POST /v1/admin/benchmark/run
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_benchmark_returns_200_with_valid_scores(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """POST benchmark/run with default (jcpoa) corpus returns 200 with metrics."""
    resp = await client.post(
        "/v1/admin/benchmark/run",
        json={"corpus_id": "jcpoa", "tier": "standard"},
        headers=admin_headers,
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()

    # Top-level fields
    assert "benchmark_id" in data
    assert data["corpus_id"] == "jcpoa"
    assert data["tier"] == "standard"
    assert data["model"] == "gemini-2.0-flash"
    assert "completed_at" in data

    # Results structure
    results = data["results"]
    assert "overall" in results
    overall = results["overall"]
    assert 0.0 <= overall["precision"] <= 1.0
    assert 0.0 <= overall["recall"] <= 1.0
    assert 0.0 <= overall["f1"] <= 1.0
    assert overall["true_positives"] > 0  # Stub should produce matches

    # By node type
    assert "by_node_type" in results
    assert "Actor" in results["by_node_type"]

    # By edge type (standard tier includes edges)
    assert "by_edge_type" in results
    assert len(results["by_edge_type"]) > 0

    # Evaluation metrics
    assert results["evaluation_points"] > 0
    assert results["extraction_time_ms"] >= 0
    assert 0.0 <= results["hallucination_rate"] <= 1.0


@pytest.mark.asyncio
async def test_run_benchmark_essential_tier(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Essential tier should not include edge metrics."""
    resp = await client.post(
        "/v1/admin/benchmark/run",
        json={"corpus_id": "jcpoa", "tier": "essential"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    # Essential tier: edge metrics should be empty (no edge comparison)
    assert data["results"]["by_edge_type"] == {}


@pytest.mark.asyncio
async def test_run_benchmark_with_graph_augmented(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Graph-augmented evaluation should be included when requested."""
    resp = await client.post(
        "/v1/admin/benchmark/run",
        json={
            "corpus_id": "jcpoa",
            "tier": "standard",
            "include_graph_augmented": True,
        },
        headers=admin_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["results"]["graph_augmented"] is not None
    ga = data["results"]["graph_augmented"]
    assert 0.0 <= ga["f1"] <= 1.0


# ---------------------------------------------------------------------------
# Auth: non-admin gets 403
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_benchmark_non_admin_gets_403(
    client: AsyncClient, tenant_headers: dict[str, str]
) -> None:
    """Non-admin tenant should receive 403 Forbidden."""
    resp = await client.post(
        "/v1/admin/benchmark/run",
        json={"corpus_id": "jcpoa"},
        headers=tenant_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_history_non_admin_gets_403(
    client: AsyncClient, tenant_headers: dict[str, str]
) -> None:
    resp = await client.get(
        "/v1/admin/benchmark/history",
        headers=tenant_headers,
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Invalid corpus_id returns 422
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invalid_corpus_id_returns_422(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Invalid corpus_id should return 422 validation error."""
    resp = await client.post(
        "/v1/admin/benchmark/run",
        json={"corpus_id": "nonexistent_corpus"},
        headers=admin_headers,
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /v1/admin/benchmark/history
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_history_returns_past_runs(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """After running a benchmark, history should contain the result."""
    # Run a benchmark first
    run_resp = await client.post(
        "/v1/admin/benchmark/run",
        json={"corpus_id": "jcpoa"},
        headers=admin_headers,
    )
    assert run_resp.status_code == 200
    benchmark_id = run_resp.json()["benchmark_id"]

    # Check history
    hist_resp = await client.get(
        "/v1/admin/benchmark/history",
        headers=admin_headers,
    )
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    assert len(history) >= 1
    ids = [item["benchmark_id"] for item in history]
    assert benchmark_id in ids


# ---------------------------------------------------------------------------
# GET /v1/admin/benchmark/{benchmark_id}
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_benchmark_by_id(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    """Fetch a specific benchmark run by ID."""
    run_resp = await client.post(
        "/v1/admin/benchmark/run",
        json={"corpus_id": "jcpoa"},
        headers=admin_headers,
    )
    assert run_resp.status_code == 200
    benchmark_id = run_resp.json()["benchmark_id"]

    detail_resp = await client.get(
        f"/v1/admin/benchmark/{benchmark_id}",
        headers=admin_headers,
    )
    assert detail_resp.status_code == 200
    assert detail_resp.json()["benchmark_id"] == benchmark_id


@pytest.mark.asyncio
async def test_get_benchmark_not_found(
    client: AsyncClient, admin_headers: dict[str, str]
) -> None:
    resp = await client.get(
        "/v1/admin/benchmark/nonexistent_id",
        headers=admin_headers,
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# BenchmarkRunner unit tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_runner_compare_nodes() -> None:
    """Node comparison should match by label + fuzzy name."""
    from dialectica_api.benchmark_runner import BenchmarkRunner

    runner = BenchmarkRunner()
    gold = [
        {"label": "Actor", "name": "United States of America"},
        {"label": "Actor", "name": "Islamic Republic of Iran"},
        {"label": "Conflict", "name": "Iran Nuclear Dispute"},
    ]
    extracted = [
        {"label": "Actor", "name": "United States"},
        {"label": "Actor", "name": "Iran"},
        {"label": "Conflict", "name": "Iran Nuclear Program Dispute"},
    ]
    metrics = runner.compare_nodes(gold, extracted)

    # Actor: "United States" vs "United States of America" — may or may not match
    # depending on threshold; "Iran" vs "Islamic Republic of Iran" is likely below 0.8
    assert "Actor" in metrics
    assert "Conflict" in metrics

    # Conflict names are similar enough
    assert metrics["Conflict"].true_positives >= 1


@pytest.mark.asyncio
async def test_runner_compare_edges() -> None:
    """Edge comparison should match by type + endpoint fuzzy match."""
    from dialectica_api.benchmark_runner import BenchmarkRunner

    runner = BenchmarkRunner()
    gold = [
        {"source": "gold_actor_iran", "target": "gold_conflict_jcpoa", "type": "PARTY_TO"},
        {"source": "gold_actor_usa", "target": "gold_conflict_jcpoa", "type": "PARTY_TO"},
    ]
    extracted = [
        {"source": "ext_iran", "target": "ext_jcpoa", "type": "PARTY_TO"},
        {"source": "ext_usa", "target": "ext_jcpoa", "type": "PARTY_TO"},
    ]
    metrics = runner.compare_edges(gold, extracted)
    assert "PARTY_TO" in metrics
    assert metrics["PARTY_TO"].true_positives >= 1


@pytest.mark.asyncio
async def test_runner_full_benchmark() -> None:
    """Full run_benchmark should return a BenchmarkResult with scores."""
    from dialectica_api.benchmark_runner import BenchmarkRunner

    runner = BenchmarkRunner()
    result = await runner.run_benchmark(corpus_id="jcpoa", tier="standard")

    assert result.benchmark_id.startswith("bench_")
    assert result.corpus_id == "jcpoa"
    assert result.results.overall.f1 > 0.0
    assert result.results.extraction_time_ms >= 0
    assert result.completed_at.endswith("Z")
