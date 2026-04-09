"""
Tests for write_to_graph_async — the async graph persistence step of the
extraction pipeline.

Verifies:
- Nodes and edges are persisted via graph_client.batch_upsert_*
- None graph_client is handled gracefully (data retained, no crash)
- Exceptions from batch operations are caught and recorded in state errors
"""

from __future__ import annotations

import os
import sys
from unittest.mock import AsyncMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_extraction.pipeline import (
    ExtractionState,
    write_to_graph,
    write_to_graph_async,
)


def _make_state(
    num_nodes: int = 3,
    num_edges: int = 2,
) -> ExtractionState:
    """Build a minimal ExtractionState with stub node/edge objects."""
    nodes = [f"node_{i}" for i in range(num_nodes)]
    edges = [f"edge_{i}" for i in range(num_edges)]
    return ExtractionState(
        text="test",
        tier="essential",
        workspace_id="ws-1",
        tenant_id="t-1",
        _nodes=nodes,  # type: ignore[typeddict-item]
        _edges=edges,  # type: ignore[typeddict-item]
        errors=[],
        processing_time={},
    )


# ═══════════════════════════════════════════════════════════════════════════
#  write_to_graph (sync stub) — existing behaviour preserved
# ═══════════════════════════════════════════════════════════════════════════


class TestWriteToGraphSync:
    """The synchronous write_to_graph should populate ingestion_stats only."""

    def test_populates_ingestion_stats(self) -> None:
        state = _make_state(num_nodes=4, num_edges=2)
        result = write_to_graph(state)
        assert result["ingestion_stats"]["nodes_written"] == 4
        assert result["ingestion_stats"]["edges_written"] == 2

    def test_records_processing_time(self) -> None:
        state = _make_state()
        result = write_to_graph(state)
        assert "write_to_graph" in result["processing_time"]
        assert result["processing_time"]["write_to_graph"] >= 0


# ═══════════════════════════════════════════════════════════════════════════
#  write_to_graph_async — with graph client
# ═══════════════════════════════════════════════════════════════════════════


class TestWriteToGraphAsyncWithClient:
    """When a graph_client is provided, nodes and edges are persisted."""

    @pytest.mark.asyncio
    async def test_calls_batch_upsert_nodes(self) -> None:
        state = _make_state(num_nodes=3, num_edges=0)
        client = AsyncMock()
        client.batch_upsert_nodes.return_value = ["n0", "n1", "n2"]
        client.batch_upsert_edges.return_value = []

        result = await write_to_graph_async(state, client)

        client.batch_upsert_nodes.assert_awaited_once_with(
            state["_nodes"], "ws-1", "t-1"
        )
        assert result["ingestion_stats"]["nodes_written"] == 3

    @pytest.mark.asyncio
    async def test_calls_batch_upsert_edges(self) -> None:
        state = _make_state(num_nodes=0, num_edges=2)
        client = AsyncMock()
        client.batch_upsert_nodes.return_value = []
        client.batch_upsert_edges.return_value = ["e0", "e1"]

        result = await write_to_graph_async(state, client)

        client.batch_upsert_edges.assert_awaited_once_with(
            state["_edges"], "ws-1", "t-1"
        )
        assert result["ingestion_stats"]["edges_written"] == 2

    @pytest.mark.asyncio
    async def test_records_processing_time(self) -> None:
        state = _make_state()
        client = AsyncMock()
        client.batch_upsert_nodes.return_value = ["n0", "n1", "n2"]
        client.batch_upsert_edges.return_value = ["e0", "e1"]

        result = await write_to_graph_async(state, client)
        assert "write_to_graph" in result["processing_time"]
        assert result["processing_time"]["write_to_graph"] >= 0


# ═══════════════════════════════════════════════════════════════════════════
#  write_to_graph_async — None graph client
# ═══════════════════════════════════════════════════════════════════════════


class TestWriteToGraphAsyncNoneClient:
    """When graph_client is None, data stays in state without crash."""

    @pytest.mark.asyncio
    async def test_no_crash_on_none_client(self) -> None:
        state = _make_state(num_nodes=5, num_edges=3)
        result = await write_to_graph_async(state, None)
        assert result["ingestion_stats"]["nodes_written"] == 5
        assert result["ingestion_stats"]["edges_written"] == 3

    @pytest.mark.asyncio
    async def test_processing_time_recorded(self) -> None:
        state = _make_state()
        result = await write_to_graph_async(state, None)
        assert "write_to_graph" in result["processing_time"]


# ═══════════════════════════════════════════════════════════════════════════
#  write_to_graph_async — exception handling
# ═══════════════════════════════════════════════════════════════════════════


class TestWriteToGraphAsyncExceptions:
    """Batch operation failures should be caught and recorded."""

    @pytest.mark.asyncio
    async def test_node_upsert_failure_recorded(self) -> None:
        state = _make_state(num_nodes=2, num_edges=1)
        client = AsyncMock()
        client.batch_upsert_nodes.side_effect = RuntimeError("Neo4j connection lost")
        client.batch_upsert_edges.return_value = ["e0"]

        result = await write_to_graph_async(state, client)

        # Node write should have failed, edge write should succeed
        assert result["ingestion_stats"]["nodes_written"] == 0
        assert result["ingestion_stats"]["edges_written"] == 1
        error_msgs = [e["message"] for e in result["errors"]]
        assert any("Node upsert failed" in m for m in error_msgs)

    @pytest.mark.asyncio
    async def test_edge_upsert_failure_recorded(self) -> None:
        state = _make_state(num_nodes=2, num_edges=1)
        client = AsyncMock()
        client.batch_upsert_nodes.return_value = ["n0", "n1"]
        client.batch_upsert_edges.side_effect = RuntimeError("timeout")

        result = await write_to_graph_async(state, client)

        assert result["ingestion_stats"]["nodes_written"] == 2
        assert result["ingestion_stats"]["edges_written"] == 0
        error_msgs = [e["message"] for e in result["errors"]]
        assert any("Edge upsert failed" in m for m in error_msgs)

    @pytest.mark.asyncio
    async def test_both_fail_records_both_errors(self) -> None:
        state = _make_state(num_nodes=1, num_edges=1)
        client = AsyncMock()
        client.batch_upsert_nodes.side_effect = RuntimeError("node err")
        client.batch_upsert_edges.side_effect = RuntimeError("edge err")

        result = await write_to_graph_async(state, client)

        assert result["ingestion_stats"]["nodes_written"] == 0
        assert result["ingestion_stats"]["edges_written"] == 0
        assert len(result["errors"]) == 2
