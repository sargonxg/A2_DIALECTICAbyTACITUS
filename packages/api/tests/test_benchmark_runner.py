"""
Tests for BenchmarkRunner._run_extraction — real pipeline integration + stub fallback.

Verifies:
- _run_extraction tries the real ExtractionPipeline first
- Falls back to _stub_extraction when pipeline is unavailable
- Falls back when pipeline returns zero nodes
- _stub_extraction returns expected structure
"""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_api.benchmark_runner import BenchmarkRunner

# ═══════════════════════════════════════════════════════════════════════════
#  _stub_extraction
# ═══════════════════════════════════════════════════════════════════════════


class TestStubExtraction:
    """The static fallback stub should return realistic JCPOA data."""

    def test_returns_tuple_of_two_lists(self) -> None:
        nodes, edges = BenchmarkRunner._stub_extraction()
        assert isinstance(nodes, list)
        assert isinstance(edges, list)

    def test_stub_nodes_non_empty(self) -> None:
        nodes, _ = BenchmarkRunner._stub_extraction()
        assert len(nodes) > 0

    def test_stub_edges_non_empty(self) -> None:
        _, edges = BenchmarkRunner._stub_extraction()
        assert len(edges) > 0

    def test_stub_nodes_have_required_fields(self) -> None:
        nodes, _ = BenchmarkRunner._stub_extraction()
        for node in nodes:
            assert "id" in node
            assert "label" in node
            assert "name" in node

    def test_stub_edges_have_required_fields(self) -> None:
        _, edges = BenchmarkRunner._stub_extraction()
        for edge in edges:
            assert "source" in edge
            assert "target" in edge
            assert "type" in edge


# ═══════════════════════════════════════════════════════════════════════════
#  _run_extraction — real pipeline integration
# ═══════════════════════════════════════════════════════════════════════════


class TestRunExtractionRealPipeline:
    """When ExtractionPipeline is available and produces nodes, use its output."""

    @pytest.mark.asyncio
    async def test_uses_real_pipeline_when_available(self) -> None:
        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.run.return_value = {
            "validated_nodes": [
                {"id": "n1", "label": "Actor", "name": "Test Actor"},
            ],
            "validated_edges": [
                {"source": "n1", "target": "n2", "type": "PARTY_TO"},
            ],
        }

        with patch(
            "dialectica_api.benchmark_runner.BenchmarkRunner._stub_extraction"
        ) as mock_stub, patch.dict(
            "sys.modules",
            {
                "dialectica_extraction": MagicMock(),
                "dialectica_extraction.pipeline": MagicMock(
                    ExtractionPipeline=MagicMock(return_value=mock_pipeline_instance),
                ),
                "dialectica_ontology": MagicMock(),
                "dialectica_ontology.tiers": MagicMock(
                    OntologyTier=MagicMock(return_value="standard"),
                ),
            },
        ):
            runner = BenchmarkRunner()
            nodes, edges = await runner._run_extraction("some text", "standard", "test")

        assert len(nodes) == 1
        assert nodes[0]["name"] == "Test Actor"
        assert len(edges) == 1
        mock_stub.assert_not_called()


class TestRunExtractionFallback:
    """When pipeline is unavailable or returns no nodes, fall back to stub."""

    @pytest.mark.asyncio
    async def test_falls_back_on_import_error(self) -> None:
        """If dialectica_extraction is not installed, use stub."""
        runner = BenchmarkRunner()

        with patch(
            "dialectica_api.benchmark_runner.BenchmarkRunner._stub_extraction",
            return_value=(
                [{"id": "stub1", "label": "Actor", "name": "Stub"}],
                [],
            ),
        ) as mock_stub:
            # Force ImportError by patching builtins
            _orig = __import__

            def failing_import(
                name: str, *args: object, **kwargs: object
            ) -> object:
                if "dialectica_extraction" in name:
                    raise ImportError("not installed")
                return _orig(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=failing_import):
                nodes, edges = await runner._run_extraction(
                    "text", "standard", "model"
                )

        mock_stub.assert_called_once()
        assert nodes[0]["id"] == "stub1"

    @pytest.mark.asyncio
    async def test_falls_back_when_pipeline_returns_empty_nodes(self) -> None:
        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.run.return_value = {
            "validated_nodes": [],
            "validated_edges": [],
        }

        with patch(
            "dialectica_api.benchmark_runner.BenchmarkRunner._stub_extraction",
            return_value=(
                [{"id": "s1", "label": "Actor", "name": "Fallback"}],
                [],
            ),
        ) as mock_stub, patch.dict(
            "sys.modules",
            {
                "dialectica_extraction": MagicMock(),
                "dialectica_extraction.pipeline": MagicMock(
                    ExtractionPipeline=MagicMock(return_value=mock_pipeline_instance),
                ),
                "dialectica_ontology": MagicMock(),
                "dialectica_ontology.tiers": MagicMock(
                    OntologyTier=MagicMock(return_value="standard"),
                ),
            },
        ):
            runner = BenchmarkRunner()
            nodes, edges = await runner._run_extraction("text", "standard", "m")

        mock_stub.assert_called_once()
        assert nodes[0]["name"] == "Fallback"

    @pytest.mark.asyncio
    async def test_falls_back_on_runtime_error(self) -> None:
        """If the pipeline raises at runtime, fall back to stub."""
        mock_pipeline_cls = MagicMock()
        mock_pipeline_cls.return_value.run.side_effect = RuntimeError("Gemini down")

        with patch(
            "dialectica_api.benchmark_runner.BenchmarkRunner._stub_extraction",
            return_value=(
                [{"id": "s1", "label": "Actor", "name": "Fallback"}],
                [],
            ),
        ) as mock_stub, patch.dict(
            "sys.modules",
            {
                "dialectica_extraction": MagicMock(),
                "dialectica_extraction.pipeline": MagicMock(
                    ExtractionPipeline=mock_pipeline_cls,
                ),
                "dialectica_ontology": MagicMock(),
                "dialectica_ontology.tiers": MagicMock(
                    OntologyTier=MagicMock(return_value="standard"),
                ),
            },
        ):
            runner = BenchmarkRunner()
            nodes, edges = await runner._run_extraction("text", "standard", "m")

        mock_stub.assert_called_once()
