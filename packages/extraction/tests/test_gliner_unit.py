"""
Unit tests for dialectica_extraction.gliner_ner — GLiNER pre-filter.

Tests keyword fallback, entity density, priority chunk filtering, and the
GLINER_AVAILABLE flag. No GLiNER model download required.
"""
from __future__ import annotations

import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_extraction.gliner_ner import (
    CONFLICT_KEYWORDS,
    GLINER_AVAILABLE,
    GLiNERPreFilter,
    PrefilterEntity,
    PrefilterResult,
)


# ═══════════════════════════════════════════════════════════════════════════
#  KEYWORD FALLBACK — CONFLICT TERM DETECTION
# ═══════════════════════════════════════════════════════════════════════════


class TestKeywordFallbackDetectsConflictTerms:
    """Keyword fallback should detect conflict-related terms in text."""

    @pytest.fixture
    def prefilter(self):
        """Create a GLiNERPreFilter with GLiNER forcibly disabled."""
        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            return GLiNERPreFilter()

    def test_conflict_keyword(self, prefilter):
        results = prefilter.prefilter(["The conflict between the two groups escalated."])
        assert len(results) == 1
        assert results[0].entity_count > 0
        entities_text = [e.text.lower() for e in results[0].entities]
        assert "conflict" in entities_text

    def test_negotiation_keyword(self, prefilter):
        results = prefilter.prefilter(["The negotiation stalled between the parties."])
        assert results[0].entity_count > 0
        entities_text = [e.text.lower() for e in results[0].entities]
        assert "negotiation" in entities_text

    def test_government_and_rebel(self, prefilter):
        results = prefilter.prefilter([
            "The government responded to the rebel offensive with sanctions."
        ])
        entities_text = [e.text.lower() for e in results[0].entities]
        assert "government" in entities_text
        assert "rebel" in entities_text
        assert "sanctions" in entities_text

    def test_multiple_conflict_terms(self, prefilter):
        text = (
            "The president called for mediation after the attack on "
            "the border region led to escalation of the war."
        )
        results = prefilter.prefilter([text])
        # Should find: president, mediation, attack, border, region, escalation, war
        assert results[0].entity_count >= 5

    def test_ceasefire_and_peace(self, prefilter):
        results = prefilter.prefilter(["A ceasefire was agreed, bringing hope for peace."])
        entities_text = [e.text.lower() for e in results[0].entities]
        assert "ceasefire" in entities_text
        assert "peace" in entities_text

    def test_emotion_keywords(self, prefilter):
        results = prefilter.prefilter(["Anger and fear spread through the community."])
        entities_text = [e.text.lower() for e in results[0].entities]
        assert "anger" in entities_text
        assert "fear" in entities_text

    def test_all_entities_have_keyword_label(self, prefilter):
        results = prefilter.prefilter(["The militia attacked the capital."])
        for entity in results[0].entities:
            assert entity.label == "keyword_match"
            assert entity.score == 0.5

    def test_entity_start_end_positions(self, prefilter):
        text = "The conflict started."
        results = prefilter.prefilter([text])
        for entity in results[0].entities:
            assert entity.start >= 0
            assert entity.end > entity.start
            # Verify the entity text matches the slice from the original text
            assert text[entity.start:entity.end].lower() == entity.text.lower()


# ═══════════════════════════════════════════════════════════════════════════
#  KEYWORD FALLBACK — NO ENTITIES IN BLAND TEXT
# ═══════════════════════════════════════════════════════════════════════════


class TestKeywordFallbackNoEntities:
    """Bland text with no conflict keywords should yield zero or very few entities."""

    @pytest.fixture
    def prefilter(self):
        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            return GLiNERPreFilter()

    def test_weather_text(self, prefilter):
        results = prefilter.prefilter(["The weather is nice today."])
        assert results[0].entity_count == 0

    def test_cooking_text(self, prefilter):
        results = prefilter.prefilter(["I made pasta with tomato sauce for dinner."])
        assert results[0].entity_count == 0

    def test_math_text(self, prefilter):
        results = prefilter.prefilter(["The sum of two and three is five."])
        assert results[0].entity_count == 0

    def test_bland_density_is_zero(self, prefilter):
        results = prefilter.prefilter(["A completely ordinary sentence about nothing."])
        assert results[0].entity_density == 0.0

    def test_bland_vs_conflict_density_comparison(self, prefilter):
        results = prefilter.prefilter([
            "The conflict between government and rebel forces led to war.",
            "The cat sat on the mat and looked out the window.",
        ])
        assert results[0].entity_density > results[1].entity_density


# ═══════════════════════════════════════════════════════════════════════════
#  PREFILTER RESULT PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════


