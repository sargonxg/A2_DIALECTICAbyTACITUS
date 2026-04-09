"""
Tests for the TACITUS integration API endpoints.

Covers:
- GET /v1/integration/graph/{workspace_id} returns nodes + edges
- GET /v1/integration/context/{workspace_id} returns context text
- POST /v1/integration/query returns analysis result
- All endpoints require admin auth (403 without admin key, 401 without any key)
"""

from __future__ import annotations

from typing import Any

import pytest
from httpx import AsyncClient

# Constants matching conftest.py
ADMIN_KEY = "test-admin-key-for-integration-tests"
TENANT_KEY = "test-tenant-key-for-testuser"

pytestmark = pytest.mark.asyncio


# ============================================================================
# Helper: seed a workspace with graph data
# ============================================================================


async def _seed_workspace(
    client: AsyncClient, admin_headers: dict[str, str], mock_graph: Any
) -> str:
    """Create a workspace and seed nodes + edges into mock graph."""
    from dialectica_ontology.primitives import Actor
    from dialectica_ontology.relationships import ConflictRelationship, EdgeType

    resp = await client.post(
        "/v1/workspaces",
        json={"name": "Integration Test Conflict", "domain": "political", "scale": "macro"},
        headers=admin_headers,
    )
    assert resp.status_code == 201, f"Workspace creation failed: {resp.text}"
    ws_id = resp.json()["id"]

    # Seed actors
    actor1 = Actor(
        id="actor-int-1",
        name="Country Alpha",
        actor_type="state",
        workspace_id=ws_id,
        tenant_id="admin",
        label="Actor",
    )
    actor2 = Actor(
        id="actor-int-2",
        name="Country Beta",
        actor_type="state",
        workspace_id=ws_id,
        tenant_id="admin",
        label="Actor",
    )
    await mock_graph.upsert_node(actor1, ws_id, "admin")
    await mock_graph.upsert_node(actor2, ws_id, "admin")

    # Seed an issue-like node. ConflictNode base class lacks a name field,
    # so we use Actor (which has name) with label="Issue" for filtering.
    issue = Actor(
        id="issue-int-1",
        name="Border Dispute",
        actor_type="organization",
        workspace_id=ws_id,
        tenant_id="admin",
        label="Issue",
    )
    await mock_graph.upsert_node(issue, ws_id, "admin")

    # Seed an edge
    edge = ConflictRelationship(
        id="edge-int-1",
        type=EdgeType.OPPOSED_TO,
        source_id="actor-int-1",
        target_id="actor-int-2",
        source_label="Actor",
        target_label="Actor",
        workspace_id=ws_id,
        weight=0.9,
    )
    await mock_graph.upsert_edge(edge, ws_id, "admin")

    return ws_id


# ============================================================================
# GET /v1/integration/graph/{workspace_id}
# ============================================================================


