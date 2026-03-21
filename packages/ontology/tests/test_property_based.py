"""
Property-based tests for DIALECTICA ontology using Hypothesis.

Tests:
  - Every generated node serializes to JSON and deserializes back identically
  - Every StrEnum value is a valid non-empty string
  - Tier filtering preserves subset relationships (Essential < Standard < Full)
"""
from __future__ import annotations

import json

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from dialectica_ontology.primitives import (
    Actor, Conflict, Event, Issue, Interest, Norm, Process, Outcome,
    Narrative, EmotionalState, TrustState, PowerDynamic, Location, Evidence, Role,
    ConflictNode, NODE_TYPES,
)
from dialectica_ontology.enums import (
    ActorType, ConflictScale, ConflictDomain, ConflictStatus,
    EventType, InterestType, NormType, ProcessType, OutcomeType,
    NarrativeType, PrimaryEmotion, PowerDomain, RoleType,
    GlaslStage, KriesbergPhase, ViolenceType, Intensity,
)
from dialectica_ontology.tiers import OntologyTier, TIER_NODES, TIER_EDGES, get_available_nodes, get_available_edges
from dialectica_ontology.relationships import ConflictRelationship, EdgeType, EDGE_SCHEMA


# ── Hypothesis Strategies ─────────────────────────────────────────────────

safe_text = st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=("L", "N", "Z")))
confidence = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)

actor_strategy = st.builds(
    Actor,
    name=safe_text,
    actor_type=st.sampled_from(list(ActorType)),
    confidence=confidence,
)

conflict_strategy = st.builds(
    Conflict,
    name=safe_text,
    scale=st.sampled_from(list(ConflictScale)),
    domain=st.sampled_from(list(ConflictDomain)),
    status=st.sampled_from(list(ConflictStatus)),
    confidence=confidence,
)

event_strategy = st.builds(
    Event,
    event_type=st.sampled_from(list(EventType)),
    severity=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    confidence=confidence,
)


# ── JSON Round-Trip Tests ─────────────────────────────────────────────────


class TestJsonRoundTrip:
    @given(actor=actor_strategy)
    @settings(max_examples=50)
    def test_actor_roundtrip(self, actor: Actor):
        data = actor.model_dump(mode="json")
        json_str = json.dumps(data)
        recovered = Actor.model_validate(json.loads(json_str))
        assert recovered.name == actor.name
        assert recovered.actor_type == actor.actor_type
        assert recovered.id == actor.id

    @given(conflict=conflict_strategy)
    @settings(max_examples=50)
    def test_conflict_roundtrip(self, conflict: Conflict):
        data = conflict.model_dump(mode="json")
        json_str = json.dumps(data)
        recovered = Conflict.model_validate(json.loads(json_str))
        assert recovered.name == conflict.name
        assert recovered.scale == conflict.scale

    @given(event=event_strategy)
    @settings(max_examples=50)
    def test_event_roundtrip(self, event: Event):
        data = event.model_dump(mode="json")
        json_str = json.dumps(data)
        recovered = Event.model_validate(json.loads(json_str))
        assert recovered.event_type == event.event_type
        assert abs(recovered.severity - event.severity) < 0.001


# ── StrEnum Validity Tests ────────────────────────────────────────────────


class TestStrEnumValidity:
    @pytest.mark.parametrize("enum_cls", [
        ActorType, ConflictScale, ConflictDomain, ConflictStatus,
        EventType, InterestType, NormType, ProcessType, OutcomeType,
        NarrativeType, PrimaryEmotion, PowerDomain, RoleType,
        GlaslStage, KriesbergPhase, ViolenceType, Intensity,
    ])
    def test_enum_values_are_nonempty_strings(self, enum_cls):
        for member in enum_cls:
            assert isinstance(member.value, str)
            assert len(member.value) > 0
            assert member.value == member.value.strip()

    @pytest.mark.parametrize("enum_cls", [
        ActorType, ConflictScale, ConflictDomain, ConflictStatus, EventType,
    ])
    def test_enum_no_none_values(self, enum_cls):
        for member in enum_cls:
            assert member.value is not None


# ── Tier Subset Tests ─────────────────────────────────────────────────────


class TestTierSubsets:
    def test_essential_subset_of_standard(self):
        essential_nodes = get_available_nodes(OntologyTier.ESSENTIAL)
        standard_nodes = get_available_nodes(OntologyTier.STANDARD)
        assert essential_nodes <= standard_nodes, f"Essential nodes not subset of Standard: {essential_nodes - standard_nodes}"

    def test_standard_subset_of_full(self):
        standard_nodes = get_available_nodes(OntologyTier.STANDARD)
        full_nodes = get_available_nodes(OntologyTier.FULL)
        assert standard_nodes <= full_nodes, f"Standard nodes not subset of Full: {standard_nodes - full_nodes}"

    def test_essential_edges_subset_of_standard(self):
        essential_edges = get_available_edges(OntologyTier.ESSENTIAL)
        standard_edges = get_available_edges(OntologyTier.STANDARD)
        assert essential_edges <= standard_edges

    def test_standard_edges_subset_of_full(self):
        standard_edges = get_available_edges(OntologyTier.STANDARD)
        full_edges = get_available_edges(OntologyTier.FULL)
        assert standard_edges <= full_edges

    def test_full_tier_contains_all_node_types(self):
        full_nodes = get_available_nodes(OntologyTier.FULL)
        all_nodes = set(NODE_TYPES.keys())
        assert all_nodes == full_nodes


# ── Relationship Constraint Tests ─────────────────────────────────────────


class TestRelationshipConstraints:
    def test_all_edge_types_have_schema(self):
        for edge_type in EdgeType:
            assert edge_type.value in EDGE_SCHEMA, f"EdgeType {edge_type} missing from EDGE_SCHEMA"

    def test_edge_schema_has_valid_labels(self):
        valid_labels = {type(n).__name__ for n in NODE_TYPES}
        for edge_type, schema in EDGE_SCHEMA.items():
            src = schema.get("source_label", "")
            tgt = schema.get("target_label", "")
            if src:
                assert src in valid_labels, f"{edge_type} source_label '{src}' not a valid node type"
            if tgt:
                assert tgt in valid_labels, f"{edge_type} target_label '{tgt}' not a valid node type"
