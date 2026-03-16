"""
Tests for dialectica_extraction.gemini — Gemini extractor (mocked).
"""
from __future__ import annotations

import json
import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_ontology.tiers import OntologyTier
from dialectica_extraction.gemini import GeminiExtractor, GeminiExtractionResult, ExtractionMetrics


class TestGeminiExtractor:
    def test_init(self):
        extractor = GeminiExtractor(project_id="test-project")
        assert extractor._project_id == "test-project"
        assert extractor._flash_model_id == "gemini-2.5-flash-001"

    def test_extraction_result_dataclass(self):
        result = GeminiExtractionResult(
            raw_nodes=[{"label": "Actor", "name": "Test"}],
            metrics=ExtractionMetrics(input_tokens=100, output_tokens=50),
        )
        assert len(result.raw_nodes) == 1
        assert result.metrics.input_tokens == 100
        assert result.error is None

    def test_extraction_result_with_error(self):
        result = GeminiExtractionResult(error="Test error")
        assert result.error == "Test error"
        assert len(result.raw_nodes) == 0

    def test_metrics_dataclass(self):
        metrics = ExtractionMetrics(
            input_tokens=500,
            output_tokens=200,
            latency_ms=1234.5,
            model="gemini-2.5-flash-001",
            retries=1,
        )
        assert metrics.input_tokens == 500
        assert metrics.retries == 1


class TestGeminiExtractorWithMock:
    """Tests using mocked Vertex AI calls."""

    @patch("dialectica_extraction.gemini.GeminiExtractor._call_gemini")
    def test_extract_entities_success(self, mock_call):
        mock_call.return_value = (
            {"nodes": [
                {"label": "Actor", "name": "Alice", "actor_type": "person", "confidence": 0.9},
                {"label": "Conflict", "name": "Dispute", "scale": "micro", "domain": "workplace", "status": "active"},
            ]},
            ExtractionMetrics(input_tokens=100, output_tokens=50, model="gemini-2.5-flash-001"),
        )

        extractor = GeminiExtractor(project_id="test")
        result = extractor.extract_entities("Test text", OntologyTier.ESSENTIAL)

        assert len(result.raw_nodes) == 2
        assert result.raw_nodes[0]["name"] == "Alice"
        assert result.error is None

    @patch("dialectica_extraction.gemini.GeminiExtractor._call_gemini")
    def test_extract_entities_failure(self, mock_call):
        mock_call.return_value = (None, ExtractionMetrics())

        extractor = GeminiExtractor(project_id="test")
        result = extractor.extract_entities("Test text", OntologyTier.ESSENTIAL)

        assert result.error is not None
        assert len(result.raw_nodes) == 0

    @patch("dialectica_extraction.gemini.GeminiExtractor._call_gemini")
    def test_extract_relationships(self, mock_call):
        mock_call.return_value = (
            {"edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1",
                 "source_label": "Actor", "target_label": "Conflict", "confidence": 0.8},
            ]},
            ExtractionMetrics(),
        )

        extractor = GeminiExtractor(project_id="test")
        entities = [{"id": "a1", "label": "Actor", "name": "Alice"}]
        result = extractor.extract_relationships(entities, "Test text", OntologyTier.ESSENTIAL)

        assert len(result.raw_edges) == 1
        assert result.raw_edges[0]["type"] == "PARTY_TO"

    @patch("dialectica_extraction.gemini.GeminiExtractor._call_gemini")
    def test_repair_entities(self, mock_call):
        mock_call.return_value = (
            {"nodes": [
                {"label": "Actor", "name": "Alice", "actor_type": "person", "confidence": 0.9},
            ]},
            ExtractionMetrics(),
        )

        extractor = GeminiExtractor(project_id="test")
        result = extractor.repair_entities(
            [{"label": "Actor", "name": "Alice"}],
            ["Actor.actor_type: field required"],
            OntologyTier.ESSENTIAL,
        )

        assert len(result.raw_nodes) == 1
        assert result.raw_nodes[0].get("actor_type") == "person"


class TestGLiNERPreFilter:
    def test_keyword_fallback(self):
        from dialectica_extraction.gliner_ner import GLiNERPreFilter

        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            prefilter = GLiNERPreFilter()
            results = prefilter.prefilter([
                "The conflict between rebel forces escalated into violence.",
                "The cat sat on the mat.",
            ])
            assert len(results) == 2
            # Conflict text should have higher entity density
            assert results[0].entity_count >= results[1].entity_count

    def test_priority_chunks(self):
        from dialectica_extraction.gliner_ner import GLiNERPreFilter, PrefilterResult

        results = [
            PrefilterResult(chunk_index=0, chunk_text="a", entity_density=5.0, priority_score=0.9),
            PrefilterResult(chunk_index=1, chunk_text="b", entity_density=1.0, priority_score=0.2),
            PrefilterResult(chunk_index=2, chunk_text="c", entity_density=3.0, priority_score=0.6),
        ]
        prefilter = GLiNERPreFilter()
        priority = prefilter.get_priority_chunks(results, min_score=0.3)
        assert len(priority) == 2
        assert priority[0].chunk_index == 0  # highest priority first


class TestEmbeddingService:
    def test_node_to_embedding_text(self):
        from dialectica_extraction.embeddings import _node_to_embedding_text
        from dialectica_ontology.primitives import Actor

        actor = Actor(name="Alice", actor_type="person", source_text="Alice is a negotiator")
        text = _node_to_embedding_text(actor)
        assert "Actor" in text
        assert "Alice" in text
        assert "negotiator" in text