class TestPrefilterResultProperties:
    """Test the PrefilterResult dataclass and its computed properties."""

    def test_entity_count_empty(self):
        result = PrefilterResult(chunk_index=0, chunk_text="test")
        assert result.entity_count == 0

    def test_entity_count_with_entities(self):
        entities = [
            PrefilterEntity(text="conflict", label="keyword_match", start=0, end=8, score=0.5),
            PrefilterEntity(text="war", label="keyword_match", start=20, end=23, score=0.5),
            PrefilterEntity(text="peace", label="keyword_match", start=30, end=35, score=0.5),
        ]
        result = PrefilterResult(chunk_index=0, chunk_text="test", entities=entities)
        assert result.entity_count == 3

    def test_entity_count_is_property(self):
        """entity_count should reflect the current length of entities list."""
        result = PrefilterResult(chunk_index=0, chunk_text="test", entities=[])
        assert result.entity_count == 0
        result.entities.append(
            PrefilterEntity(text="x", label="kw", start=0, end=1)
        )
        assert result.entity_count == 1

    def test_default_density_and_priority(self):
        result = PrefilterResult(chunk_index=0, chunk_text="text")
        assert result.entity_density == 0.0
        assert result.priority_score == 0.0


# ═══════════════════════════════════════════════════════════════════════════
#  PRIORITY CHUNK FILTERING
# ═══════════════════════════════════════════════════════════════════════════


class TestPriorityChunksFiltering:
    """get_priority_chunks should filter and sort by priority score."""

    @pytest.fixture
    def prefilter(self):
        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            return GLiNERPreFilter()

    def test_filters_below_threshold(self, prefilter):
        results = [
            PrefilterResult(chunk_index=0, chunk_text="a", priority_score=0.9),
            PrefilterResult(chunk_index=1, chunk_text="b", priority_score=0.1),
            PrefilterResult(chunk_index=2, chunk_text="c", priority_score=0.5),
        ]
        priority = prefilter.get_priority_chunks(results, min_score=0.3)
        assert len(priority) == 2
        # Chunk with score 0.1 should be excluded
        indices = [r.chunk_index for r in priority]
        assert 1 not in indices

    def test_sorted_by_priority_descending(self, prefilter):
        results = [
            PrefilterResult(chunk_index=0, chunk_text="a", priority_score=0.3),
            PrefilterResult(chunk_index=1, chunk_text="b", priority_score=0.9),
            PrefilterResult(chunk_index=2, chunk_text="c", priority_score=0.6),
        ]
        priority = prefilter.get_priority_chunks(results, min_score=0.2)
        assert priority[0].chunk_index == 1  # highest first
        assert priority[1].chunk_index == 2
        assert priority[2].chunk_index == 0

    def test_all_below_threshold_returns_empty(self, prefilter):
        results = [
            PrefilterResult(chunk_index=0, chunk_text="a", priority_score=0.1),
            PrefilterResult(chunk_index=1, chunk_text="b", priority_score=0.2),
        ]
        priority = prefilter.get_priority_chunks(results, min_score=0.5)
        assert priority == []

    def test_empty_results(self, prefilter):
        priority = prefilter.get_priority_chunks([], min_score=0.3)
        assert priority == []

    def test_exact_threshold_included(self, prefilter):
        """Chunks with priority_score exactly equal to min_score should pass."""
        results = [
            PrefilterResult(chunk_index=0, chunk_text="a", priority_score=0.3),
        ]
        priority = prefilter.get_priority_chunks(results, min_score=0.3)
        assert len(priority) == 1

    def test_default_threshold(self, prefilter):
        """Default min_score is 0.3."""
        results = [
            PrefilterResult(chunk_index=0, chunk_text="a", priority_score=0.29),
            PrefilterResult(chunk_index=1, chunk_text="b", priority_score=0.31),
        ]
        priority = prefilter.get_priority_chunks(results)
        assert len(priority) == 1
        assert priority[0].chunk_index == 1


# ═══════════════════════════════════════════════════════════════════════════
#  ENTITY DENSITY CALCULATION
# ═══════════════════════════════════════════════════════════════════════════


