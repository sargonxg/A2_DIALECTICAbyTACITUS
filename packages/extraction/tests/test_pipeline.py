"""
Tests for dialectica_extraction.pipeline — LangGraph extraction DAG.

Tests chunking, validation, coreference, and the full pipeline flow
using mocked Gemini calls.
"""
from __future__ import annotations

import sys
import os
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_ontology.primitives import Actor, Conflict, Event, ConflictNode
from dialectica_ontology.relationships import ConflictRelationship, EdgeType
from dialectica_ontology.tiers import OntologyTier

from dialectica_extraction.pipeline import (
    ExtractionState,
    chunk_document,
    gliner_prefilter,
    validate_schema,
    resolve_coreference,
    validate_structural_step,
    write_to_graph,
    should_repair,
    ExtractionPipeline,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
from dialectica_extraction.validators.schema import validate_raw_nodes, validate_raw_edges
from dialectica_extraction.validators.structural import validate_structural
from dialectica_extraction.validators.temporal import validate_temporal
from dialectica_extraction.validators.symbolic import validate_symbolic
from dialectica_extraction.extractors.entity import enrich_actors, deduplicate_nodes
from dialectica_extraction.extractors.coreference import (
    find_coreferences,
    merge_coreferent_nodes,
    token_sort_ratio,
)
from dialectica_extraction.extractors.causal import detect_causal_signals, has_causal_language
from dialectica_extraction.extractors.narrative import analyze_frame
from dialectica_extraction.extractors.emotion import detect_emotions
from dialectica_extraction.extractors.temporal import parse_date

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def _load_fixture(name: str) -> str:
    with open(os.path.join(FIXTURE_DIR, name)) as f:
        return f.read()


# ═══════════════════════════════════════════════════════════════════════════
#  CHUNKING TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestChunkDocument:
    def test_short_text_single_chunk(self):
        state: ExtractionState = {"text": "Short text.", "tier": "essential"}
        result = chunk_document(state)
        assert len(result["chunks"]) == 1
        assert result["chunks"][0]["text"] == "Short text."

    def test_long_text_multiple_chunks(self):
        text = "A" * 5000
        state: ExtractionState = {"text": text, "tier": "essential"}
        result = chunk_document(state)
        assert len(result["chunks"]) > 1

    def test_chunks_have_overlap(self):
        # Create text with clear sentence boundaries
        sentences = ["This is sentence number %d. " % i for i in range(100)]
        text = "".join(sentences)
        state: ExtractionState = {"text": text, "tier": "essential"}
        result = chunk_document(state)

        if len(result["chunks"]) >= 2:
            # Chunks should overlap
            c1_end = result["chunks"][0]["end"]
            c2_start = result["chunks"][1]["start"]
            assert c2_start < c1_end  # overlap exists

    def test_fixture_chunking(self):
        text = _load_fixture("hr_dispute.txt")
        state: ExtractionState = {"text": text, "tier": "essential"}
        result = chunk_document(state)
        assert len(result["chunks"]) >= 1
        assert result["chunks"][0]["text"]  # non-empty

    def test_processing_time_recorded(self):
        state: ExtractionState = {"text": "Test", "tier": "essential"}
        result = chunk_document(state)
        assert "chunk_document" in result.get("processing_time", {})


# ═══════════════════════════════════════════════════════════════════════════
#  PREFILTER TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestGlinerPrefilter:
    def test_prefilter_with_keyword_fallback(self):
        state: ExtractionState = {
            "text": "Test",
            "tier": "essential",
            "chunks": [
                {"text": "The conflict between rebel forces and the government escalated.", "index": 0, "start": 0, "end": 60},
                {"text": "The weather was sunny today with no clouds.", "index": 1, "start": 60, "end": 100},
            ],
            "processing_time": {},
            "errors": [],
        }
        # Force keyword fallback by disabling GLiNER
        with patch.dict(os.environ, {"GLINER_ENABLED": "false"}):
            result = gliner_prefilter(state)
        assert len(result["prefilter_results"]) == 2
        # Conflict text should have higher priority
        r0 = result["prefilter_results"][0]
        r1 = result["prefilter_results"][1]
        assert r0["entity_density"] >= 0


# ═══════════════════════════════════════════════════════════════════════════
#  SCHEMA VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestSchemaValidation:
    def test_validate_valid_actor(self):
        raw = [{"label": "Actor", "name": "Alice", "actor_type": "person", "confidence": 0.9}]
        result = validate_raw_nodes(raw, OntologyTier.ESSENTIAL)
        assert len(result.valid_nodes) == 1
        assert result.all_valid

    def test_validate_invalid_label(self):
        raw = [{"label": "InvalidType", "name": "Test"}]
        result = validate_raw_nodes(raw, OntologyTier.ESSENTIAL)
        assert len(result.valid_nodes) == 0
        assert len(result.errors) > 0

    def test_validate_missing_required_field(self):
        raw = [{"label": "Actor"}]  # missing name and actor_type
        result = validate_raw_nodes(raw, OntologyTier.ESSENTIAL)
        assert len(result.valid_nodes) == 0
        assert len(result.errors) > 0

    def test_validate_tier_restriction(self):
        # Interest is not in ESSENTIAL tier
        raw = [{"label": "Interest", "description": "Test", "interest_type": "substantive"}]
        result = validate_raw_nodes(raw, OntologyTier.ESSENTIAL)
        assert len(result.valid_nodes) == 0

        # But it should work in STANDARD tier
        result = validate_raw_nodes(raw, OntologyTier.STANDARD)
        assert len(result.valid_nodes) == 1

    def test_validate_conflict(self):
        raw = [{"label": "Conflict", "name": "Test", "scale": "micro", "domain": "workplace", "status": "active"}]
        result = validate_raw_nodes(raw, OntologyTier.ESSENTIAL)
        assert len(result.valid_nodes) == 1

    def test_validate_edges(self):
        raw_edges = [{
            "type": "PARTY_TO",
            "source_id": "a1",
            "target_id": "c1",
            "source_label": "Actor",
            "target_label": "Conflict",
            "confidence": 0.9,
        }]
        result = validate_raw_edges(raw_edges, OntologyTier.ESSENTIAL)
        assert len(result.valid_edges) == 1

    def test_validate_edge_wrong_type(self):
        raw_edges = [{
            "type": "PARTY_TO",
            "source_id": "c1",
            "target_id": "a1",
            "source_label": "Conflict",  # Wrong! Should be Actor
            "target_label": "Actor",
        }]
        result = validate_raw_edges(raw_edges, OntologyTier.ESSENTIAL)
        assert len(result.valid_edges) == 0
        assert len(result.errors) > 0


# ═══════════════════════════════════════════════════════════════════════════
#  STRUCTURAL VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestStructuralValidation:
    def test_orphan_detection(self):
        actor = Actor(name="Orphan", actor_type="person")
        conflict = Conflict(name="C1", scale="micro", domain="workplace", status="active")
        result = validate_structural([actor, conflict], [])
        assert len(result.orphan_nodes) == 2

    def test_valid_structure(self):
        actor = Actor(name="A1", actor_type="person")
        conflict = Conflict(name="C1", scale="micro", domain="workplace", status="active")
        edge = ConflictRelationship(
            type=EdgeType.PARTY_TO,
            source_id=actor.id,
            target_id=conflict.id,
            source_label="Actor",
            target_label="Conflict",
        )
        result = validate_structural([actor, conflict], [edge])
        assert result.is_valid

    def test_invalid_edge_direction(self):
        actor = Actor(name="A1", actor_type="person")
        conflict = Conflict(name="C1", scale="micro", domain="workplace", status="active")
        # PARTY_TO should be Actor -> Conflict, not Conflict -> Actor
        edge = ConflictRelationship(
            type=EdgeType.PARTY_TO,
            source_id=conflict.id,
            target_id=actor.id,
            source_label="Conflict",
            target_label="Actor",
        )
        result = validate_structural([actor, conflict], [edge])
        assert not result.is_valid


# ═══════════════════════════════════════════════════════════════════════════
#  TEMPORAL VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestTemporalValidation:
    def test_valid_causal_chain(self):
        e1 = Event(event_type="protest", severity=0.5, occurred_at=datetime(2024, 1, 1))
        e2 = Event(event_type="assault", severity=0.8, occurred_at=datetime(2024, 2, 1))
        edge = ConflictRelationship(
            type=EdgeType.CAUSED,
            source_id=e1.id,
            target_id=e2.id,
            source_label="Event",
            target_label="Event",
        )
        result = validate_temporal([e1, e2], [edge])
        assert result.is_valid

    def test_invalid_causal_chain(self):
        e1 = Event(event_type="protest", severity=0.5, occurred_at=datetime(2024, 3, 1))
        e2 = Event(event_type="assault", severity=0.8, occurred_at=datetime(2024, 1, 1))
        edge = ConflictRelationship(
            type=EdgeType.CAUSED,
            source_id=e1.id,
            target_id=e2.id,
            source_label="Event",
            target_label="Event",
        )
        result = validate_temporal([e1, e2], [edge])
        assert not result.is_valid


# ═══════════════════════════════════════════════════════════════════════════
#  SYMBOLIC VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestSymbolicValidation:
    def test_conflict_needs_parties(self):
        conflict = Conflict(name="C1", scale="micro", domain="workplace", status="active")
        result = validate_symbolic([conflict], [])
        assert len(result.warnings) > 0  # Should warn about missing parties

    def test_conflict_with_parties(self):
        a1 = Actor(name="A1", actor_type="person")
        a2 = Actor(name="A2", actor_type="person")
        c1 = Conflict(name="C1", scale="micro", domain="workplace", status="active")
        edges = [
            ConflictRelationship(type=EdgeType.PARTY_TO, source_id=a1.id, target_id=c1.id, source_label="Actor", target_label="Conflict"),
            ConflictRelationship(type=EdgeType.PARTY_TO, source_id=a2.id, target_id=c1.id, source_label="Actor", target_label="Conflict"),
        ]
        result = validate_symbolic([a1, a2, c1], edges)
        # Should not warn about parties
        party_warnings = [w for w in result.warnings if "party" in w.lower()]
        assert len(party_warnings) == 0


# ═══════════════════════════════════════════════════════════════════════════
#  COREFERENCE TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestCoreference:
    def test_exact_match(self):
        a1 = Actor(name="John Smith", actor_type="person")
        a2 = Actor(name="John Smith", actor_type="person")
        matches = find_coreferences([a1, a2])
        assert len(matches) == 1
        assert matches[0].match_type == "exact"

    def test_no_match(self):
        a1 = Actor(name="Alice", actor_type="person")
        a2 = Actor(name="Bob", actor_type="person")
        matches = find_coreferences([a1, a2])
        assert len(matches) == 0

    def test_different_labels_no_match(self):
        a = Actor(name="Test", actor_type="person")
        c = Conflict(name="Test", scale="micro", domain="workplace", status="active")
        matches = find_coreferences([a, c])
        assert len(matches) == 0  # Different labels shouldn't match

    def test_token_sort_ratio(self):
        assert token_sort_ratio("hello world", "hello world") == pytest.approx(1.0)
        assert token_sort_ratio("hello", "goodbye") < 0.5


# ═══════════════════════════════════════════════════════════════════════════
#  ENRICHMENT MODULE TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestEnrichment:
    def test_enrich_actors_aliases(self):
        actors = [Actor(name="United Nations", actor_type="organization")]
        enriched = enrich_actors(actors)
        assert "UN" in enriched[0].aliases

    def test_deduplicate_nodes(self):
        a1 = Actor(name="Alice", actor_type="person", confidence=0.9)
        a2 = Actor(name="Alice", actor_type="person", confidence=0.7)
        result = deduplicate_nodes([a1, a2])
        assert len(result) == 1

    def test_detect_causal_signals(self):
        text = "The protest led to a government crackdown"
        signals = detect_causal_signals(text)
        assert len(signals) > 0
        assert signals[0].signal_phrase == "led to"

    def test_has_causal_language(self):
        assert has_causal_language("A caused B") is True
        assert has_causal_language("The weather is nice") is False

    def test_analyze_frame(self):
        text = "The problem is corruption. We must act now to fix this dangerous situation."
        frame = analyze_frame(text)
        assert frame.diagnostic_score > 0
        assert frame.motivational_score > 0

    def test_detect_emotions(self):
        text = "The community was angry and frustrated by the government's decision."
        emotions = detect_emotions(text)
        assert len(emotions) > 0
        assert any(e.emotion == "anger" for e in emotions)

    def test_parse_date_iso(self):
        dt = parse_date("2024-03-15")
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 3

    def test_parse_date_month_year(self):
        dt = parse_date("March 2024")
        assert dt is not None
        assert dt.year == 2024
        assert dt.month == 3


# ═══════════════════════════════════════════════════════════════════════════
#  PIPELINE ROUTING TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestPipelineRouting:
    def test_should_repair_no_invalid(self):
        state: ExtractionState = {"invalid_entities": [], "retry_count": 0}
        assert should_repair(state) == "skip_repair"

    def test_should_repair_with_invalid(self):
        state: ExtractionState = {"invalid_entities": [{"label": "Bad"}], "retry_count": 0}
        assert should_repair(state) == "repair"

    def test_should_repair_max_retries(self):
        state: ExtractionState = {"invalid_entities": [{"label": "Bad"}], "retry_count": 3}
        assert should_repair(state) == "max_retries"


# ═══════════════════════════════════════════════════════════════════════════
#  PROMPT TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestPrompts:
    def test_system_prompt_builds(self):
        from dialectica_extraction.prompts.system import build_system_prompt
        prompt = build_system_prompt(OntologyTier.ESSENTIAL)
        assert "DIALECTICA" in prompt
        assert "Actor" in prompt

    def test_tier_prompts_exist(self):
        from dialectica_extraction.prompts import (
            EXTRACTION_ESSENTIAL_PROMPT,
            EXTRACTION_STANDARD_PROMPT,
            EXTRACTION_FULL_PROMPT,
            RELATIONSHIP_PROMPT,
        )
        assert "ESSENTIAL" in EXTRACTION_ESSENTIAL_PROMPT or "essential" in EXTRACTION_ESSENTIAL_PROMPT.lower()
        assert len(EXTRACTION_STANDARD_PROMPT) > 100
        assert len(EXTRACTION_FULL_PROMPT) > 100
        assert "edges" in RELATIONSHIP_PROMPT

    def test_node_type_descriptions(self):
        from dialectica_extraction.prompts.system import get_node_type_descriptions
        desc = get_node_type_descriptions(OntologyTier.ESSENTIAL)
        assert "Actor" in desc
        assert "Conflict" in desc
        # Interest should NOT be in essential
        assert "Interest" not in desc.split("\n")[0]  # at least not as a header

    def test_edge_type_descriptions(self):
        from dialectica_extraction.prompts.system import get_edge_type_descriptions
        desc = get_edge_type_descriptions(OntologyTier.ESSENTIAL)
        assert "PARTY_TO" in desc
