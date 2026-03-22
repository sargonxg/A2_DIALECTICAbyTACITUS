"""
Tests for FalkorDBGraphClient — graph-per-tenant isolation, parameterized queries,
temporal filtering, and node CRUD.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_graph.falkordb_client import FalkorDBGraphClient, _graph_key
from dialectica_ontology.primitives import Actor
from dialectica_ontology.relationships import ConflictRelationship, EdgeType

# ═══════════════════════════════════════════════════════════════════════════
#  GRAPH KEY GENERATION
# ═══════════════════════════════════════════════════════════════════════════


class TestGraphKeyGeneration:
    def test_default_key(self):
        key = _graph_key("tenant-123")
        assert key == "tacitus_graph_tenant_123"

    def test_key_sanitizes_spaces(self):
        key = _graph_key("my tenant")
        assert key == "tacitus_graph_my_tenant"

    def test_key_sanitizes_hyphens(self):
        key = _graph_key("a-b-c")
        assert key == "tacitus_graph_a_b_c"

    def test_different_tenants_different_keys(self):
        k1 = _graph_key("tenant-a")
        k2 = _graph_key("tenant-b")
        assert k1 != k2

    def test_key_prefix(self):
        key = _graph_key("x")
        assert key.startswith("tacitus_graph_")


# ═══════════════════════════════════════════════════════════════════════════
#  CLIENT CONSTRUCTION
# ═══════════════════════════════════════════════════════════════════════════


class TestClientConstruction:
    def test_default_params(self):
        client = FalkorDBGraphClient()
        assert client._host == "localhost"
        assert client._port == 6379
        assert client._default_tenant_id == "default"

    def test_custom_params(self):
        client = FalkorDBGraphClient(
            host="redis.example.com",
            port=6380,
            default_tenant_id="acme",
        )
        assert client._host == "redis.example.com"
        assert client._port == 6380
        assert client._default_tenant_id == "acme"

    def test_graph_name_override(self):
        client = FalkorDBGraphClient(graph_name="custom_graph")
        assert client._graph_name_override == "custom_graph"


# ═══════════════════════════════════════════════════════════════════════════
#  PARAMETERIZED QUERY SAFETY
# ═══════════════════════════════════════════════════════════════════════════


class TestQueryParameterization:
    """Ensure all queries use parameterized queries (no string interpolation of user data)."""

    @pytest.fixture
    def mock_client(self):
        client = FalkorDBGraphClient(graph_name="test_graph")
        mock_db = MagicMock()
        mock_graph = MagicMock()
        mock_graph.query.return_value = MagicMock(result_set=[], header=[])
        mock_db.select_graph.return_value = mock_graph
        client._db = mock_db
        return client, mock_graph

    @pytest.mark.asyncio
    async def test_upsert_node_uses_params(self, mock_client):
        client, mock_graph = mock_client
        actor = Actor(name="Test Actor", actor_type="person")
        await client.upsert_node(actor, "ws-1", "tenant-1")

        mock_graph.query.assert_called_once()
        call_args = mock_graph.query.call_args
        query = call_args[0][0]
        call_args[0][1]

        # Query should use $id, $workspace_id, $props — not raw values
        assert "$id" in query
        assert "$workspace_id" in query or "$ws" in query
        assert "$props" in query
        assert "Test Actor" not in query  # No string interpolation

    @pytest.mark.asyncio
    async def test_get_node_uses_params(self, mock_client):
        client, mock_graph = mock_client
        await client.get_node("node-123", "ws-1")

        call_args = mock_graph.query.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "$id" in query
        assert "$ws" in query
        assert "node-123" not in query
        assert params["id"] == "node-123"

    @pytest.mark.asyncio
    async def test_delete_node_soft_uses_params(self, mock_client):
        client, mock_graph = mock_client
        await client.delete_node("node-123", "ws-1", hard=False)

        call_args = mock_graph.query.call_args
        query = call_args[0][0]
        assert "$id" in query
        assert "$now" in query

    @pytest.mark.asyncio
    async def test_delete_node_hard_uses_params(self, mock_client):
        client, mock_graph = mock_client
        await client.delete_node("node-123", "ws-1", hard=True)

        call_args = mock_graph.query.call_args
        query = call_args[0][0]
        assert "DETACH DELETE" in query
        assert "$id" in query

    @pytest.mark.asyncio
    async def test_injection_attempt_is_parameterized(self, mock_client):
        """Verify that malicious node_id doesn't end up in the query string."""
        client, mock_graph = mock_client
        malicious_id = "'; DROP TABLE nodes; --"
        await client.get_node(malicious_id, "ws-1")

        call_args = mock_graph.query.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert malicious_id not in query
        assert params["id"] == malicious_id


