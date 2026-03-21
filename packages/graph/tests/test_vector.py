"""Tests for QdrantVectorStore — named vectors, tenant isolation, hybrid search."""
from __future__ import annotations

import sys
import os
from datetime import datetime
from unittest.mock import MagicMock, patch, PropertyMock
from dataclasses import dataclass

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_graph.vector import QdrantVectorStore, COLLECTION_NAME, SEMANTIC_DIM, STRUCTURAL_DIM
from dialectica_ontology.primitives import Actor


@dataclass
class MockPoint:
    payload: dict
    score: float


@dataclass
class MockQueryResult:
    points: list[MockPoint]


class TestQdrantVectorStoreConstruction:
    def test_defaults(self):
        store = QdrantVectorStore()
        assert store._host == "localhost"
        assert store._port == 6334
        assert store._collection_name == COLLECTION_NAME

    def test_custom_params(self):
        store = QdrantVectorStore(host="qdrant.prod", port=6335, collection_name="custom")
        assert store._host == "qdrant.prod"
        assert store._collection_name == "custom"


class TestUpsertVectors:
    @pytest.fixture
    def mock_store(self):
        store = QdrantVectorStore()
        store._client = MagicMock()
        return store

    @pytest.mark.asyncio
    async def test_upsert_with_semantic_only(self, mock_store):
        actor = Actor(name="Test", actor_type="person")
        embeddings = {actor.id: [0.1] * SEMANTIC_DIM}
        count = await mock_store.upsert_vectors(
            [actor], embeddings, tenant_id="t1", workspace_id="ws1"
        )
        assert count == 1
        mock_store._client.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_upsert_with_both_vectors(self, mock_store):
        actor = Actor(name="Test", actor_type="person")
        sem = {actor.id: [0.1] * SEMANTIC_DIM}
        struct = {actor.id: [0.2] * STRUCTURAL_DIM}
        count = await mock_store.upsert_vectors(
            [actor], sem, struct, tenant_id="t1", workspace_id="ws1"
        )
        assert count == 1

    @pytest.mark.asyncio
    async def test_upsert_skips_missing_embedding(self, mock_store):
        actor = Actor(name="Test", actor_type="person")
        count = await mock_store.upsert_vectors(
            [actor], {}, tenant_id="t1", workspace_id="ws1"
        )
        assert count == 0


class TestSearchSemantic:
    @pytest.fixture
    def mock_store(self):
        store = QdrantVectorStore()
        mock_client = MagicMock()
        mock_client.query_points.return_value = MockQueryResult(points=[
            MockPoint(payload={"node_id": "n1", "node_type": "Actor"}, score=0.95),
            MockPoint(payload={"node_id": "n2", "node_type": "Event"}, score=0.82),
        ])
        store._client = mock_client
        return store

    @pytest.mark.asyncio
    async def test_search_returns_results(self, mock_store):
        results = await mock_store.search_semantic(
            query_embedding=[0.1] * SEMANTIC_DIM,
            tenant_id="t1",
            top_k=5,
        )
        assert len(results) == 2
        assert results[0]["node_id"] == "n1"
        assert results[0]["score"] == 0.95

    @pytest.mark.asyncio
    async def test_search_with_node_type_filter(self, mock_store):
        await mock_store.search_semantic(
            query_embedding=[0.1] * SEMANTIC_DIM,
            tenant_id="t1",
            node_types=["Actor"],
        )
        call_args = mock_store._client.query_points.call_args
        assert call_args.kwargs["using"] == "semantic"


class TestHybridSearch:
    @pytest.fixture
    def mock_store(self):
        store = QdrantVectorStore()
        mock_client = MagicMock()

        def query_side_effect(**kwargs):
            if kwargs.get("using") == "semantic":
                return MockQueryResult(points=[
                    MockPoint(payload={"node_id": "n1"}, score=0.9),
                    MockPoint(payload={"node_id": "n2"}, score=0.8),
                ])
            else:
                return MockQueryResult(points=[
                    MockPoint(payload={"node_id": "n2"}, score=0.95),
                    MockPoint(payload={"node_id": "n3"}, score=0.7),
                ])

        mock_client.query_points.side_effect = query_side_effect
        store._client = mock_client
        return store

    @pytest.mark.asyncio
    async def test_hybrid_rrf_fusion(self, mock_store):
        results = await mock_store.hybrid_search(
            query_embedding=[0.1] * SEMANTIC_DIM,
            kge_embedding=[0.2] * STRUCTURAL_DIM,
            tenant_id="t1",
            top_k=5,
        )
        # n2 should be ranked highest (appears in both)
        assert len(results) == 3
        node_ids = [r["node_id"] for r in results]
        assert "n2" in node_ids
        # n2 should have highest RRF score (in both lists)
        assert results[0]["node_id"] == "n2"


class TestDeleteTenant:
    @pytest.mark.asyncio
    async def test_delete_calls_qdrant(self):
        store = QdrantVectorStore()
        store._client = MagicMock()
        await store.delete_tenant("tenant-to-delete")
        store._client.delete.assert_called_once()


class TestDimensions:
    def test_semantic_dim(self):
        assert SEMANTIC_DIM == 768

    def test_structural_dim(self):
        assert STRUCTURAL_DIM == 256