class TestGraphSnapshot:
    async def test_returns_nodes_and_edges(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
        mock_graph: Any,
    ) -> None:
        ws_id = await _seed_workspace(client, admin_headers, mock_graph)

        resp = await client.get(
            f"/v1/integration/graph/{ws_id}",
            headers=admin_headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()

        assert data["workspace_id"] == ws_id
        assert data["node_count"] == 3
        assert data["edge_count"] == 1
        assert len(data["nodes"]) == 3
        assert len(data["edges"]) == 1

        # Verify node structure
        node_names = {n["name"] for n in data["nodes"]}
        assert "Country Alpha" in node_names
        assert "Country Beta" in node_names

        # Verify edge structure
        edge = data["edges"][0]
        assert edge["source_id"] == "actor-int-1"
        assert edge["target_id"] == "actor-int-2"

        # Escalation stage should be present (from mock)
        assert data["escalation_stage"] == 3

    async def test_empty_workspace(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        # Create workspace but don't seed data
        resp = await client.post(
            "/v1/workspaces",
            json={"name": "Empty WS", "domain": "political"},
            headers=admin_headers,
        )
        ws_id = resp.json()["id"]

        resp = await client.get(
            f"/v1/integration/graph/{ws_id}",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["node_count"] == 0
        assert data["edge_count"] == 0

    async def test_requires_admin_auth(self, client: AsyncClient) -> None:
        """Non-admin tenant key should get 403."""
        resp = await client.get(
            "/v1/integration/graph/some-ws",
            headers={"X-API-Key": TENANT_KEY},
        )
        assert resp.status_code == 403

    async def test_no_auth_returns_401(self, client: AsyncClient) -> None:
        """No API key should get 401."""
        resp = await client.get("/v1/integration/graph/some-ws")
        assert resp.status_code == 401


# ============================================================================
# GET /v1/integration/context/{workspace_id}
# ============================================================================


class TestConflictContext:
    async def test_returns_context_text(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
        mock_graph: Any,
    ) -> None:
        ws_id = await _seed_workspace(client, admin_headers, mock_graph)

        resp = await client.get(
            f"/v1/integration/context/{ws_id}",
            headers=admin_headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()

        assert data["workspace_id"] == ws_id
        assert len(data["context_text"]) > 0
        assert "Country Alpha" in data["context_text"]

        # Key actors
        assert "Country Alpha" in data["key_actors"]
        assert "Country Beta" in data["key_actors"]
        assert len(data["key_actors"]) == 2

        # Key issues (conflict node has label "Conflict")
        assert "Border Dispute" in data["key_issues"]

        # Escalation summary should contain stage info
        assert "Stage 3" in data["escalation_summary"]

    async def test_requires_admin_auth(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/v1/integration/context/some-ws",
            headers={"X-API-Key": TENANT_KEY},
        )
        assert resp.status_code == 403

    async def test_no_auth_returns_401(self, client: AsyncClient) -> None:
        resp = await client.get("/v1/integration/context/some-ws")
        assert resp.status_code == 401


# ============================================================================
# POST /v1/integration/query
# ============================================================================


class TestQueryConflict:
    async def test_returns_analysis_when_engine_available(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
        mock_graph: Any,
    ) -> None:
        """When query engine is available, returns structured analysis."""
        ws_id = await _seed_workspace(client, admin_headers, mock_graph)

        resp = await client.post(
            "/v1/integration/query",
            json={
                "workspace_id": ws_id,
                "query": "What is the current state of the conflict?",
                "mode": "general",
            },
            headers=admin_headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()

        # The real query engine returns structured analysis
        assert "answer" in data
        assert len(data["answer"]) > 0
        assert "confidence" in data
        assert isinstance(data["confidence"], float)
        assert "citations" in data
        assert "reasoning_trace" in data
        assert isinstance(data["reasoning_trace"], list)
        assert "patterns_detected" in data

    async def test_returns_503_when_graph_unavailable(
        self,
        admin_headers: dict[str, str],
    ) -> None:
        """When graph client is None, returns 503."""
        import json as json_mod
        import os

        from httpx import ASGITransport
        from httpx import AsyncClient as TestAsyncClient

        os.environ["ADMIN_API_KEY"] = ADMIN_KEY
        os.environ["API_KEYS_JSON"] = json_mod.dumps(
            [
                {"key": ADMIN_KEY, "level": "admin", "tenant_id": "admin"},
                {"key": TENANT_KEY, "level": "standard", "tenant_id": "testuser"},
            ]
        )

        from dialectica_api.deps import get_graph_client
        from dialectica_api.main import create_app
        from dialectica_api.middleware.rate_limit import InMemoryBackend, set_rate_limit_backend

        set_rate_limit_backend(InMemoryBackend())
        test_app = create_app()
        # Override graph client to None so query engine also becomes None
        test_app.dependency_overrides[get_graph_client] = lambda: None

        transport = ASGITransport(app=test_app)
        async with TestAsyncClient(transport=transport, base_url="http://testserver") as ac:
            resp = await ac.post(
                "/v1/integration/query",
                json={
                    "workspace_id": "test-ws",
                    "query": "What is happening?",
                },
                headers=admin_headers,
            )
            assert resp.status_code == 503
        test_app.dependency_overrides.clear()

    async def test_requires_admin_auth(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/v1/integration/query",
            json={"workspace_id": "ws-1", "query": "test"},
            headers={"X-API-Key": TENANT_KEY},
        )
        assert resp.status_code == 403

    async def test_no_auth_returns_401(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/v1/integration/query",
            json={"workspace_id": "ws-1", "query": "test"},
        )
        assert resp.status_code == 401

    async def test_empty_query_rejected(
        self,
        client: AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        """Empty query string should be rejected by validation."""
        resp = await client.post(
            "/v1/integration/query",
            json={"workspace_id": "ws-1", "query": ""},
            headers=admin_headers,
        )
        assert resp.status_code == 422
