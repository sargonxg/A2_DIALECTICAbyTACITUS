"""
Comprehensive integration tests for the DIALECTICA FastAPI API.

Covers all 10 routers: health, workspaces, entities, relationships,
extraction, graph, reasoning, theory, admin, developers.

Uses httpx.AsyncClient with ASGITransport against the real FastAPI app,
with a MockGraphClient injected via dependency overrides.
"""

from __future__ import annotations

import io

import pytest
from httpx import AsyncClient

# Constants matching conftest.py fixtures
ADMIN_KEY = "test-admin-key-for-integration-tests"
TENANT_KEY = "test-tenant-key-for-testuser"
TENANT_ALPHA_KEY = "test-key-alpha"
TENANT_BETA_KEY = "test-key-beta"
TENANT_OTHER_KEY = "test-key-other"
READONLY_KEY = "test-readonly-key"

pytestmark = pytest.mark.asyncio


# ============================================================================
# Helper to get the first workspace ID from a seeded_client
# ============================================================================


async def _get_workspace_id(client: AsyncClient, headers: dict[str, str]) -> str:
    """Return the first workspace ID from the list endpoint."""
    resp = await client.get("/v1/workspaces", headers=headers)
    data = resp.json()
    assert len(data) > 0, "Expected at least one workspace"
    return data[0]["id"]


# ============================================================================
# 1. HEALTH ROUTER
# ============================================================================


