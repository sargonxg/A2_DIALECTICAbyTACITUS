"""Tests for QdrantVectorStore (qdrant_store.py) — simplified node-level vector store."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_graph.qdrant_store import COLLECTION_NAME, VECTOR_DIM, QdrantVectorStore

# qdrant_client is an optional dependency; skip tests that import its models
qdrant_client = pytest.importorskip("qdrant_client", reason="qdrant-client not installed")


@dataclass
class MockPoint:
    payload: dict
    score: float


@dataclass
class MockQueryResult:
    points: list[MockPoint]


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestConstruction:
    def test_defaults(self):
        store = QdrantVectorStore()
        assert store._url == "http://localhost:6333"
        assert store._api_key is None

    def test_custom_params(self):
        store = QdrantVectorStore(url="http://qdrant.prod:6333", api_key="secret")
        assert store._url == "http://qdrant.prod:6333"
        assert store._api_key == "secret"


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants:
    def test_collection_name(self):
        assert COLLECTION_NAME == "dialectica_nodes"

    def test_vector_dim(self):
        assert VECTOR_DIM == 768


# ---------------------------------------------------------------------------
# search_semantic
# ---------------------------------------------------------------------------


class TestSearchSemantic:
    @pytest.fixture
    def mock_store(self):
        store = QdrantVectorStore()
        mock_client = MagicMock()
        mock_client.query_points.return_value = MockQueryResult(
            points=[
                MockPoint(
                    payload={"node_id": "n1", "node_type": "Actor", "name": "Iran"},
                    score=0.95,
                ),
                MockPoint(
                    payload={"node_id": "n2", "node_type": "Event", "name": "Attack"},
                    score=0.82,
                ),
            ]
        )
        store._client = mock_client
        return store

    @pytest.mark.asyncio
    async def test_search_returns_results(self, mock_store):
        results = await mock_store.search_semantic(
            query_embedding=[0.1] * VECTOR_DIM,
            tenant_id="t1",
            top_k=5,
        )
        assert len(results) == 2
        assert results[0]["node_id"] == "n1"
        assert results[0]["score"] == 0.95
        assert results[0]["label"] == "Actor"

    @pytest.mark.asyncio
    async def test_search_with_node_type_filter(self, mock_store):
        await mock_store.search_semantic(
            query_embedding=[0.1] * VECTOR_DIM,
            tenant_id="t1",
            node_types=["Actor"],
        )
        mock_store._client.query_points.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_date_filter(self, mock_store):
        from datetime import datetime

        await mock_store.search_semantic(
            query_embedding=[0.1] * VECTOR_DIM,
            tenant_id="t1",
            date_from=datetime(2024, 1, 1),
            date_to=datetime(2024, 12, 31),
        )
        mock_store._client.query_points.assert_called_once()


# ---------------------------------------------------------------------------
# upsert_vectors
# ---------------------------------------------------------------------------


class TestUpsertVectors:
    @pytest.fixture
    def mock_store(self):
        store = QdrantVectorStore()
        store._client = MagicMock()
        return store

    @pytest.mark.asyncio
    async def test_upsert_single(self, mock_store):
        await mock_store.upsert_vectors(
            node_id="node1",
            embedding=[0.1] * VECTOR_DIM,
            workspace_id="ws1",
            tenant_id="t1",
            label="Actor",
            name="Iran",
        )
        mock_store._client.upsert.assert_called_once()
        call_args = mock_store._client.upsert.call_args
        points = call_args.kwargs.get("points") or call_args[1].get("points")
        assert len(points) == 1
        assert points[0].payload["node_id"] == "node1"
        assert points[0].payload["node_type"] == "Actor"


# ---------------------------------------------------------------------------
# batch_upsert
# ---------------------------------------------------------------------------


class TestBatchUpsert:
    @pytest.fixture
    def mock_store(self):
        store = QdrantVectorStore()
        store._client = MagicMock()
        return store

    @pytest.mark.asyncio
    async def test_batch_upsert_multiple(self, mock_store):
        items = [
            {
                "node_id": "n1",
                "embedding": [0.1] * VECTOR_DIM,
                "workspace_id": "ws1",
                "tenant_id": "t1",
                "label": "Actor",
                "name": "Iran",
            },
            {
                "node_id": "n2",
                "embedding": [0.2] * VECTOR_DIM,
                "workspace_id": "ws1",
                "tenant_id": "t1",
                "label": "Event",
                "name": "Summit",
            },
        ]
        count = await mock_store.batch_upsert(items)
        assert count == 2
        mock_store._client.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_batch_upsert_skips_missing(self, mock_store):
        items = [
            {"node_id": "n1"},  # no embedding
            {"embedding": [0.1] * VECTOR_DIM},  # no node_id
        ]
        count = await mock_store.batch_upsert(items)
        assert count == 0

    @pytest.mark.asyncio
    async def test_batch_upsert_empty(self, mock_store):
        count = await mock_store.batch_upsert([])
        assert count == 0


# ---------------------------------------------------------------------------
# close
# ---------------------------------------------------------------------------


class TestClose:
    @pytest.mark.asyncio
    async def test_close_cleans_up(self):
        store = QdrantVectorStore()
        store._client = MagicMock()
        await store.close()
        assert store._client is None
