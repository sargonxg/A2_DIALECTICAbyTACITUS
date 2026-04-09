"""
Tests for Neo4j UNWIND-based batch upsert operations.

Verifies:
- batch_upsert_nodes groups by label and issues UNWIND queries
- batch_upsert_edges groups by type and issues UNWIND queries
- Embeddings are handled in a separate pass
- Empty batches return empty lists without issuing queries
"""

from __future__ import annotations

import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_ontology.primitives import Actor, Conflict
from dialectica_ontology.relationships import ConflictRelationship, EdgeType

# ── Helpers ───────────────────────────────────────────────────────────────


def _make_actor(
    name: str,
    node_id: str | None = None,
    embedding: list[float] | None = None,
) -> Actor:
    return Actor(
        id=node_id or f"actor-{name.lower().replace(' ', '-')}",
        name=name,
        actor_type="person",
        workspace_id="ws-test",
        tenant_id="t-test",
        embedding=embedding,
    )


def _make_conflict(name: str, node_id: str | None = None) -> Conflict:
    return Conflict(
        id=node_id or f"conflict-{name.lower().replace(' ', '-')}",
        name=name,
        scale="micro",
        domain="political",
        status="active",
        workspace_id="ws-test",
        tenant_id="t-test",
    )


def _make_edge(
    source: str,
    target: str,
    edge_type: EdgeType = EdgeType.PARTY_TO,
    edge_id: str | None = None,
) -> ConflictRelationship:
    return ConflictRelationship(
        id=edge_id or f"edge-{source}-{target}",
        type=edge_type,
        source_id=source,
        target_id=target,
        source_label="Actor",
        target_label="Conflict",
        workspace_id="ws-test",
        tenant_id="t-test",
    )


def _mock_neo4j_client() -> MagicMock:
    """Create a Neo4jGraphClient with mocked driver and session."""
    mock_session = AsyncMock()
    mock_session.run = AsyncMock()

    # Patch AsyncGraphDatabase.driver so we don't need real Neo4j
    with patch("dialectica_graph.neo4j_client.AsyncGraphDatabase") as mock_db:
        mock_driver = AsyncMock()
        mock_db.driver.return_value = mock_driver

        from dialectica_graph.neo4j_client import Neo4jGraphClient

        client = Neo4jGraphClient(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="test",
        )

    # Replace _session to return our mock
    client._session = MagicMock(return_value=mock_session)
    # Make the mock session work as async context manager
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    return client, mock_session


# ═══════════════════════════════════════════════════════════════════════════
#  batch_upsert_nodes
# ═══════════════════════════════════════════════════════════════════════════


class TestBatchUpsertNodes:
    """UNWIND-based batch node upsert."""

    @pytest.mark.asyncio
    async def test_empty_list_returns_empty(self) -> None:
        client, session = _mock_neo4j_client()
        result = await client.batch_upsert_nodes([], "ws-1", "t-1")
        assert result == []
        session.run.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_single_label_single_unwind(self) -> None:
        client, session = _mock_neo4j_client()
        actors = [_make_actor("Alice"), _make_actor("Bob")]

        ids = await client.batch_upsert_nodes(actors, "ws-1", "t-1")

        assert len(ids) == 2
        # One UNWIND call for the "Actor" label group
        calls = session.run.await_args_list
        assert len(calls) == 1  # no embeddings, so just one call
        cypher = calls[0].args[0]
        assert "UNWIND" in cypher
        assert "Actor" in cypher

    @pytest.mark.asyncio
    async def test_multiple_labels_grouped(self) -> None:
        client, session = _mock_neo4j_client()
        nodes = [_make_actor("Alice"), _make_conflict("Border Dispute")]

        ids = await client.batch_upsert_nodes(nodes, "ws-1", "t-1")

        assert len(ids) == 2
        # Two UNWIND calls (one per label), no embeddings
        calls = session.run.await_args_list
        assert len(calls) == 2

    @pytest.mark.asyncio
    async def test_embeddings_separate_pass(self) -> None:
        client, session = _mock_neo4j_client()
        actors = [
            _make_actor("Alice", embedding=[0.1] * 128),
            _make_actor("Bob"),  # no embedding
        ]

        ids = await client.batch_upsert_nodes(actors, "ws-1", "t-1")

        assert len(ids) == 2
        calls = session.run.await_args_list
        # One UNWIND for actors + one for embedding pass
        assert len(calls) == 2
        emb_cypher = calls[1].args[0]
        assert "embedding" in emb_cypher

    @pytest.mark.asyncio
    async def test_returns_all_ids(self) -> None:
        client, session = _mock_neo4j_client()
        actors = [_make_actor("A", node_id="id-a"), _make_actor("B", node_id="id-b")]

        ids = await client.batch_upsert_nodes(actors, "ws-1", "t-1")
        assert ids == ["id-a", "id-b"]


# ═══════════════════════════════════════════════════════════════════════════
#  batch_upsert_edges
# ═══════════════════════════════════════════════════════════════════════════


class TestBatchUpsertEdges:
    """UNWIND-based batch edge upsert."""

    @pytest.mark.asyncio
    async def test_empty_list_returns_empty(self) -> None:
        client, session = _mock_neo4j_client()
        result = await client.batch_upsert_edges([], "ws-1", "t-1")
        assert result == []
        session.run.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_single_type_single_unwind(self) -> None:
        client, session = _mock_neo4j_client()
        edges = [
            _make_edge("a1", "c1", EdgeType.PARTY_TO, edge_id="e1"),
            _make_edge("a2", "c1", EdgeType.PARTY_TO, edge_id="e2"),
        ]

        ids = await client.batch_upsert_edges(edges, "ws-1", "t-1")

        assert len(ids) == 2
        calls = session.run.await_args_list
        assert len(calls) == 1
        cypher = calls[0].args[0]
        assert "UNWIND" in cypher
        assert "PARTY_TO" in cypher

    @pytest.mark.asyncio
    async def test_multiple_types_grouped(self) -> None:
        client, session = _mock_neo4j_client()
        edges = [
            _make_edge("a1", "c1", EdgeType.PARTY_TO, edge_id="e1"),
            _make_edge("a1", "a2", EdgeType.ALLIED_WITH, edge_id="e2"),
        ]

        ids = await client.batch_upsert_edges(edges, "ws-1", "t-1")

        assert len(ids) == 2
        calls = session.run.await_args_list
        assert len(calls) == 2

    @pytest.mark.asyncio
    async def test_returns_all_ids(self) -> None:
        client, session = _mock_neo4j_client()
        edges = [
            _make_edge("a1", "c1", edge_id="e-alpha"),
            _make_edge("a2", "c1", edge_id="e-beta"),
        ]

        ids = await client.batch_upsert_edges(edges, "ws-1", "t-1")
        assert ids == ["e-alpha", "e-beta"]

    @pytest.mark.asyncio
    async def test_workspace_id_passed_as_param(self) -> None:
        client, session = _mock_neo4j_client()
        edges = [_make_edge("a1", "c1", edge_id="e1")]

        await client.batch_upsert_edges(edges, "ws-42", "t-1")

        call_params = session.run.await_args_list[0].args[1]
        assert call_params["ws"] == "ws-42"
