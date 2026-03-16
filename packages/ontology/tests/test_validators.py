"""Tests for dialectica_ontology.validators — Conflict Grammar constraints."""

from datetime import datetime

from dialectica_ontology.primitives import Actor, Conflict, Event
from dialectica_ontology.relationships import ConflictRelationship, EdgeType
from dialectica_ontology.enums import (
    ActorType,
    ConflictDomain,
    ConflictScale,
    ConflictStatus,
    EventType,
)
from dialectica_ontology.tiers import OntologyTier
from dialectica_ontology.validators import (
    validate_relationship_types,
    validate_subgraph,
    validate_temporal_consistency,
    validate_tier_compliance,
)


def test_validate_valid_subgraph():
    a = Actor(name="Test", actor_type=ActorType.PERSON)
    c = Conflict(
        name="Test Conflict",
        scale=ConflictScale.MICRO,
        domain=ConflictDomain.WORKPLACE,
        status=ConflictStatus.ACTIVE,
    )
    r = ConflictRelationship(
        type=EdgeType.PARTY_TO,
        source_id=a.id,
        target_id=c.id,
        source_label="Actor",
        target_label="Conflict",
    )
    errors = validate_subgraph([a, c], [r])
    assert errors == []


def test_validate_missing_node():
    r = ConflictRelationship(
        type=EdgeType.PARTY_TO,
        source_id="missing_1",
        target_id="missing_2",
    )
    errors = validate_subgraph([], [r])
    assert len(errors) == 2
    assert "source_id" in errors[0]
    assert "target_id" in errors[1]


def test_validate_temporal_consistency_valid():
    r = ConflictRelationship(
        type=EdgeType.CAUSED,
        source_id="event_1",
        target_id="event_2",
    )
    timestamps = {
        "event_1": datetime(2024, 1, 1),
        "event_2": datetime(2024, 1, 15),
    }
    errors = validate_temporal_consistency([r], timestamps)
    assert errors == []


def test_validate_temporal_consistency_invalid():
    r = ConflictRelationship(
        type=EdgeType.CAUSED,
        source_id="event_1",
        target_id="event_2",
    )
    timestamps = {
        "event_1": datetime(2024, 6, 1),
        "event_2": datetime(2024, 1, 1),
    }
    errors = validate_temporal_consistency([r], timestamps)
    assert len(errors) == 1
    assert "cause must precede effect" in errors[0]


def test_validate_tier_compliance_essential():
    a = Actor(name="Test", actor_type=ActorType.PERSON)
    c = Conflict(
        name="Test",
        scale=ConflictScale.MICRO,
        domain=ConflictDomain.WORKPLACE,
        status=ConflictStatus.ACTIVE,
    )
    r = ConflictRelationship(
        type=EdgeType.PARTY_TO,
        source_id=a.id,
        target_id=c.id,
    )
    errors = validate_tier_compliance([a, c], [r], OntologyTier.ESSENTIAL)
    assert errors == []


def test_validate_tier_compliance_violation():
    from dialectica_ontology.primitives import EmotionalState
    from dialectica_ontology.enums import PrimaryEmotion, EmotionIntensity

    es = EmotionalState(
        primary_emotion=PrimaryEmotion.ANGER,
        intensity=EmotionIntensity.HIGH,
    )
    # EmotionalState is only in FULL tier
    errors = validate_tier_compliance([es], [], OntologyTier.ESSENTIAL)
    assert len(errors) == 1
    assert "EmotionalState" in errors[0]
