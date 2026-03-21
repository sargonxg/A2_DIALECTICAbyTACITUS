"""
Unit tests for dialectica_extraction.pipeline — step functions with mock data.

Tests chunking, state dataclasses, and GLiNER prefilter fallback behavior.
No external services (Gemini, Vertex AI, GLiNER model) required.
"""
from __future__ import annotations

import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_extraction.pipeline import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    ExtractionError,
    ExtractionState,
    TextChunk,
    chunk_document,
    gliner_prefilter,
)


# ═══════════════════════════════════════════════════════════════════════════
#  CHUNK_DOCUMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestChunkDocumentShortText:
    """Text shorter than CHUNK_SIZE should produce exactly one chunk."""

    def test_single_chunk_returned(self):
        text = "A short paragraph about a conflict."
        state: ExtractionState = {"text": text, "tier": "essential"}
        result = chunk_document(state)

        assert len(result["chunks"]) == 1

    def test_single_chunk_content_matches(self):
        text = "A short paragraph about a conflict."
        state: ExtractionState = {"text": text, "tier": "essential"}
        result = chunk_document(state)

        chunk = result["chunks"][0]
        assert chunk["text"] == text
        assert chunk["index"] == 0
        assert chunk["start"] == 0
        assert chunk["end"] == len(text)

    def test_text_just_under_limit(self):
        """Text exactly at CHUNK_SIZE should still be a single chunk."""
        text = "x" * CHUNK_SIZE
        state: ExtractionState = {"text": text, "tier": "essential"}
        result = chunk_document(state)

        assert len(result["chunks"]) == 1
        assert result["chunks"][0]["text"] == text


class TestChunkDocumentLongText:
    """Text 5000+ chars should produce multiple overlapping chunks."""

    def test_multiple_chunks_produced(self):
        text = "A" * 5000
        state: ExtractionState = {"text": text, "tier": "essential"}
        result = chunk_document(state)

        assert len(result["chunks"]) > 1

    def test_chunks_cover_full_text(self):
        """All characters in the original text should appear in at least one chunk."""
        text = "A" * 5000
        state: ExtractionState = {"text": text, "tier": "essential"}
        result = chunk_document(state)

        chunks = result["chunks"]
        # First chunk starts at 0
        assert chunks[0]["start"] == 0
        # Last chunk covers the end
        assert chunks[-1]["end"] == len(text)

    def test_chunks_have_overlap(self):
        """Adjacent chunks should overlap by approximately CHUNK_OVERLAP chars."""
        text = "A" * 5000
        state: ExtractionState = {"text": text, "tier": "essential"}
        result = chunk_document(state)

        chunks = result["chunks"]
        if len(chunks) >= 2:
            c1_end = chunks[0]["end"]
            c2_start = chunks[1]["start"]
            overlap = c1_end - c2_start
            assert overlap > 0, "Chunks must overlap"
            assert overlap == CHUNK_OVERLAP

    def test_chunk_indices_sequential(self):
        text = "A" * 5000
        state: ExtractionState = {"text": text, "tier": "essential"}
        result = chunk_document(state)

        indices = [c["index"] for c in result["chunks"]]
        assert indices == list(range(len(indices)))

    def test_very_long_text(self):
        """Test with 20,000 chars to verify many chunks."""
        text = "word " * 4000  # 20,000 chars
        state: ExtractionState = {"text": text, "tier": "essential"}
        result = chunk_document(state)

        assert len(result["chunks"]) >= 5