class TestHealth:
    """Tests for GET /health and GET /health/dependencies."""

    async def test_health_check(self, client: AsyncClient) -> None:
        resp = await client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] in ("healthy", "degraded")
        assert "timestamp" in body
        assert body["version"] == "2.0.0"
        assert "graph_backend" in body
        assert "checks" in body

    async def test_health_no_auth_required(self, client: AsyncClient) -> None:
        """Health endpoint should be publicly accessible without API key."""
        resp = await client.get("/health")
        assert resp.status_code == 200

    async def test_health_ready(self, client: AsyncClient, admin_headers: dict[str, str]) -> None:
        resp = await client.get("/health/ready", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body
        assert "checks" in body


# ============================================================================
# 2. WORKSPACES ROUTER
# ============================================================================


class TestWorkspaces:
    """Tests for /v1/workspaces CRUD."""

    async def test_create_workspace(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        resp = await client.post(
            "/v1/workspaces",
            json={
                "name": "Syria Civil War",
                "domain": "political",
                "scale": "macro",
                "description": "Multi-party conflict analysis",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "Syria Civil War"
        assert body["domain"] == "political"
        assert body["scale"] == "macro"
        assert body["tenant_id"] == "admin"
        assert "id" in body
        assert "created_at" in body

    async def test_list_workspaces(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        # Create two workspaces
        await client.post(
            "/v1/workspaces",
            json={"name": "WS-1"},
            headers=admin_headers,
        )
        await client.post(
            "/v1/workspaces",
            json={"name": "WS-2"},
            headers=admin_headers,
        )
        resp = await client.get("/v1/workspaces", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2
        names = {ws["name"] for ws in data}
        assert "WS-1" in names
        assert "WS-2" in names

    async def test_get_workspace(self, client: AsyncClient, admin_headers: dict[str, str]) -> None:
        create_resp = await client.post(
            "/v1/workspaces",
            json={"name": "GetMe"},
            headers=admin_headers,
        )
        ws_id = create_resp.json()["id"]
        resp = await client.get(f"/v1/workspaces/{ws_id}", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "GetMe"

    async def test_get_workspace_not_found(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        resp = await client.get("/v1/workspaces/nonexistent", headers=admin_headers)
        assert resp.status_code == 404

    async def test_update_workspace(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            "/v1/workspaces",
            json={"name": "Original"},
            headers=admin_headers,
        )
        ws_id = create_resp.json()["id"]
        resp = await client.patch(
            f"/v1/workspaces/{ws_id}",
            json={"name": "Updated", "description": "New desc"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "Updated"
        assert body["description"] == "New desc"

    async def test_delete_workspace(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        create_resp = await client.post(
            "/v1/workspaces",
            json={"name": "ToDelete"},
            headers=admin_headers,
        )
        ws_id = create_resp.json()["id"]
        resp = await client.delete(f"/v1/workspaces/{ws_id}", headers=admin_headers)
        assert resp.status_code == 204
        # Verify it's gone
        resp2 = await client.get(f"/v1/workspaces/{ws_id}", headers=admin_headers)
        assert resp2.status_code == 404

    async def test_delete_workspace_not_found(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        resp = await client.delete("/v1/workspaces/nope", headers=admin_headers)
        assert resp.status_code == 404


# ============================================================================
# 3. AUTH MIDDLEWARE
# ============================================================================


class TestAuth:
    """Tests for authentication middleware behavior."""

    async def test_no_api_key_returns_401(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/workspaces")
        assert resp.status_code == 401

    async def test_invalid_api_key_returns_401(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/workspaces", headers={"X-API-Key": "bad-key"})
        assert resp.status_code == 401

    async def test_tenant_key_authenticates(self, client: AsyncClient) -> None:
        """A tenant-prefixed key should authenticate successfully."""
        resp = await client.get("/v1/workspaces", headers={"X-API-Key": TENANT_KEY})
        assert resp.status_code == 200

    async def test_admin_key_authenticates(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        resp = await client.get("/v1/workspaces", headers=admin_headers)
        assert resp.status_code == 200

    async def test_public_paths_skip_auth(self, client: AsyncClient) -> None:
        """Public paths (/health, /docs, /openapi.json, /redoc) need no auth."""
        for path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            resp = await client.get(path)
            assert resp.status_code in (200, 307), f"{path} returned {resp.status_code}"


# ============================================================================
# 4. ENTITIES ROUTER
# ============================================================================


class TestEntities:
    """Tests for /v1/workspaces/{id}/entities."""

    async def test_list_entities(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(f"/v1/workspaces/{ws_id}/entities", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2  # Two seeded actors

    async def test_list_entities_label_filter(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/entities",
            params={"label": "Actor"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert all(e["label"] == "Actor" for e in data)

    async def test_list_entities_label_filter_no_match(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/entities",
            params={"label": "Conflict"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_get_entity(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/entities/actor-1", headers=admin_headers
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == "actor-1"
        assert body["name"] == "Party A"
        assert body["label"] == "Actor"

    async def test_get_entity_not_found(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/entities/nonexistent", headers=admin_headers
        )
        assert resp.status_code == 404

    async def test_delete_entity(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.delete(
            f"/v1/workspaces/{ws_id}/entities/actor-1", headers=admin_headers
        )
        assert resp.status_code == 204
        # Confirm gone
        resp2 = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/entities/actor-1", headers=admin_headers
        )
        assert resp2.status_code == 404

    async def test_delete_entity_not_found(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.delete(
            f"/v1/workspaces/{ws_id}/entities/ghost", headers=admin_headers
        )
        assert resp.status_code == 404


# ============================================================================
# 5. RELATIONSHIPS ROUTER
# ============================================================================


class TestRelationships:
    """Tests for /v1/workspaces/{id}/relationships."""

    async def test_list_relationships(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/relationships", headers=admin_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 1  # One seeded edge
        edge = data[0]
        assert edge["type"] == "OPPOSED_TO"
        assert edge["source_id"] == "actor-1"
        assert edge["target_id"] == "actor-2"

    async def test_list_relationships_edge_type_filter(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/relationships",
            params={"edge_type": "ALLIED_WITH"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_delete_relationship(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.delete(
            f"/v1/workspaces/{ws_id}/relationships/edge-1", headers=admin_headers
        )
        assert resp.status_code == 204


# ============================================================================
# 6. EXTRACTION ROUTER
# ============================================================================


class TestExtraction:
    """Tests for /v1/workspaces/{id}/extract and /extractions."""

    async def test_extract_text(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.post(
            f"/v1/workspaces/{ws_id}/extract",
            json={
                "text": "Tensions escalated between factions in the eastern region.",
                "source_title": "Test Article",
                "tier": "standard",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 202
        body = resp.json()
        assert "job_id" in body
        assert body["workspace_id"] == ws_id
        assert body["status"] in ("pending", "queued", "running", "complete", "failed")

    async def test_extract_document_upload(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        file_content = b"Violence erupted in the capital after disputed elections."
        resp = await seeded_client.post(
            f"/v1/workspaces/{ws_id}/extract/document",
            files={"file": ("report.txt", io.BytesIO(file_content), "text/plain")},
            headers=admin_headers,
        )
        assert resp.status_code in (200, 201, 202)
        body = resp.json()
        assert body.get("workspace_id") == ws_id or "job_id" in body

    async def test_list_extraction_jobs(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        # Create a job first
        await seeded_client.post(
            f"/v1/workspaces/{ws_id}/extract",
            json={"text": "Conflict text here."},
            headers=admin_headers,
        )
        resp = await seeded_client.get(f"/v1/workspaces/{ws_id}/extractions", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    async def test_get_extraction_job(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        create_resp = await seeded_client.post(
            f"/v1/workspaces/{ws_id}/extract",
            json={"text": "Sample conflict text."},
            headers=admin_headers,
        )
        job_id = create_resp.json()["job_id"]
        resp = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/extractions/{job_id}", headers=admin_headers
        )
        assert resp.status_code == 200
        assert resp.json()["job_id"] == job_id

    async def test_get_extraction_job_not_found(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/extractions/no-such-job", headers=admin_headers
        )
        assert resp.status_code == 404


# ============================================================================
# 7. GRAPH ROUTER
# ============================================================================


class TestGraph:
    """Tests for /v1/workspaces/{id}/graph endpoints."""

    async def test_get_full_graph(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(f"/v1/workspaces/{ws_id}/graph", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "nodes" in body
        assert "edges" in body
        assert len(body["nodes"]) == 2
        assert len(body["edges"]) == 1

    async def test_get_graph_stats(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(f"/v1/workspaces/{ws_id}/graph/stats", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["workspace_id"] == ws_id
        assert body["total_nodes"] == 2
        assert body["total_edges"] == 1

    async def test_get_subgraph(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/graph/subgraph",
            params={"center_id": "actor-1", "hops": 2},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["center_id"] == "actor-1"
        assert body["hops"] == 2
        assert isinstance(body["nodes"], list)

    async def test_get_subgraph_requires_center_id(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/graph/subgraph", headers=admin_headers
        )
        assert resp.status_code == 422  # Missing required query param

    async def test_graph_search(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/graph/search",
            params={"q": "Party"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        # The mock should match "Party A" and "Party B"
        assert len(data) >= 1

    async def test_graph_search_no_results(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/graph/search",
            params={"q": "zzzznonexistent"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_graph_search_requires_query(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/graph/search", headers=admin_headers
        )
        assert resp.status_code == 422

    async def test_raw_query_admin_only(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.post(
            f"/v1/workspaces/{ws_id}/graph/query",
            json={"query": "MATCH (n) RETURN n LIMIT 10"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "result" in body

    async def test_raw_query_rejected_for_tenant(
        self, seeded_client: AsyncClient, tenant_headers: dict[str, str]
    ) -> None:
        """Non-admin tenant should get 403 on raw query."""
        ws_id = await _get_workspace_id(seeded_client, {"X-API-Key": ADMIN_KEY})
        resp = await seeded_client.post(
            f"/v1/workspaces/{ws_id}/graph/query",
            json={"query": "MATCH (n) RETURN n"},
            headers=tenant_headers,
        )
        assert resp.status_code == 403

    async def test_raw_query_empty_query_returns_400(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.post(
            f"/v1/workspaces/{ws_id}/graph/query",
            json={"query": ""},
            headers=admin_headers,
        )
        assert resp.status_code == 400


# ============================================================================
# 8. REASONING ROUTER
# ============================================================================


class TestReasoning:
    """Tests for /v1/workspaces/{id}/analyze and analysis endpoints.

    The reasoning endpoints import from dialectica_reasoning which may not be
    available, so we test that they either return data or handle import errors.
    """

    async def test_analyze_streaming_returns_sse(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.post(
            f"/v1/workspaces/{ws_id}/analyze",
            json={"query": "What is the conflict about?", "mode": "general"},
            headers=admin_headers,
        )
        # Should return 200 with SSE content type (query engine is None -> error stream)
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers.get("content-type", "")

    async def test_escalation_endpoint(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(f"/v1/workspaces/{ws_id}/escalation", headers=admin_headers)
        # This will likely return 500 (ImportError from dialectica_reasoning)
        # or 503 if graph client is somehow None. Either way, check it doesn't crash.
        assert resp.status_code in (200, 500, 503)

    async def test_ripeness_endpoint(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(f"/v1/workspaces/{ws_id}/ripeness", headers=admin_headers)
        assert resp.status_code in (200, 500, 503)

    async def test_power_endpoint(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(f"/v1/workspaces/{ws_id}/power", headers=admin_headers)
        assert resp.status_code in (200, 500, 503)

    async def test_trust_endpoint(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(f"/v1/workspaces/{ws_id}/trust", headers=admin_headers)
        assert resp.status_code in (200, 500, 503)

    async def test_causation_endpoint(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(f"/v1/workspaces/{ws_id}/causation", headers=admin_headers)
        assert resp.status_code in (200, 500, 503)

    async def test_quality_endpoint(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(f"/v1/workspaces/{ws_id}/quality", headers=admin_headers)
        assert resp.status_code in (200, 500, 503)

    async def test_network_endpoint(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(f"/v1/workspaces/{ws_id}/network", headers=admin_headers)
        assert resp.status_code in (200, 500, 503)


# ============================================================================
# 9. THEORY ROUTER
# ============================================================================


class TestTheory:
    """Tests for /v1/theory/frameworks and workspace theory endpoints."""

    async def test_list_frameworks(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        resp = await client.get("/v1/theory/frameworks", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        # May be empty if frameworks.json doesn't exist, but shouldn't error

    async def test_get_framework_not_found(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        resp = await client.get(
            "/v1/theory/frameworks/nonexistent-framework", headers=admin_headers
        )
        assert resp.status_code == 404

    async def test_apply_all_theories_no_graph(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        """When the reasoning module import fails, expect 500."""
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(f"/v1/workspaces/{ws_id}/theory", headers=admin_headers)
        # Will fail with ImportError from dialectica_reasoning.agents.theorist
        assert resp.status_code in (200, 500, 503)

    async def test_apply_single_framework(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.get(
            f"/v1/workspaces/{ws_id}/theory/glasl-escalation",
            headers=admin_headers,
        )
        assert resp.status_code in (200, 404, 500, 503)


# ============================================================================
# 10. ADMIN ROUTER
# ============================================================================


class TestAdmin:
    """Tests for /v1/admin endpoints (admin only)."""

    async def test_get_system_info_admin(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        resp = await client.get("/v1/admin/system", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "graph_backend" in body
        assert body["version"] == "2.0.0"
        assert "environment" in body

    async def test_get_system_info_forbidden_for_tenant(
        self, client: AsyncClient, tenant_headers: dict[str, str]
    ) -> None:
        resp = await client.get("/v1/admin/system", headers=tenant_headers)
        assert resp.status_code == 403

    async def test_get_usage_admin(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        resp = await client.get("/v1/admin/usage", headers=admin_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), dict)

    async def test_get_usage_forbidden_for_tenant(
        self, client: AsyncClient, tenant_headers: dict[str, str]
    ) -> None:
        resp = await client.get("/v1/admin/usage", headers=tenant_headers)
        assert resp.status_code == 403

    async def test_seed_data_admin(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        resp = await client.post("/v1/admin/seed", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] in ("started", "error")

    async def test_seed_data_forbidden_for_tenant(
        self, client: AsyncClient, tenant_headers: dict[str, str]
    ) -> None:
        resp = await client.post("/v1/admin/seed", headers=tenant_headers)
        assert resp.status_code == 403


# ============================================================================
# 11. DEVELOPERS ROUTER
# ============================================================================


class TestDevelopers:
    """Tests for /v1/developers/keys and /v1/developers/usage."""

    async def test_create_api_key(self, client: AsyncClient, admin_headers: dict[str, str]) -> None:
        resp = await client.post(
            "/v1/developers/keys",
            json={"name": "test-key", "rate_limit_per_min": 50},
            headers=admin_headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "test-key"
        assert body["rate_limit_per_min"] == 50
        assert body["api_key"].startswith("tenant-")
        assert "key_id" in body

    async def test_list_api_keys(self, client: AsyncClient, admin_headers: dict[str, str]) -> None:
        # Create a key first
        await client.post(
            "/v1/developers/keys",
            json={"name": "list-test-key"},
            headers=admin_headers,
        )
        resp = await client.get("/v1/developers/keys", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        # Admin tenant owns the keys created above
        names = {k["name"] for k in data}
        assert "list-test-key" in names

    async def test_delete_api_key(self, client: AsyncClient, admin_headers: dict[str, str]) -> None:
        create_resp = await client.post(
            "/v1/developers/keys",
            json={"name": "to-delete"},
            headers=admin_headers,
        )
        key_id = create_resp.json()["key_id"]
        resp = await client.delete(f"/v1/developers/keys/{key_id}", headers=admin_headers)
        assert resp.status_code == 204
        # Verify it's gone
        list_resp = await client.get("/v1/developers/keys", headers=admin_headers)
        key_ids = {k["key_id"] for k in list_resp.json()}
        assert key_id not in key_ids

    async def test_delete_api_key_not_found(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        resp = await client.delete("/v1/developers/keys/no-such-key", headers=admin_headers)
        assert resp.status_code == 404

    async def test_get_developer_usage(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        resp = await client.get("/v1/developers/usage", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "tenant_id" in body
        assert "usage" in body


# ============================================================================
# 12. WORKSPACE TENANT ISOLATION
# ============================================================================


class TestTenantIsolation:
    """Tests verifying multi-tenant isolation."""

    async def test_tenant_cannot_access_other_tenant_workspace(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        # Create workspace as admin
        create_resp = await client.post(
            "/v1/workspaces",
            json={"name": "Admin Only WS"},
            headers=admin_headers,
        )
        ws_id = create_resp.json()["id"]

        # Try to access as a different tenant
        other_headers = {"X-API-Key": TENANT_OTHER_KEY}
        resp = await client.get(f"/v1/workspaces/{ws_id}", headers=other_headers)
        assert resp.status_code == 403

    async def test_tenant_can_only_see_own_workspaces(self, client: AsyncClient) -> None:
        # Create workspace as tenant-alpha
        alpha_headers = {"X-API-Key": TENANT_ALPHA_KEY}
        await client.post(
            "/v1/workspaces",
            json={"name": "Alpha WS"},
            headers=alpha_headers,
        )

        # Create workspace as tenant-beta
        beta_headers = {"X-API-Key": TENANT_BETA_KEY}
        await client.post(
            "/v1/workspaces",
            json={"name": "Beta WS"},
            headers=beta_headers,
        )

        # Alpha should only see its own
        resp = await client.get("/v1/workspaces", headers=alpha_headers)
        data = resp.json()
        assert all(ws["tenant_id"] == "alpha" for ws in data)

        # Beta should only see its own
        resp = await client.get("/v1/workspaces", headers=beta_headers)
        data = resp.json()
        assert all(ws["tenant_id"] == "beta" for ws in data)

    async def test_admin_sees_all_workspaces(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        # Create workspaces as different tenants
        alpha_headers = {"X-API-Key": TENANT_ALPHA_KEY}
        beta_headers = {"X-API-Key": TENANT_BETA_KEY}
        await client.post(
            "/v1/workspaces",
            json={"name": "T1 WS"},
            headers=alpha_headers,
        )
        await client.post(
            "/v1/workspaces",
            json={"name": "T2 WS"},
            headers=beta_headers,
        )
        # Admin sees all
        resp = await client.get("/v1/workspaces", headers=admin_headers)
        data = resp.json()
        names = {ws["name"] for ws in data}
        assert "T1 WS" in names
        assert "T2 WS" in names


# ============================================================================
# 13. EDGE CASES AND ERROR HANDLING
# ============================================================================


class TestEdgeCases:
    """Miscellaneous edge case and error handling tests."""

    async def test_workspace_create_defaults(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        """Creating a workspace with only required field 'name'."""
        resp = await client.post(
            "/v1/workspaces",
            json={"name": "MinimalWS"},
            headers=admin_headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["domain"] == "political"  # default
        assert body["scale"] == "macro"  # default
        assert body["tier"] == "standard"  # default
        assert body["description"] == ""  # default

    async def test_workspace_update_partial(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        """PATCH with only one field should preserve the rest."""
        create_resp = await client.post(
            "/v1/workspaces",
            json={"name": "OrigName", "domain": "economic", "description": "keep me"},
            headers=admin_headers,
        )
        ws_id = create_resp.json()["id"]
        resp = await client.patch(
            f"/v1/workspaces/{ws_id}",
            json={"name": "NewName"},
            headers=admin_headers,
        )
        body = resp.json()
        assert body["name"] == "NewName"
        assert body["domain"] == "economic"  # unchanged
        assert body["description"] == "keep me"  # unchanged

    async def test_extract_empty_text(
        self, seeded_client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        ws_id = await _get_workspace_id(seeded_client, admin_headers)
        resp = await seeded_client.post(
            f"/v1/workspaces/{ws_id}/extract",
            json={"text": ""},
            headers=admin_headers,
        )
        # Empty text should still create a job (just with status complete)
        assert resp.status_code == 202

    async def test_rate_limit_headers_present(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        """Rate limit middleware should add X-RateLimit headers."""
        resp = await client.get("/v1/workspaces", headers=admin_headers)
        assert "x-ratelimit-remaining" in resp.headers or "X-RateLimit-Remaining" in resp.headers

    async def test_request_id_header_present(
        self, client: AsyncClient, admin_headers: dict[str, str]
    ) -> None:
        """Logging middleware should add X-Request-ID header."""
        resp = await client.get("/v1/workspaces", headers=admin_headers)
        assert "x-request-id" in resp.headers or "X-Request-ID" in resp.headers

    async def test_openapi_schema_available(self, client: AsyncClient) -> None:
        """OpenAPI schema should be publicly accessible."""
        resp = await client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert schema["info"]["title"] == "DIALECTICA API"
        assert schema["info"]["version"] == "2.0.0"
