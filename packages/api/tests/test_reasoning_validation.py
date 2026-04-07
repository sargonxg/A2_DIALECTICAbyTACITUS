"""
Integration tests for the reasoning validation and trace-listing endpoints.

POST /v1/workspaces/{ws}/reasoning/{trace_id}/validate
GET  /v1/workspaces/{ws}/reasoning/traces
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from dialectica_ontology.primitives import InferredFact, ReasoningTrace

# Auth constants (must match conftest.py)
ADMIN_KEY = "test-admin-key-for-integration-tests"
TENANT_KEY = "test-tenant-key-for-testuser"

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_workspace(client: AsyncClient, headers: dict) -> str:
    resp = await client.post(
        "/v1/workspaces",
        json={"name": "Validation Test WS", "domain": "political", "scale": "macro"},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ---------------------------------------------------------------------------
# GET /v1/workspaces/{ws}/reasoning/traces
# ---------------------------------------------------------------------------


class TestListReasoningTraces:
    async def test_empty_traces(
        self,
        client: AsyncClient,
        admin_headers: dict,
    ) -> None:
        ws_id = await _create_workspace(client, admin_headers)
        resp = await client.get(
            f"/v1/workspaces/{ws_id}/reasoning/traces",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["workspace_id"] == ws_id
        assert body["traces"] == []
        assert body["total"] == 0

    async def test_traces_with_seeded_nodes(
        self,
        client: AsyncClient,
        admin_headers: dict,
        mock_graph: object,
    ) -> None:
        ws_id = await _create_workspace(client, admin_headers)

        # Seed two ReasoningTrace nodes directly into the mock graph
        trace1 = ReasoningTrace(
            id="rt-1",
            workspace_id=ws_id,
            tenant_id="admin",
            rules_fired=["glasl_stage_derivation"],
            conclusion="Stage 5",
        )
        trace2 = ReasoningTrace(
            id="rt-2",
            workspace_id=ws_id,
            tenant_id="admin",
            rules_fired=["ripeness_detection"],
            conclusion="Ripe for negotiation",
        )
        await mock_graph.upsert_node(trace1, ws_id, "admin")
        await mock_graph.upsert_node(trace2, ws_id, "admin")

        resp = await client.get(
            f"/v1/workspaces/{ws_id}/reasoning/traces",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["workspace_id"] == ws_id
        assert body["total"] == 2
        ids = {t["id"] for t in body["traces"]}
        assert "rt-1" in ids
        assert "rt-2" in ids

    async def test_traces_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/workspaces/ws-fake/reasoning/traces")
        assert resp.status_code == 401

    async def test_traces_pagination(
        self,
        client: AsyncClient,
        admin_headers: dict,
        mock_graph: object,
    ) -> None:
        ws_id = await _create_workspace(client, admin_headers)
        for i in range(5):
            t = ReasoningTrace(
                id=f"rt-page-{i}",
                workspace_id=ws_id,
                tenant_id="admin",
            )
            await mock_graph.upsert_node(t, ws_id, "admin")

        resp = await client.get(
            f"/v1/workspaces/{ws_id}/reasoning/traces?limit=2&offset=0",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["limit"] == 2
        assert body["offset"] == 0
        assert len(body["traces"]) <= 2


# ---------------------------------------------------------------------------
# POST /v1/workspaces/{ws}/reasoning/{trace_id}/validate
# ---------------------------------------------------------------------------


class TestValidateReasoningTrace:
    async def test_validate_confirmed(
        self,
        client: AsyncClient,
        admin_headers: dict,
        mock_graph: object,
    ) -> None:
        ws_id = await _create_workspace(client, admin_headers)
        # Add validate_reasoning_trace method to mock_graph for this test
        mock_graph._traces: dict = {}

        async def _validate(
            trace_id: str,
            workspace_id: str,
            verdict: str,
            validated_by: str,
            notes: str = "",
            modified_value=None,
        ) -> bool:
            mock_graph._traces[trace_id] = {
                "verdict": verdict,
                "validated_by": validated_by,
                "notes": notes,
            }
            return True

        mock_graph.validate_reasoning_trace = _validate

        resp = await client.post(
            f"/v1/workspaces/{ws_id}/reasoning/trace-001/validate",
            json={"verdict": "confirmed", "notes": "Looks correct"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["verdict"] == "confirmed"
        assert body["trace_id"] == "trace-001"
        assert body["workspace_id"] == ws_id
        assert "validated_at" in body

    async def test_validate_rejected(
        self,
        client: AsyncClient,
        admin_headers: dict,
        mock_graph: object,
    ) -> None:
        ws_id = await _create_workspace(client, admin_headers)

        async def _validate(trace_id, workspace_id, verdict, validated_by, **kw) -> bool:
            return True

        mock_graph.validate_reasoning_trace = _validate

        resp = await client.post(
            f"/v1/workspaces/{ws_id}/reasoning/trace-002/validate",
            json={"verdict": "rejected", "notes": "Incorrect reasoning"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["verdict"] == "rejected"

    async def test_validate_modified_with_value(
        self,
        client: AsyncClient,
        admin_headers: dict,
        mock_graph: object,
    ) -> None:
        ws_id = await _create_workspace(client, admin_headers)

        async def _validate(trace_id, workspace_id, verdict, validated_by, **kw) -> bool:
            return True

        mock_graph.validate_reasoning_trace = _validate

        resp = await client.post(
            f"/v1/workspaces/{ws_id}/reasoning/trace-003/validate",
            json={"verdict": "modified", "notes": "Stage should be 4", "modified_value": "4"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["verdict"] == "modified"

    async def test_validate_invalid_verdict(
        self,
        client: AsyncClient,
        admin_headers: dict,
        mock_graph: object,
    ) -> None:
        ws_id = await _create_workspace(client, admin_headers)

        async def _validate(*a, **kw) -> bool:
            return True

        mock_graph.validate_reasoning_trace = _validate

        resp = await client.post(
            f"/v1/workspaces/{ws_id}/reasoning/trace-004/validate",
            json={"verdict": "maybe"},  # invalid
            headers=admin_headers,
        )
        assert resp.status_code == 422

    async def test_validate_trace_not_found(
        self,
        client: AsyncClient,
        admin_headers: dict,
        mock_graph: object,
    ) -> None:
        ws_id = await _create_workspace(client, admin_headers)

        async def _validate(*a, **kw) -> bool:
            return False  # simulate not found

        mock_graph.validate_reasoning_trace = _validate

        resp = await client.post(
            f"/v1/workspaces/{ws_id}/reasoning/nonexistent-trace/validate",
            json={"verdict": "confirmed"},
            headers=admin_headers,
        )
        assert resp.status_code == 404

    async def test_validate_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/v1/workspaces/ws-fake/reasoning/trace-x/validate",
            json={"verdict": "confirmed"},
        )
        assert resp.status_code == 401

    async def test_validate_no_graph_client(self, client: AsyncClient) -> None:
        """When graph client unavailable (dependency returns None), expect 503."""
        from dialectica_api.deps import get_graph_client
        from dialectica_api.main import create_app
        from dialectica_api.middleware.rate_limit import InMemoryBackend, set_rate_limit_backend

        set_rate_limit_backend(InMemoryBackend())
        app = create_app()
        app.dependency_overrides[get_graph_client] = lambda: None

        from httpx import ASGITransport, AsyncClient as AC

        async with AC(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
            resp = await ac.post(
                "/v1/workspaces/ws-fake/reasoning/trace-y/validate",
                json={"verdict": "confirmed"},
                headers={"X-API-Key": ADMIN_KEY},
            )
        assert resp.status_code in (401, 503)
        app.dependency_overrides.clear()

    async def test_validate_no_method_on_client(
        self,
        client: AsyncClient,
        admin_headers: dict,
        mock_graph: object,
    ) -> None:
        """501 when graph client doesn't support validation."""
        # Ensure validate_reasoning_trace is NOT present
        if hasattr(mock_graph, "validate_reasoning_trace"):
            del mock_graph.validate_reasoning_trace

        ws_id = await _create_workspace(client, admin_headers)
        resp = await client.post(
            f"/v1/workspaces/{ws_id}/reasoning/trace-z/validate",
            json={"verdict": "confirmed"},
            headers=admin_headers,
        )
        assert resp.status_code == 501