class TestEntityDensityCalculation:
    """Verify density = len(entities) / word_count * 100."""

    @pytest.fixture
    def prefilter(self):
        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            return GLiNERPreFilter()

    def test_density_formula(self, prefilter):
        # "conflict war" = 2 words, both are conflict keywords -> 2 entities
        # density = 2 / 2 * 100 = 100.0
        results = prefilter.prefilter(["conflict war"])
        assert results[0].entity_count == 2
        assert results[0].entity_density == pytest.approx(100.0)

    def test_density_with_more_words(self, prefilter):
        # "The conflict was a major war" = 6 words, "conflict" + "war" = 2 entities
        # density = 2 / 6 * 100 = 33.33...
        results = prefilter.prefilter(["The conflict was a major war"])
        assert results[0].entity_count == 2
        assert results[0].entity_density == pytest.approx(2 / 6 * 100)

    def test_density_zero_for_bland_text(self, prefilter):
        results = prefilter.prefilter(["Hello there how are you doing today"])
        assert results[0].entity_density == 0.0

    def test_single_word_text(self, prefilter):
        # "conflict" = 1 word, 1 entity -> density = 100.0
        results = prefilter.prefilter(["conflict"])
        assert results[0].entity_count == 1
        assert results[0].entity_density == pytest.approx(100.0)

    def test_priority_score_normalization(self, prefilter):
        """Priority scores should be normalized: max density chunk gets 1.0."""
        results = prefilter.prefilter([
            "conflict war escalation violence",  # high density
            "The cat sat on the mat",  # zero density
        ])
        # Highest density chunk should have priority_score = 1.0
        assert results[0].priority_score == pytest.approx(1.0)
        # Zero density chunk should have priority_score = 0.0
        assert results[1].priority_score == pytest.approx(0.0)

    def test_single_chunk_gets_max_priority(self, prefilter):
        """With one chunk, that chunk should get priority_score = 1.0."""
        results = prefilter.prefilter(["The government initiated negotiations."])
        assert results[0].priority_score == pytest.approx(1.0)


# ═══════════════════════════════════════════════════════════════════════════
#  GLINER AVAILABILITY FLAG
# ═══════════════════════════════════════════════════════════════════════════


class TestGlinerAvailabilityFlag:
    """GLINER_AVAILABLE should be False when the gliner package is not installed."""

    def test_gliner_available_is_bool(self):
        assert isinstance(GLINER_AVAILABLE, bool)

    def test_gliner_not_installed_in_test_env(self):
        """In our test environment, gliner is typically not installed."""
        # This test documents expected behavior: GLINER_AVAILABLE is False
        # when the optional gliner dependency is not installed.
        # If gliner IS installed, this test is skipped.
        if GLINER_AVAILABLE:
            pytest.skip("GLiNER is installed in this environment")
        assert GLINER_AVAILABLE is False

    def test_prefilter_uses_keyword_when_gliner_unavailable(self):
        """When GLINER_AVAILABLE is False, prefilter falls back to keywords."""
        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            pf = GLiNERPreFilter()
            assert pf._gliner_available is False
            # _init_model should return False
            assert pf._init_model() is False

    def test_env_var_override_disables_gliner(self):
        """Setting GLINER_ENABLED=false disables GLiNER even if available."""
        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            pf = GLiNERPreFilter()
            assert pf._gliner_available is False


# ═══════════════════════════════════════════════════════════════════════════
#  CONFLICT KEYWORDS CONSTANT
# ═══════════════════════════════════════════════════════════════════════════


class TestConflictKeywords:
    """Verify the CONFLICT_KEYWORDS list is properly defined."""

    def test_keywords_is_nonempty_list(self):
        assert isinstance(CONFLICT_KEYWORDS, list)
        assert len(CONFLICT_KEYWORDS) > 0

    def test_keywords_are_regex_strings(self):
        for kw in CONFLICT_KEYWORDS:
            assert isinstance(kw, str)
            # Each keyword should be a valid regex pattern (starts with \b)
            assert r"\b" in kw

    def test_keywords_cover_main_categories(self):
        """Keywords should cover actors, events, conflict terms, emotions, locations."""
        joined = " ".join(CONFLICT_KEYWORDS)
        assert "president" in joined
        assert "attack" in joined
        assert "conflict" in joined
        assert "anger" in joined
        assert "border" in joined


# ═══════════════════════════════════════════════════════════════════════════
#  PREFILTER ENTITY DATACLASS
# ═══════════════════════════════════════════════════════════════════════════


class TestPrefilterEntityDataclass:
    """Test the PrefilterEntity dataclass."""

    def test_creation(self):
        entity = PrefilterEntity(
            text="conflict",
            label="keyword_match",
            start=4,
            end=12,
            score=0.5,
        )
        assert entity.text == "conflict"
        assert entity.label == "keyword_match"
        assert entity.start == 4
        assert entity.end == 12
        assert entity.score == 0.5

    def test_default_score(self):
        entity = PrefilterEntity(text="war", label="kw", start=0, end=3)
        assert entity.score == 0.0

    def test_gliner_style_entity(self):
        """Entity with GLiNER-style label and high score."""
        entity = PrefilterEntity(
            text="United Nations",
            label="conflict actor",
            start=10,
            end=24,
            score=0.92,
        )
        assert entity.label == "conflict actor"
        assert entity.score == 0.92