# ═══════════════════════════════════════════════════════════════════════════
#  TEMPORAL FILTERING
# ═══════════════════════════════════════════════════════════════════════════


class TestTemporalFiltering:
    @pytest.fixture
    def mock_client(self):
        client = FalkorDBGraphClient(graph_name="test_graph")
        mock_db = MagicMock()
        mock_graph = MagicMock()
        mock_graph.query.return_value = MagicMock(result_set=[], header=[])
        mock_db.select_graph.return_value = mock_graph
        client._db = mock_db
        return client, mock_graph

    @pytest.mark.asyncio
    async def test_timeline_with_date_range(self, mock_client):
        client, mock_graph = mock_client
        start = datetime(2024, 1, 1)
        end = datetime(2024, 6, 1)

        await client.get_timeline("ws-1", start=start, end=end)

        call_args = mock_graph.query.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "$start" in query
        assert "$end" in query
        assert params["start"] == start.isoformat()
        assert params["end"] == end.isoformat()

    @pytest.mark.asyncio
    async def test_timeline_without_date_range(self, mock_client):
        client, mock_graph = mock_client
        await client.get_timeline("ws-1")

        call_args = mock_graph.query.call_args
        query = call_args[0][0]
        call_args[0][1]

        assert "$start" not in query
        assert "$end" not in query

    @pytest.mark.asyncio
    async def test_reference_time_query(self, mock_client):
        client, mock_graph = mock_client
        ref_time = datetime(2024, 3, 15)
        await client.get_events_by_reference_time("ws-1", ref_time, window_days=7)

        call_args = mock_graph.query.call_args
        query = call_args[0][0]
        params = call_args[0][1]

        assert "$start" in query
        assert "$end" in query
        expected_start = (ref_time - timedelta(days=7)).isoformat()
        expected_end = (ref_time + timedelta(days=7)).isoformat()
        assert params["start"] == expected_start
        assert params["end"] == expected_end


# ═══════════════════════════════════════════════════════════════════════════
#  NODE CRUD ROUND-TRIP
# ═══════════════════════════════════════════════════════════════════════════


class TestNodeCRUD:
    @pytest.fixture
    def mock_client(self):
        client = FalkorDBGraphClient(graph_name="test_graph")
        mock_db = MagicMock()
        mock_graph = MagicMock()
        mock_db.select_graph.return_value = mock_graph
        client._db = mock_db
        return client, mock_graph

    @pytest.mark.asyncio
    async def test_upsert_returns_node_id(self, mock_client):
        client, mock_graph = mock_client
        mock_graph.query.return_value = MagicMock(result_set=[["node-1"]])

        actor = Actor(name="Alice", actor_type="person")
        result = await client.upsert_node(actor, "ws-1", "tenant-1")
        assert result == actor.id

    @pytest.mark.asyncio
    async def test_get_node_returns_none_when_missing(self, mock_client):
        client, mock_graph = mock_client
        mock_graph.query.return_value = MagicMock(result_set=[])

        result = await client.get_node("nonexistent", "ws-1")
        assert result is None

    @pytest.mark.asyncio
    async def test_batch_upsert_nodes(self, mock_client):
        client, mock_graph = mock_client
        mock_graph.query.return_value = MagicMock(result_set=[["id"]])

        actors = [
            Actor(name="A1", actor_type="person"),
            Actor(name="A2", actor_type="organization"),
        ]
        ids = await client.batch_upsert_nodes(actors, "ws-1", "tenant-1")
        assert len(ids) == 2
        assert mock_graph.query.call_count == 2

    @pytest.mark.asyncio
    async def test_upsert_edge(self, mock_client):
        client, mock_graph = mock_client
        mock_graph.query.return_value = MagicMock(result_set=[])

        edge = ConflictRelationship(
            type=EdgeType.PARTY_TO,
            source_id="a1",
            target_id="c1",
            source_label="Actor",
            target_label="Conflict",
        )
        result = await client.upsert_edge(edge, "ws-1", "tenant-1")
        assert result == edge.id


# ═══════════════════════════════════════════════════════════════════════════
#  FACTORY INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════


class TestFactory:
    def test_create_falkordb_client(self):
        from dialectica_graph import create_graph_client

        with patch(
            "dialectica_graph.falkordb_client.FalkorDBGraphClient.__init__", return_value=None
        ):
            client = create_graph_client("falkordb", {"host": "redis.local", "port": 6380})
            assert isinstance(client, FalkorDBGraphClient)

    def test_unsupported_backend_raises(self):
        from dialectica_graph import create_graph_client

        with pytest.raises(ValueError, match="Unsupported graph backend"):
            create_graph_client("mongodb")
