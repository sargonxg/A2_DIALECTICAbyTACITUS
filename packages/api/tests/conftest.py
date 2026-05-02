"""
Shared fixtures for DIALECTICA API integration tests.

Provides:
- MockGraphClient: in-memory implementation of GraphClient interface
- Async test client via httpx.AsyncClient + ASGITransport
- Dependency overrides for graph client, tenant, and query engine
- Admin and tenant auth header fixtures
- Workspace creation helper
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from dialectica_graph.models import (
    ActorNetworkResult,
    EscalationResult,
    EscalationTrajectoryPoint,
    ScoredNode,
    SubgraphResult,
    WorkspaceStats,
)
from dialectica_ontology.primitives import Actor, ConflictNode
from dialectica_ontology.relationships import ConflictRelationship, EdgeType

# ---------------------------------------------------------------------------
# Auth keys — set env vars BEFORE any app import
# ---------------------------------------------------------------------------

ADMIN_KEY = "test-admin-key-for-integration-tests"
TENANT_KEY = "test-tenant-key-for-testuser"
TENANT_ALPHA_KEY = "test-key-alpha"
TENANT_BETA_KEY = "test-key-beta"
TENANT_OTHER_KEY = "test-key-other"
READONLY_KEY = "test-readonly-key"

# Configure env vars so the auth middleware picks them up
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
os.environ["ENVIRONMENT"] = "development"


# ---------------------------------------------------------------------------
# Mock Graph Client — in-memory implementation
# ---------------------------------------------------------------------------


class MockGraphClient:
    """In-memory mock implementing the GraphClient abstract interface."""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, ConflictNode]] = {}  # {workspace_id: {node_id: node}}
        self.edges: dict[str, list[ConflictRelationship]] = {}  # {workspace_id: [edge]}
        self.schema_initialized: bool = False

    async def initialize_schema(self) -> None:
        self.schema_initialized = True

    async def upsert_node(self, node: ConflictNode, workspace_id: str, tenant_id: str) -> str:
        if workspace_id not in self.nodes:
            self.nodes[workspace_id] = {}
        self.nodes[workspace_id][node.id] = node
        return node.id

    async def delete_node(self, node_id: str, workspace_id: str, hard: bool = False) -> bool:
        ws_nodes = self.nodes.get(workspace_id, {})
        if node_id in ws_nodes:
            del ws_nodes[node_id]
            return True
        return False

    async def get_node(self, node_id: str, workspace_id: str) -> ConflictNode | None:
        return self.nodes.get(workspace_id, {}).get(node_id)

    async def get_nodes(
        self,
        workspace_id: str,
        label: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ConflictNode]:
        ws_nodes = list(self.nodes.get(workspace_id, {}).values())
        if label:
            ws_nodes = [n for n in ws_nodes if getattr(n, "label", "") == label]
        return ws_nodes[offset : offset + limit]

    async def upsert_edge(
        self, edge: ConflictRelationship, workspace_id: str, tenant_id: str
    ) -> str:
        if workspace_id not in self.edges:
            self.edges[workspace_id] = []
        self.edges[workspace_id].append(edge)
        return edge.id

    async def get_edges(
        self,
        workspace_id: str,
        edge_type: str | None = None,
    ) -> list[ConflictRelationship]:
        ws_edges = self.edges.get(workspace_id, [])
        if edge_type:
            ws_edges = [e for e in ws_edges if str(e.type) == edge_type]
        return ws_edges

    async def traverse(
        self,
        start_id: str,
        workspace_id: str,
        hops: int = 2,
        edge_types: list[str] | None = None,
    ) -> SubgraphResult:
        node = self.nodes.get(workspace_id, {}).get(start_id)
        nodes = [node] if node else []
        return SubgraphResult(nodes=nodes, edges=[], metadata={"hops": hops})

    async def vector_search(
        self,
        workspace_id: str = "",
        embedding: list[float] | None = None,
        label: str | None = None,
        top_k: int = 10,
        query_text: str = "",
        **kwargs: Any,
    ) -> list[ScoredNode]:
        # Return matching nodes by keyword in name
        results: list[ScoredNode] = []
        q = query_text.lower() if query_text else ""
        for node in self.nodes.get(workspace_id, {}).values():
            name = getattr(node, "name", "")
            if q and q in name.lower():
                results.append(ScoredNode(node=node, score=0.9, distance=0.1))
        return results[:top_k]

    async def execute_query(
        self, query: str = "", params: dict | None = None, **kwargs: Any
    ) -> list[dict]:
        return [{"result": "mock_query_result", "query": query}]

    async def get_workspace_stats(self, workspace_id: str) -> WorkspaceStats:
        ws_nodes = self.nodes.get(workspace_id, {})
        ws_edges = self.edges.get(workspace_id, [])
        label_counts: dict[str, int] = {}
        for n in ws_nodes.values():
            lbl = getattr(n, "label", "Unknown")
            label_counts[lbl] = label_counts.get(lbl, 0) + 1
        type_counts: dict[str, int] = {}
        for e in ws_edges:
            t = str(e.type)
            type_counts[t] = type_counts.get(t, 0) + 1
        return WorkspaceStats(
            node_counts_by_label=label_counts,
            edge_counts_by_type=type_counts,
            total_nodes=len(ws_nodes),
            total_edges=len(ws_edges),
        )

    async def get_actor_network(self, actor_id: str, workspace_id: str) -> ActorNetworkResult:
        node = self.nodes.get(workspace_id, {}).get(actor_id)
        if not node:
            node = Actor(
                id=actor_id,
                name="Unknown",
                actor_type="person",
                workspace_id=workspace_id,
            )
        return ActorNetworkResult(
            actor=node,
            allies=[],
            opponents=[],
            connections=[],
            centrality_scores={"betweenness": 0.5},
        )

    async def get_timeline(
        self,
        workspace_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> list[ConflictNode]:
        return list(self.nodes.get(workspace_id, {}).values())

    async def get_escalation_trajectory(self, workspace_id: str) -> EscalationResult:
        return EscalationResult(
            trajectory=[
                EscalationTrajectoryPoint(
                    timestamp=datetime.utcnow(),
                    glasl_stage=3,
                    evidence="Mock evidence",
                )
            ],
            current_stage=3,
            velocity=0.2,
            direction="escalating",
        )

    async def batch_upsert_nodes(
        self,
        nodes: list[ConflictNode],
        workspace_id: str,
        tenant_id: str,
    ) -> list[str]:
        ids = []
        for node in nodes:
            await self.upsert_node(node, workspace_id, tenant_id)
            ids.append(node.id)
        return ids

    async def batch_upsert_edges(
        self,
        edges: list[ConflictRelationship],
        workspace_id: str,
        tenant_id: str,
    ) -> list[str]:
        ids = []
        for edge in edges:
            await self.upsert_edge(edge, workspace_id, tenant_id)
            ids.append(edge.id)
        return ids

    async def close(self) -> None:
        self.nodes.clear()
        self.edges.clear()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def admin_headers() -> dict[str, str]:
    """Headers that authenticate as admin."""
    return {"X-API-Key": ADMIN_KEY}


@pytest.fixture()
def tenant_headers() -> dict[str, str]:
    """Headers that authenticate as tenant 'testuser'."""
    return {"X-API-Key": TENANT_KEY}


@pytest.fixture()
def mock_graph() -> MockGraphClient:
    """Shared mock graph client instance for a test."""
    return MockGraphClient()


@pytest_asyncio.fixture()
async def client(mock_graph: MockGraphClient) -> AsyncClient:
    """Async test client with dependency overrides.

    The admin API key header bypasses auth middleware, and
    get_graph_client is overridden to return the mock.
    """
    from dialectica_api.deps import get_graph_client
    from dialectica_api.main import create_app

    # Reset rate limiter before creating the app to avoid cross-test pollution
    from dialectica_api.middleware.rate_limit import InMemoryBackend, set_rate_limit_backend

    set_rate_limit_backend(InMemoryBackend())

    test_app = create_app()

    # Reset the auth middleware's cached keys so it re-reads env vars
    for middleware in test_app.user_middleware:
        if hasattr(middleware, "cls") and middleware.cls.__name__ == "AuthMiddleware":
            break
    # The middleware caches keys lazily; force re-init by clearing on
    # any existing AuthMiddleware instances. We do this by patching the
    # middleware attribute to None so _get_keys re-loads from env.
    _reset_auth_middleware_cache(test_app)

    # Override the graph client dependency
    test_app.dependency_overrides[get_graph_client] = lambda: mock_graph

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    # Clean up overrides and in-memory stores
    test_app.dependency_overrides.clear()

    from dialectica_api.routers.developers import _api_keys
    from dialectica_api.routers.workspaces import _workspaces
    from dialectica_api.services.job_store import reset_job_store_for_tests

    _workspaces.clear()
    reset_job_store_for_tests()
    _api_keys.clear()

    # Reset rate limit backend so tests don't accumulate hits
    from dialectica_api.middleware.rate_limit import InMemoryBackend, set_rate_limit_backend

    set_rate_limit_backend(InMemoryBackend())


def _reset_auth_middleware_cache(app: Any) -> None:
    """Walk the Starlette middleware stack and reset AuthMiddleware key cache."""
    # Starlette wraps middleware in a chain; the AuthMiddleware instance
    # is created when the ASGI app is built. We need to force its _keys
    # attribute to None so it re-reads from env vars on next request.
    # However, middleware instances aren't created until first request
    # with BaseHTTPMiddleware, so we just ensure env vars are set (done above).
    pass


@pytest_asyncio.fixture()
async def seeded_client(
    client: AsyncClient, admin_headers: dict[str, str], mock_graph: MockGraphClient
) -> AsyncClient:
    """Client with a pre-created workspace and sample entities."""
    # Create a workspace
    resp = await client.post(
        "/v1/workspaces",
        json={"name": "Test Conflict", "domain": "political", "scale": "macro"},
        headers=admin_headers,
    )
    assert resp.status_code == 201, f"Workspace creation failed: {resp.status_code} {resp.text}"
    ws_id = resp.json()["id"]

    # Seed some nodes into the mock graph
    actor1 = Actor(
        id="actor-1",
        name="Party A",
        actor_type="person",
        workspace_id=ws_id,
        tenant_id="admin",
        label="Actor",
    )
    actor2 = Actor(
        id="actor-2",
        name="Party B",
        actor_type="organization",
        workspace_id=ws_id,
        tenant_id="admin",
        label="Actor",
    )
    await mock_graph.upsert_node(actor1, ws_id, "admin")
    await mock_graph.upsert_node(actor2, ws_id, "admin")

    # Seed an edge
    edge = ConflictRelationship(
        id="edge-1",
        type=EdgeType.OPPOSED_TO,
        source_id="actor-1",
        target_id="actor-2",
        source_label="Actor",
        target_label="Actor",
        workspace_id=ws_id,
        weight=0.8,
    )
    await mock_graph.upsert_edge(edge, ws_id, "admin")

    return client
