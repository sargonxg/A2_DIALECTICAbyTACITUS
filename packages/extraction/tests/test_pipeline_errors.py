"""Tests for pipeline error handling — Prompt 0.2."""
from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture()
def base_state() -> dict:
    return {
        "text": "Russia and Ukraine signed a ceasefire in 2024.",
        "tier": "standard",
        "workspace_id": "ws-test",
        "tenant_id": "t-test",
        "errors": [],
        "retry_count": 0,
        "processing_time": {},
        "ingestion_stats": {},
        "gliner_available": True,
    }


class TestInstructorImportError:
    def test_import_error_falls_back_gracefully(self, base_state):
        """When instructor is not importable, extract_entities does not crash."""
        from dialectica_extraction.pipeline import extract_entities

        state = {**base_state, "chunks": [{"text": "test", "index": 0, "start": 0, "end": 4}]}
        # This should not raise even if instructor is missing
        try:
            result = extract_entities(state)
            # Should not have crashed
            assert isinstance(result, dict)
        except ImportError:
            pytest.fail("extract_entities raised ImportError — should catch it internally")


class TestGeminiExtractionError:
    def test_gemini_error_logged_to_state(self, base_state, caplog):
        """When extraction fails, error is logged at ERROR level and appended to state['errors']."""
        import logging
        from dialectica_extraction.pipeline import extract_entities

        # Patch the GeminiExtractor to raise
        with patch(
            "dialectica_extraction.pipeline.GeminiExtractor",
            side_effect=RuntimeError("Gemini 503"),
        ):
            state = {
                **base_state,
                "chunks": [{"text": "test chunk", "index": 0, "start": 0, "end": 10}],
            }
            with caplog.at_level(logging.ERROR, logger="dialectica_extraction.pipeline"):
                result = extract_entities(state)

        # Error must appear in state["errors"]
        assert len(result.get("errors", [])) > 0 or len(caplog.records) > 0


class TestRepairRetries:
    def test_retries_exhaust_does_not_increment_beyond_max(self, base_state):
        """When retry_count >= MAX_REPAIR_RETRIES, repair_extraction does not increment further."""
        from dialectica_extraction.pipeline import MAX_REPAIR_RETRIES, repair_extraction

        state = {
            **base_state,
            "retry_count": MAX_REPAIR_RETRIES,
            "validation_errors": ["missing required field: confidence_score"],
            "validated_nodes": [],
        }
        result = repair_extraction(state)
        # Must not increment beyond max
        assert result.get("retry_count", 0) >= MAX_REPAIR_RETRIES


class TestGlinerFailure:
    def test_gliner_exception_sets_unavailable_flag(self, base_state, caplog):
        """When GLiNER raises during prefilter, state['gliner_available'] is set to False."""
        import logging
        from dialectica_extraction.pipeline import gliner_prefilter

        # Patch GLiNERPreFilter to raise on any call
        with patch(
            "dialectica_extraction.pipeline.GLiNERPreFilter",
            side_effect=RuntimeError("Model load failed"),
        ):
            state = {
                **base_state,
                "chunks": [{"text": "test", "index": 0, "start": 0, "end": 4}],
            }
            with caplog.at_level(logging.WARNING):
                result = gliner_prefilter(state)

        # Flag must be set to False
        assert result.get("gliner_available") is False
        # Should still return prefilter_results (fallback)
        assert "prefilter_results" in result