class TestChunkPreservesSentenceBoundaries:
    """Chunking should break at sentence boundaries when possible."""

    def test_splits_at_period_space(self):
        """Sentences ending with '. ' should be preferred split points."""
        # Build text with clear sentence boundaries that exceeds CHUNK_SIZE
        sentence = "This is a conflict sentence about war and negotiation. "
        repeat_count = (CHUNK_SIZE // len(sentence)) + 5
        text = sentence * repeat_count
        state: ExtractionState = {"text": text, "tier": "essential"}
        result = chunk_document(state)

        assert len(result["chunks"]) >= 2
        # First chunk should end at a sentence boundary (period + space)
        first_chunk_text = result["chunks"][0]["text"]
        assert first_chunk_text.rstrip().endswith(".")

    def test_splits_at_period_newline(self):
        """Sentences ending with '.\\n' should be preferred split points."""
        sentence = "This is a conflict sentence about mediation.\n"
        repeat_count = (CHUNK_SIZE // len(sentence)) + 5
        text = sentence * repeat_count
        state: ExtractionState = {"text": text, "tier": "essential"}
        result = chunk_document(state)

        assert len(result["chunks"]) >= 2


class TestChunkDocumentEmpty:
    """Empty or whitespace-only text edge cases."""

    def test_empty_string(self):
        """Empty text is <= CHUNK_SIZE, so it produces a single chunk with empty text."""
        state: ExtractionState = {"text": "", "tier": "essential"}
        result = chunk_document(state)
        assert len(result["chunks"]) == 1
        assert result["chunks"][0]["text"] == ""
        assert result["chunks"][0]["start"] == 0
        assert result["chunks"][0]["end"] == 0

    def test_whitespace_only(self):
        """Whitespace-only text is <= CHUNK_SIZE; short-text path stores it as-is."""
        state: ExtractionState = {"text": "   ", "tier": "essential"}
        result = chunk_document(state)
        assert len(result["chunks"]) == 1
        assert result["chunks"][0]["text"] == "   "

    def test_missing_text_key(self):
        """State with no 'text' key defaults to '' via state.get('text', '')."""
        state: ExtractionState = {"tier": "essential"}
        result = chunk_document(state)
        assert len(result["chunks"]) == 1
        assert result["chunks"][0]["text"] == ""


class TestChunkDocumentStateInit:
    """chunk_document should initialize default state fields."""

    def test_processing_time_recorded(self):
        state: ExtractionState = {"text": "Test.", "tier": "essential"}
        result = chunk_document(state)
        assert "chunk_document" in result["processing_time"]
        assert isinstance(result["processing_time"]["chunk_document"], float)
        assert result["processing_time"]["chunk_document"] >= 0

    def test_errors_initialized(self):
        state: ExtractionState = {"text": "Test.", "tier": "essential"}
        result = chunk_document(state)
        assert result.get("errors") == []

    def test_retry_count_initialized(self):
        state: ExtractionState = {"text": "Test.", "tier": "essential"}
        result = chunk_document(state)
        assert result.get("retry_count") == 0

    def test_requires_review_initialized(self):
        state: ExtractionState = {"text": "Test.", "tier": "essential"}
        result = chunk_document(state)
        assert result.get("requires_review") is False
        assert result.get("review_reasons") == []


# ═══════════════════════════════════════════════════════════════════════════
#  EXTRACTION STATE TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestExtractionStateDefaults:
    """ExtractionState (TypedDict) can be created with minimal fields."""

    def test_minimal_creation(self):
        """TypedDict with total=False allows empty creation."""
        state: ExtractionState = {}
        assert isinstance(state, dict)

    def test_with_required_fields(self):
        state: ExtractionState = {
            "text": "Some conflict text.",
            "tier": "essential",
        }
        assert state["text"] == "Some conflict text."
        assert state["tier"] == "essential"

    def test_with_all_fields(self):
        state: ExtractionState = {
            "text": "Text",
            "tier": "essential",
            "workspace_id": "ws-1",
            "tenant_id": "t-1",
            "chunks": [],
            "prefilter_results": [],
            "raw_entities": [],
            "validated_nodes": [],
            "validated_edges": [],
            "invalid_entities": [],
            "validation_errors": [],
            "embeddings": {},
            "errors": [],
            "retry_count": 0,
            "processing_time": {},
            "ingestion_stats": {},
            "requires_review": False,
            "review_reasons": [],
            "_nodes": [],
            "_edges": [],
        }
        assert state["workspace_id"] == "ws-1"
        assert state["retry_count"] == 0
        assert state["requires_review"] is False

    def test_state_is_dict(self):
        """ExtractionState is a TypedDict, so it behaves like a plain dict."""
        state: ExtractionState = {"text": "Hello", "tier": "essential"}
        assert isinstance(state, dict)
        state["chunks"] = [{"text": "Hello", "index": 0, "start": 0, "end": 5}]
        assert len(state["chunks"]) == 1


# ═══════════════════════════════════════════════════════════════════════════
#  TEXT CHUNK DATACLASS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestTextChunkDataclass:
    """TextChunk is a dataclass holding chunk metadata."""

    def test_creation(self):
        chunk = TextChunk(text="Hello world", index=0, start=0, end=11)
        assert chunk.text == "Hello world"
        assert chunk.index == 0
        assert chunk.start == 0
        assert chunk.end == 11

    def test_fields(self):
        chunk = TextChunk(text="Test", index=2, start=100, end=104)
        assert chunk.index == 2
        assert chunk.start == 100
        assert chunk.end == 104

    def test_empty_text(self):
        chunk = TextChunk(text="", index=0, start=0, end=0)
        assert chunk.text == ""

    def test_large_index(self):
        chunk = TextChunk(text="chunk", index=999, start=50000, end=50005)
        assert chunk.index == 999


# ═══════════════════════════════════════════════════════════════════════════
#  EXTRACTION ERROR DATACLASS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestExtractionErrorDataclass:
    """ExtractionError captures pipeline step errors."""

    def test_creation_minimal(self):
        err = ExtractionError(step="chunk_document", message="Something failed")
        assert err.step == "chunk_document"
        assert err.message == "Something failed"
        assert err.details == {}

    def test_creation_with_details(self):
        err = ExtractionError(
            step="extract_entities",
            message="Gemini timeout",
            details={"chunk_index": 3, "retry": 2},
        )
        assert err.step == "extract_entities"
        assert err.details["chunk_index"] == 3
        assert err.details["retry"] == 2

    def test_default_details_is_empty_dict(self):
        err1 = ExtractionError(step="s1", message="m1")
        err2 = ExtractionError(step="s2", message="m2")
        # Default factory should give independent dicts
        err1.details["key"] = "value"
        assert "key" not in err2.details


# ═══════════════════════════════════════════════════════════════════════════
#  GLINER PREFILTER FALLBACK TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestGlinerPrefilterFallback:
    """When GLiNER is not installed, keyword fallback should work for all chunks."""

    def _make_state(self, chunk_texts: list[str]) -> ExtractionState:
        chunks = [
            {"text": t, "index": i, "start": 0, "end": len(t)}
            for i, t in enumerate(chunk_texts)
        ]
        return {
            "text": " ".join(chunk_texts),
            "tier": "essential",
            "chunks": chunks,
            "processing_time": {},
            "errors": [],
        }

    def test_returns_result_for_every_chunk(self):
        """Prefilter should return one result per chunk."""
        state = self._make_state([
            "The conflict escalated between rebel forces and the government.",
            "Talks began at the summit to negotiate a ceasefire.",
            "Meanwhile the weather remained clear over the region.",
        ])
        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            result = gliner_prefilter(state)

        assert len(result["prefilter_results"]) == 3

    def test_conflict_text_gets_entities(self):
        """Text with conflict keywords should have entity_count > 0."""
        state = self._make_state([
            "The rebel militia launched an attack on the government capital.",
        ])
        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            result = gliner_prefilter(state)

        r = result["prefilter_results"][0]
        assert r["entity_count"] > 0
        assert r["entity_density"] > 0

    def test_bland_text_gets_few_or_no_entities(self):
        """Bland text with no conflict keywords should have low entity count."""
        state = self._make_state([
            "The cat sat on the mat and looked out the window.",
        ])
        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            result = gliner_prefilter(state)

        r = result["prefilter_results"][0]
        assert r["entity_count"] == 0

    def test_conflict_chunk_higher_priority_than_bland(self):
        """Conflict-heavy chunk should have higher priority score than bland text."""
        state = self._make_state([
            "The conflict between rebel forces and the government escalated into violence.",
            "The weather was sunny today with no clouds in the sky.",
        ])
        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            result = gliner_prefilter(state)

        r0 = result["prefilter_results"][0]
        r1 = result["prefilter_results"][1]
        assert r0["priority_score"] > r1["priority_score"]

    def test_processing_time_recorded(self):
        state = self._make_state(["Some text about a protest."])
        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            result = gliner_prefilter(state)

        assert "gliner_prefilter" in result["processing_time"]
        assert result["processing_time"]["gliner_prefilter"] >= 0

    def test_empty_chunks(self):
        """No chunks should produce no prefilter results."""
        state: ExtractionState = {
            "text": "",
            "tier": "essential",
            "chunks": [],
            "processing_time": {},
            "errors": [],
        }
        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            result = gliner_prefilter(state)

        assert result["prefilter_results"] == []

    def test_result_fields_present(self):
        """Each prefilter result dict should contain expected keys."""
        state = self._make_state([
            "The UN mediator brokered a ceasefire agreement.",
        ])
        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            result = gliner_prefilter(state)

        r = result["prefilter_results"][0]
        assert "chunk_index" in r
        assert "entity_count" in r
        assert "entity_density" in r
        assert "priority_score" in r
        assert r["chunk_index"] == 0

    def test_gliner_exception_passes_all_chunks(self):
        """If GLiNERPreFilter() raises, all chunks pass with default scores."""
        state = self._make_state([
            "Some chunk.",
            "Another chunk.",
        ])
        with patch(
            "dialectica_extraction.pipeline.GLiNERPreFilter",
            side_effect=RuntimeError("model load failed"),
        ):
            result = gliner_prefilter(state)

        # All chunks should pass through with default priority_score=1.0
        assert len(result["prefilter_results"]) == 2
        for r in result["prefilter_results"]:
            assert r["priority_score"] == 1.0
