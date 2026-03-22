"""Tests for GraphRAG retriever, context builder, and community detector."""

from __future__ import annotations

import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_ontology.primitives import Actor, Conflict, Event
from dialectica_reasoning.graphrag.community import CommunitySummary, GraphCommunityDetector
from dialectica_reasoning.graphrag.context_builder import ConflictContextBuilder
from dialectica_reasoning.graphrag.retriever import (
    RRF_K,
    ConflictGraphRAGRetriever,
    RetrievalResult,
)

# ═══════════════════════════════════════════════════════════════════════════
#  RETRIEVER TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestRetriever:
    @pytest.fixture
    def mock_graph(self):
        gc = MagicMock()
        gc.get_nodes = AsyncMock(
            return_value=[
                Actor(name="Iran", actor_type="state"),
                Actor(name="USA", actor_type="state"),
            ]
        )
        gc.get_node = AsyncMock(return_value=Actor(name="Iran", actor_type="state"))
        gc.traverse = AsyncMock(
            return_value=MagicMock(
                nodes=[Actor(name="IAEA", actor_type="organization")],
                edges=[],
            )
        )
        return gc

    @pytest.fixture
    def mock_vector_store(self):
        vs = MagicMock()
        vs.search_semantic = AsyncMock(
            return_value=[
                {"node_id": "n1", "score": 0.95, "payload": {}},
                {"node_id": "n2", "score": 0.82, "payload": {}},
            ]
        )
        return vs

    @pytest.mark.asyncio
    async def test_retrieve_with_vector_store(self, mock_graph, mock_vector_store):
        retriever = ConflictGraphRAGRetriever(
            graph_client=mock_graph,
            vector_store=mock_vector_store,
        )
        result = await retriever.retrieve("nuclear program", "ws-1", tenant_id="t1")
        assert isinstance(result, RetrievalResult)
        assert result.retrieval_method == "hybrid"
        mock_vector_store.search_semantic.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_fallback_keyword(self, mock_graph):
        retriever = ConflictGraphRAGRetriever(graph_client=mock_graph)
        result = await retriever.retrieve("Iran", "ws-1")
        assert result.retrieval_method in ("hybrid", "fallback")

    @pytest.mark.asyncio
    async def test_rrf_constant(self):
        assert RRF_K == 60


# ═══════════════════════════════════════════════════════════════════════════
#  CONTEXT BUILDER TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestContextBuilder:
    def _make_result(self) -> RetrievalResult:
        a1 = Actor(name="Iran", actor_type="state")
        a2 = Actor(name="USA", actor_type="state")
        c1 = Conflict(name="JCPOA", scale="macro", domain="geopolitical", status="active")
        e1 = Event(event_type="protest", severity=0.7, occurred_at=datetime(2024, 1, 15))
        return RetrievalResult(
            query="nuclear program",
            workspace_id="ws-jcpoa",
            nodes=[a1, a2, c1, e1],
            edges=[],
            node_ids=[a1.id, a2.id, c1.id, e1.id],
            scores={a1.id: 0.9, a2.id: 0.8, c1.id: 0.7, e1.id: 0.6},
        )

    def test_build_context_general(self):
        builder = ConflictContextBuilder()
        result = self._make_result()
        context = builder.build_context(result, mode="general")
        assert "DIALECTICA" in context
        assert "Iran" in context
        assert "[source:" in context

    def test_build_context_escalation_mode(self):
        builder = ConflictContextBuilder()
        result = self._make_result()
        context = builder.build_context(result, mode="escalation")
        assert "CONFLICT STATE" in context

    def test_context_respects_budget(self):
        builder = ConflictContextBuilder()
        result = self._make_result()
        context = builder.build_context(result, max_chars=200)
        assert len(context) <= 250  # Small buffer for truncation marker

    def test_citation_markers_present(self):
        builder = ConflictContextBuilder()
        result = self._make_result()
        context = builder.build_context(result)
        assert "[source:" in context

    def test_empty_result(self):
        builder = ConflictContextBuilder()
        result = RetrievalResult(query="test", workspace_id="ws-1")
        context = builder.build_context(result)
        assert "Nodes retrieved: 0" in context


# ═══════════════════════════════════════════════════════════════════════════
#  COMMUNITY DETECTOR TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestCommunityDetector:
    @pytest.fixture
    def mock_graph(self):
        gc = MagicMock()
        gc.get_nodes = AsyncMock(
            side_effect=lambda ws, label=None: {
                "Actor": [
                    Actor(name="Iran", actor_type="state"),
                    Actor(name="USA", actor_type="state"),
                    Actor(name="IAEA", actor_type="organization"),
                ],
                "Issue": [],
            }.get(label, [])
        )
        gc.get_edges = AsyncMock(return_value=[])
        return gc

    @pytest.mark.asyncio
    async def test_detect_returns_summaries(self, mock_graph):
        detector = GraphCommunityDetector(mock_graph)
        summaries = await detector.detect_and_summarise("ws-1")
        assert isinstance(summaries, list)
        # With no edges, fallback gives each node its own community at each resolution
        assert len(summaries) > 0
        for s in summaries:
            assert isinstance(s, CommunitySummary)
            assert s.actor_count >= 1

    @pytest.mark.asyncio
    async def test_detect_empty_workspace(self, mock_graph):
        mock_graph.get_nodes = AsyncMock(return_value=[])
        detector = GraphCommunityDetector(mock_graph)
        summaries = await detector.detect_and_summarise("ws-empty")
        assert summaries == []

    def test_leiden_fallback_no_edges(self):
        partition = GraphCommunityDetector._leiden_partition(3, [], 1.0)
        assert len(partition) == 3

    def test_community_summary_fields(self):
        s = CommunitySummary(
            community_id=0,
            resolution=1.5,
            actor_names=["Iran", "USA"],
            summary="Test community",
            actor_count=2,
        )
        assert s.community_id == 0
        assert s.resolution == 1.5
        assert s.actor_count == 2
