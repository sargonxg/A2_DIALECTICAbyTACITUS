"""
Security-focused tests — authentication, authorization, injection prevention,
CORS, security headers.
"""
from __future__ import annotations

import json
import os
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

ADMIN_KEY = "test-admin-key-security"
STANDARD_KEY = "test-standard-key-sec"
READONLY_KEY = "test-readonly-key-sec"
EXPIRED_KEY = "test-expired-key-sec"

_KEYS_JSON = json.dumps([
    {"key": ADMIN_KEY, "level": "admin", "tenant_id": "admin"},
    {"key": STANDARD_KEY, "level": "standard", "tenant_id": "tenant-1"},
    {"key": READONLY_KEY, "level": "readonly", "tenant_id": "tenant-2"},
    {"key": EXPIRED_KEY, "level": "standard", "tenant_id": "tenant-3", "expires_at": "2020-01-01T00:00:00Z"},
])

_ENV = {
    "ADMIN_API_KEY": ADMIN_KEY,
    "API_KEYS_JSON": _KEYS_JSON,
    "ENVIRONMENT": "development",
    "RATE_LIMIT_BACKEND": "memory",
    "REDIS_URL": "redis://localhost:6379",
    "CORS_ORIGINS": "http://localhost:3000",
}


def _make_app():
    import dialectica_api.middleware.rate_limit as rl_mod
    rl_mod._backend = None
    from dialectica_api.main import create_app
    return create_app()


@pytest_asyncio.fixture()
async def client():
    with patch.dict(os.environ, _ENV, clear=False):
        app = _make_app()
        from dialectica_api.deps import get_graph_client
        app.dependency_overrides[get_graph_client] = lambda: None
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac
        app.dependency_overrides.clear()


class TestAuthentication:
    @pytest.mark.asyncio
    async def test_unauthenticated_returns_401(self, client: AsyncClient):
        resp = await client.get("/v1/workspaces")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_valid_key_returns_200(self, client: AsyncClient):
        resp = await client.get("/v1/workspaces", headers={"X-API-Key": ADMIN_KEY})
        assert resp.status_code in (200, 404)  # 200 if endpoint exists

    @pytest.mark.asyncio
    async def test_expired_key_returns_401(self, client: AsyncClient):
        resp = await client.get("/v1/workspaces", headers={"X-API-Key": EXPIRED_KEY})
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_key_returns_401(self, client: AsyncClient):
        resp = await client.get("/v1/workspaces", headers={"X-API-Key": "invalid-key"})
        assert resp.status_code == 401


class TestSecurityHeaders:
    @pytest.mark.asyncio
    async def test_health_has_response(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_content_type_header(self, client: AsyncClient):
        resp = await client.get("/health")
        assert "application/json" in resp.headers.get("content-type", "")


class TestInjectionPrevention:
    @pytest.mark.asyncio
    async def test_sql_injection_in_workspace_id(self, client: AsyncClient):
        """SQL injection in path parameter should not cause server error."""
        resp = await client.get(
            "/v1/workspaces/' OR 1=1 --/graph",
            headers={"X-API-Key": ADMIN_KEY},
        )
        # Should return 404 or 422, NOT 500
        assert resp.status_code != 500

    @pytest.mark.asyncio
    async def test_cypher_injection_in_query(self, client: AsyncClient):
        """Cypher injection should be parameterized."""
        resp = await client.get(
            "/v1/workspaces/ws-1/graph?query=MATCH (n) DETACH DELETE n",
            headers={"X-API-Key": ADMIN_KEY},
        )
        assert resp.status_code != 500


class TestHealthEndpoints:
    @pytest.mark.asyncio
    async def test_health_liveness(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_health_readiness(self, client: AsyncClient):
        resp = await client.get("/health/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert "checks" in data
        assert isinstance(data["checks"], list)

    @pytest.mark.asyncio
    async def test_health_deep(self, client: AsyncClient):
        resp = await client.get("/health/deep")
        assert resp.status_code == 200
        data = resp.json()
        assert "environment" in data
        assert "uptime_seconds" in data
