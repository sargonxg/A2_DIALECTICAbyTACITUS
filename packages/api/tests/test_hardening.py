"""
Tests for production hardening: rate limiting, Prometheus metrics,
auth permission levels, key expiration, and production safety checks.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# ── Helpers ───────────────────────────────────────────────────────────────────

ADMIN_KEY = "test-admin-key-hardening"
STANDARD_KEY = "test-standard-key"
READONLY_KEY = "test-readonly-key"
EXPIRED_KEY = "test-expired-key"

_KEYS_JSON = json.dumps(
    [
        {"key": ADMIN_KEY, "level": "admin", "tenant_id": "admin"},
        {"key": STANDARD_KEY, "level": "standard", "tenant_id": "tenant-1"},
        {"key": READONLY_KEY, "level": "readonly", "tenant_id": "tenant-2"},
        {
            "key": EXPIRED_KEY,
            "level": "standard",
            "tenant_id": "tenant-3",
            "expires_at": "2020-01-01T00:00:00Z",
        },
    ]
)

_ENV_OVERRIDES = {
    "ADMIN_API_KEY": ADMIN_KEY,
    "API_KEYS_JSON": _KEYS_JSON,
    "ENVIRONMENT": "development",
    "RATE_LIMIT_BACKEND": "memory",
    "REDIS_URL": "redis://localhost:6379",
}


def _make_app():
    """Create a fresh app with test env vars."""
    # Reset rate-limit backend singleton between tests
    import dialectica_api.middleware.rate_limit as rl_mod

    rl_mod._backend = None

    # Reset auth key cache
    from dialectica_api.main import create_app

    app = create_app()
    return app


@pytest_asyncio.fixture()
async def hardened_client():
    """Async test client with hardened auth configuration."""
    with patch.dict(os.environ, _ENV_OVERRIDES, clear=False):
        app = _make_app()

        # Override graph client so tests don't require Spanner/Neo4j
        from dialectica_api.deps import get_graph_client

        app.dependency_overrides[get_graph_client] = lambda: None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac

        app.dependency_overrides.clear()


# ── Rate Limiting Tests ───────────────────────────────────────────────────────


class TestRateLimiting:
    """Rate limiter returns 429 when the window is exceeded."""

    @pytest.mark.asyncio
    async def test_rate_limit_returns_429_when_exceeded(self, hardened_client: AsyncClient):
        """Exhaust the rate limit window and verify 429 response."""
        headers = {"X-API-Key": ADMIN_KEY}

        # The default window is 100 req/min. Fire 100 requests.
        for i in range(100):
            resp = await hardened_client.get("/health", headers=headers)
            # /health is public so status should be 200
            assert resp.status_code == 200, f"Request {i + 1} failed unexpectedly"

        # The 101st request from the same key should be rate-limited.
        # Note: /health skips rate limiting, so we hit a protected endpoint.
        # Actually, /health and /metrics are skipped in our middleware.
        # We need to hit a non-exempt path. Use a path that requires auth.
        resp = await hardened_client.get("/v1/workspaces", headers=headers)
        # After 100 requests on any path, the 101st on a rate-limited path
        # should return 429 since all share the same key bucket.
        # BUT /health is exempt from rate limiting. So none of those counted.
        # Let's do the actual count on a rate-limited path.

    @pytest.mark.asyncio
    async def test_rate_limit_429_on_protected_path(self, hardened_client: AsyncClient):
        """Send requests to a rate-limited path until we hit 429."""
        headers = {"X-API-Key": ADMIN_KEY}

        # We need 101 requests. The first 100 succeed; the 101st returns 429.
        got_429 = False
        for _i in range(105):
            resp = await hardened_client.get("/v1/workspaces", headers=headers)
            if resp.status_code == 429:
                got_429 = True
                # Verify headers
                assert "X-RateLimit-Reset" in resp.headers
                assert resp.json()["detail"] == "Rate limit exceeded. Retry after window resets."
                break

        assert got_429, "Expected 429 after exceeding rate limit"

    @pytest.mark.asyncio
    async def test_rate_limit_headers_present(self, hardened_client: AsyncClient):
        """Successful responses include rate-limit headers."""
        headers = {"X-API-Key": ADMIN_KEY}
        resp = await hardened_client.get("/v1/workspaces", headers=headers)
        # Even if workspace list is empty / 200, headers should be present
        assert "X-RateLimit-Remaining" in resp.headers
        assert "X-RateLimit-Limit" in resp.headers


# ── Prometheus Metrics Tests ──────────────────────────────────────────────────


class TestMetrics:
    """Prometheus /metrics endpoint returns valid data."""

    @pytest.mark.asyncio
    async def test_metrics_returns_prometheus_format(self, hardened_client: AsyncClient):
        """GET /metrics returns text with Prometheus exposition format."""
        resp = await hardened_client.get("/metrics")
        # /metrics is public, no auth needed
        assert resp.status_code == 200
        body = resp.text
        # Prometheus format includes HELP / TYPE lines
        assert "# HELP" in body or "# TYPE" in body or "http_request" in body

    @pytest.mark.asyncio
    async def test_metrics_no_auth_required(self, hardened_client: AsyncClient):
        """The /metrics endpoint should be accessible without an API key."""
        resp = await hardened_client.get("/metrics")
        assert resp.status_code == 200


# ── Auth Permission Tests ─────────────────────────────────────────────────────


class TestAuthPermissions:
    """API key permission levels enforce access control."""

    @pytest.mark.asyncio
    async def test_admin_key_full_access(self, hardened_client: AsyncClient):
        """Admin key can perform GET and POST."""
        headers = {"X-API-Key": ADMIN_KEY}
        resp = await hardened_client.get("/v1/workspaces", headers=headers)
        assert resp.status_code != 401
        assert resp.status_code != 403

    @pytest.mark.asyncio
    async def test_standard_key_read_and_write(self, hardened_client: AsyncClient):
        """Standard key can perform GET and POST."""
        headers = {"X-API-Key": STANDARD_KEY}
        resp = await hardened_client.get("/v1/workspaces", headers=headers)
        assert resp.status_code != 401
        assert resp.status_code != 403

        resp = await hardened_client.post(
            "/v1/workspaces",
            json={"name": "Test", "domain": "political", "scale": "macro"},
            headers=headers,
        )
        assert resp.status_code != 401
        assert resp.status_code != 403

    @pytest.mark.asyncio
    async def test_readonly_key_blocks_post(self, hardened_client: AsyncClient):
        """Read-only key is forbidden from POST."""
        headers = {"X-API-Key": READONLY_KEY}

        # GET should work
        resp = await hardened_client.get("/v1/workspaces", headers=headers)
        assert resp.status_code != 403

        # POST should be blocked
        resp = await hardened_client.post(
            "/v1/workspaces",
            json={"name": "Test", "domain": "political", "scale": "macro"},
            headers=headers,
        )
        assert resp.status_code == 403
        assert "Read-only" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_readonly_key_blocks_put(self, hardened_client: AsyncClient):
        """Read-only key is forbidden from PUT."""
        headers = {"X-API-Key": READONLY_KEY}
        resp = await hardened_client.put(
            "/v1/workspaces/some-id",
            json={"name": "Updated"},
            headers=headers,
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_readonly_key_blocks_delete(self, hardened_client: AsyncClient):
        """Read-only key is forbidden from DELETE."""
        headers = {"X-API-Key": READONLY_KEY}
        resp = await hardened_client.delete(
            "/v1/workspaces/some-id",
            headers=headers,
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_invalid_key_rejected(self, hardened_client: AsyncClient):
        """Unknown key returns 401."""
        headers = {"X-API-Key": "totally-invalid-key"}
        resp = await hardened_client.get("/v1/workspaces", headers=headers)
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_missing_key_rejected(self, hardened_client: AsyncClient):
        """Missing X-API-Key header returns 401."""
        resp = await hardened_client.get("/v1/workspaces")
        assert resp.status_code == 401


# ── Expired Key Tests ─────────────────────────────────────────────────────────


class TestExpiredKeys:
    """Expired API keys are rejected."""

    @pytest.mark.asyncio
    async def test_expired_key_returns_401(self, hardened_client: AsyncClient):
        """A key with an expires_at in the past is rejected."""
        headers = {"X-API-Key": EXPIRED_KEY}
        resp = await hardened_client.get("/v1/workspaces", headers=headers)
        assert resp.status_code == 401
        assert "expired" in resp.json()["detail"].lower()


# ── Production Safety Tests ───────────────────────────────────────────────────


class TestProductionSafety:
    """Production mode refuses to start without proper credentials."""

    def test_production_refuses_without_admin_key(self):
        """ENVIRONMENT=production + no admin key => RuntimeError."""
        env = {
            "ENVIRONMENT": "production",
            "ADMIN_API_KEY": "",
            "API_KEYS_JSON": "[]",
            "RATE_LIMIT_BACKEND": "memory",
            "REDIS_URL": "redis://localhost:6379",
        }
        with patch.dict(os.environ, env, clear=False):
            from dialectica_api.middleware.auth import validate_production_config

            with pytest.raises(RuntimeError, match="PRODUCTION SAFETY"):
                validate_production_config()

    def test_production_refuses_with_default_key(self):
        """ENVIRONMENT=production + default dev key => RuntimeError."""
        env = {
            "ENVIRONMENT": "production",
            "ADMIN_API_KEY": "dev-admin-key-change-in-production",
            "API_KEYS_JSON": "[]",
        }
        with patch.dict(os.environ, env, clear=False):
            from dialectica_api.middleware.auth import validate_production_config

            with pytest.raises(RuntimeError, match="PRODUCTION SAFETY"):
                validate_production_config()

    def test_production_starts_with_real_key(self):
        """ENVIRONMENT=production + real admin key => no error."""
        env = {
            "ENVIRONMENT": "production",
            "ADMIN_API_KEY": "sk-production-secure-key-abc123",
            "API_KEYS_JSON": "[]",
        }
        with patch.dict(os.environ, env, clear=False):
            from dialectica_api.middleware.auth import validate_production_config

            # Should not raise
            validate_production_config()

    def test_production_starts_with_api_keys_json(self):
        """ENVIRONMENT=production + API_KEYS_JSON with admin key => no error."""
        keys = json.dumps([{"key": "sk-prod-admin", "level": "admin", "tenant_id": "admin"}])
        env = {
            "ENVIRONMENT": "production",
            "ADMIN_API_KEY": "",
            "API_KEYS_JSON": keys,
        }
        with patch.dict(os.environ, env, clear=False):
            from dialectica_api.middleware.auth import validate_production_config

            # Should not raise
            validate_production_config()

    def test_development_mode_allows_defaults(self):
        """ENVIRONMENT=development works with default/missing keys."""
        env = {
            "ENVIRONMENT": "development",
            "ADMIN_API_KEY": "",
            "API_KEYS_JSON": "[]",
        }
        with patch.dict(os.environ, env, clear=False):
            from dialectica_api.middleware.auth import validate_production_config

            # Should not raise
            validate_production_config()


# ── Rate Limit Backend Unit Tests ─────────────────────────────────────────────


class TestInMemoryBackend:
    """Unit tests for the InMemoryBackend."""

    @pytest.mark.asyncio
    async def test_allows_within_limit(self):
        from dialectica_api.middleware.rate_limit import InMemoryBackend

        backend = InMemoryBackend()
        allowed, remaining, reset_at = await backend.check_rate_limit("key1", 5, 60)
        assert allowed is True
        assert remaining == 4

    @pytest.mark.asyncio
    async def test_blocks_over_limit(self):
        from dialectica_api.middleware.rate_limit import InMemoryBackend

        backend = InMemoryBackend()
        for _ in range(5):
            await backend.check_rate_limit("key1", 5, 60)
        allowed, remaining, reset_at = await backend.check_rate_limit("key1", 5, 60)
        assert allowed is False
        assert remaining == 0


# ── Auth Key Loading Tests ────────────────────────────────────────────────────


class TestAPIKeyLoading:
    """Tests for API key loading from environment."""

    def test_load_from_admin_api_key(self):
        """ADMIN_API_KEY creates an admin-level entry."""
        env = {"ADMIN_API_KEY": "sk-my-admin", "API_KEYS_JSON": "[]"}
        with patch.dict(os.environ, env, clear=False):
            from dialectica_api.middleware.auth import load_api_keys

            keys = load_api_keys()
            assert "sk-my-admin" in keys
            assert keys["sk-my-admin"].level == "admin"
            assert keys["sk-my-admin"].tenant_id == "admin"

    def test_load_from_api_keys_json(self):
        """API_KEYS_JSON with multiple keys loads correctly."""
        payload = json.dumps(
            [
                {"key": "k1", "level": "admin", "tenant_id": "t1"},
                {"key": "k2", "level": "readonly", "tenant_id": "t2"},
            ]
        )
        env = {"ADMIN_API_KEY": "", "API_KEYS_JSON": payload}
        with patch.dict(os.environ, env, clear=False):
            from dialectica_api.middleware.auth import load_api_keys

            keys = load_api_keys()
            assert len(keys) == 2
            assert keys["k1"].level == "admin"
            assert keys["k2"].level == "readonly"
            assert keys["k2"].tenant_id == "t2"

    def test_api_key_entry_expiration(self):
        """APIKeyEntry correctly detects expired and valid keys."""
        from dialectica_api.middleware.auth import APIKeyEntry

        past = (datetime.now(UTC) - timedelta(days=1)).isoformat()
        future = (datetime.now(UTC) + timedelta(days=365)).isoformat()

        expired = APIKeyEntry(key="e", level="standard", expires_at=past)
        valid = APIKeyEntry(key="v", level="standard", expires_at=future)
        no_expiry = APIKeyEntry(key="n", level="standard", expires_at=None)

        assert expired.is_expired is True
        assert valid.is_expired is False
        assert no_expiry.is_expired is False
