"""Tests for dialectica_ontology.primitives — All 15 node type Pydantic models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from dialectica_ontology.primitives import (
    ConflictNode,
    Actor,
    Conflict,
    Event,
    Issue,
    Interest,
    Norm,
    Process,
    Outcome,
    Narrative,
    EmotionalState,
    TrustState,
    PowerDynamic,
    Location,
    Evidence,
    Role,
    NODE_TYPES,
)
from dialectica_ontology.enums import (
    ActorType,
    ConflictDomain,
    ConflictScale,
    ConflictStatus,
    GlaslLevel,
    EventType,
    InterestType,
    NormType,
    ProcessType,
    ResolutionApproach,
    ProcessStatus,
    OutcomeType,
    NarrativeType,
    PrimaryEmotion,
    EmotionIntensity,
    PowerDomain,
    PowerDirection,
    LocationType,
    EvidenceType,
    RoleType,
)


# ─── Registry ───────────────────────────────────────────────────────────────

def test_node_types_registry():
    assert len(NODE_TYPES) == 15
    expected = {
        "Actor", "Conflict", "Event", "Issue", "Interest", "Norm",
        "Process", "Outcome", "Narrative", "EmotionalState", "TrustState",
        "PowerDynamic", "Location", "Evidence", "Role",
    }
    assert set(NODE_TYPES.keys()) == expected


# ─── ConflictNode base ──────────────────────────────────────────────────────

def test_conflict_node_defaults():
    node = Actor(name="Test", actor_type=ActorType.PERSON)
    assert node.id  # ULID generated
    assert len(node.id) > 0
    assert node.confidence == 1.0
    assert node.metadata == {}
    assert node.source_text is None
    assert node.extraction_method is None


def test_conflict_node_confidence_range():
    with pytest.raises(ValidationError):
        Actor(name="Test", actor_type=ActorType.PERSON, confidence=1.5)
    with pytest.raises(ValidationError):
        Actor(name="Test", actor_type=ActorType.PERSON, confidence=-0.1)


def test_conflict_node_embedding_validation():
    # Valid 128-dim
    a = Actor(name="Test", actor_type=ActorType.PERSON, embedding=[0.0] * 128)
    assert len(a.embedding) == 128
    # Valid 768-dim
    a = Actor(name="Test", actor_type=ActorType.PERSON, embedding=[0.0] * 768)
    assert len(a.embedding) == 768
    # Invalid dim
    with pytest.raises(ValidationError):
        Actor(name="Test", actor_type=ActorType.PERSON, embedding=[0.0] * 50)


# ─── 1. Actor ───────────────────────────────────────────────────────────────

def test_actor_creation():
    a = Actor(name="Iran", actor_type=ActorType.STATE, iso_code="IRN")
    assert a.label == "Actor"
    assert a.name == "Iran"
    assert a.actor_type == ActorType.STATE
    assert a.iso_code == "IRN"


def test_actor_multi_label_props():
    a = Actor(
        name="John Doe",
        actor_type=ActorType.PERSON,
        role_title="Mediator",
        gender="male",
        age=45,
    )
    assert a.role_title == "Mediator"
    assert a.age == 45


def test_actor_organization_props():
    a = Actor(
        name="UN",
        actor_type=ActorType.ORGANIZATION,
        org_type="IGO",
        sector="international",
    )
    assert a.org_type == "IGO"


def test_actor_serialization():
    a = Actor(name="Test", actor_type=ActorType.PERSON)
    d = a.model_dump()
    assert d["name"] == "Test"
    assert d["actor_type"] == "person"
    assert d["label"] == "Actor"


# ─── 2. Conflict ────────────────────────────────────────────────────────────

def test_conflict_creation():
    c = Conflict(
        name="JCPOA Dispute",
        scale=ConflictScale.MACRO,
        domain=ConflictDomain.POLITICAL,
        status=ConflictStatus.ACTIVE,
    )
    assert c.label == "Conflict"
    assert c.name == "JCPOA Dispute"


def test_conflict_glasl_level_derivation():
    c = Conflict(
        name="Test",
        scale=ConflictScale.MICRO,
        domain=ConflictDomain.WORKPLACE,
        status=ConflictStatus.ACTIVE,
        glasl_stage=7,
    )
    assert c.glasl_level == GlaslLevel.LOSE_LOSE

    c2 = Conflict(
        name="Test",
        scale=ConflictScale.MICRO,
        domain=ConflictDomain.WORKPLACE,
        status=ConflictStatus.ACTIVE,
        glasl_stage=2,
    )
    assert c2.glasl_level == GlaslLevel.WIN_WIN

    c3 = Conflict(
        name="Test",
        scale=ConflictScale.MICRO,
        domain=ConflictDomain.WORKPLACE,
        status=ConflictStatus.ACTIVE,
        glasl_stage=5,
    )
    assert c3.glasl_level == GlaslLevel.WIN_LOSE


def test_conflict_glasl_stage_range():
    with pytest.raises(ValidationError):
        Conflict(
            name="Test", scale=ConflictScale.MICRO,
            domain=ConflictDomain.WORKPLACE, status=ConflictStatus.ACTIVE,
            glasl_stage=0,
        )
    with pytest.raises(ValidationError):
        Conflict(
            name="Test", scale=ConflictScale.MICRO,
            domain=ConflictDomain.WORKPLACE, status=ConflictStatus.ACTIVE,
            glasl_stage=10,
        )


# ─── 3. Event ───────────────────────────────────────────────────────────────

def test_event_creation():
    e = Event(
        event_type=EventType.ASSAULT,
        severity=0.8,
        occurred_at=datetime(2024, 1, 15),
    )
    assert e.label == "Event"
    assert e.severity == 0.8


def test_event_severity_range():
    with pytest.raises(ValidationError):
        Event(event_type=EventType.AGREE, severity=1.5, occurred_at=datetime.now())


# ─── 4. Issue ───────────────────────────────────────────────────────────────

def test_issue_creation():
    i = Issue(name="Nuclear Enrichment", issue_type=InterestType.SUBSTANTIVE, salience=0.9)
    assert i.label == "Issue"
    assert i.salience == 0.9


# ─── 5. Interest ────────────────────────────────────────────────────────────

def test_interest_creation():
    i = Interest(
        description="Security guarantee",
        interest_type=InterestType.SUBSTANTIVE,
        priority=1,
        stated=True,
        batna_strength="strong",
    )
    assert i.label == "Interest"
    assert i.priority == 1


def test_interest_priority_range():
    with pytest.raises(ValidationError):
        Interest(description="Test", interest_type=InterestType.SUBSTANTIVE, priority=0)
    with pytest.raises(ValidationError):
        Interest(description="Test", interest_type=InterestType.SUBSTANTIVE, priority=6)


# ─── 6. Norm ────────────────────────────────────────────────────────────────

def test_norm_creation():
    n = Norm(name="NPT", norm_type=NormType.TREATY, enforceability="binding")
    assert n.label == "Norm"
    assert n.enforceability == "binding"


# ─── 7. Process ─────────────────────────────────────────────────────────────

def test_process_creation():
    p = Process(
        process_type=ProcessType.NEGOTIATION,
        resolution_approach=ResolutionApproach.INTEREST_BASED,
        status=ProcessStatus.ACTIVE,
    )
    assert p.label == "Process"


# ─── 8. Outcome ─────────────────────────────────────────────────────────────

def test_outcome_creation():
    o = Outcome(
        outcome_type=OutcomeType.AGREEMENT,
        satisfaction_a=0.7,
        satisfaction_b=0.6,
        joint_value=0.8,
    )
    assert o.label == "Outcome"
    assert o.joint_value == 0.8


# ─── 9. Narrative ───────────────────────────────────────────────────────────

def test_narrative_creation():
    n = Narrative(
        content="Iran seeks nuclear weapons",
        narrative_type=NarrativeType.DOMINANT,
        coherence=0.8,
    )
    assert n.label == "Narrative"


# ─── 10. EmotionalState ─────────────────────────────────────────────────────

def test_emotional_state_creation():
    es = EmotionalState(
        primary_emotion=PrimaryEmotion.ANGER,
        intensity=EmotionIntensity.HIGH,
        valence=-0.8,
        arousal=0.9,
    )
    assert es.label == "EmotionalState"
    assert es.valence == -0.8


def test_emotional_state_valence_range():
    with pytest.raises(ValidationError):
        EmotionalState(
            primary_emotion=PrimaryEmotion.JOY,
            intensity=EmotionIntensity.LOW,
            valence=-1.5,
        )


# ─── 11. TrustState ─────────────────────────────────────────────────────────

def test_trust_state_creation():
    ts = TrustState(
        perceived_ability=0.7,
        perceived_benevolence=0.3,
        perceived_integrity=0.2,
        overall_trust=0.35,
        trust_basis="calculus",
    )
    assert ts.label == "TrustState"
    assert ts.overall_trust == 0.35


# ─── 12. PowerDynamic ───────────────────────────────────────────────────────

def test_power_dynamic_creation():
    pd = PowerDynamic(
        power_domain=PowerDomain.ECONOMIC,
        magnitude=0.8,
        direction=PowerDirection.A_OVER_B,
    )
    assert pd.label == "PowerDynamic"
    assert pd.magnitude == 0.8


# ─── 13. Location ───────────────────────────────────────────────────────────

def test_location_creation():
    loc = Location(
        name="Tehran",
        location_type=LocationType.CITY,
        latitude=35.6892,
        longitude=51.3890,
        country_code="IRN",
    )
    assert loc.label == "Location"
    assert loc.latitude == 35.6892


def test_location_country_code_validation():
    with pytest.raises(ValidationError):
        Location(name="Test", location_type=LocationType.CITY, country_code="US")


# ─── 14. Evidence ───────────────────────────────────────────────────────────

def test_evidence_creation():
    e = Evidence(
        evidence_type=EvidenceType.DOCUMENT,
        description="IAEA report",
        reliability=0.95,
    )
    assert e.label == "Evidence"


# ─── 15. Role ───────────────────────────────────────────────────────────────

def test_role_creation():
    r = Role(role_type=RoleType.MEDIATOR, actor_id="actor_123", context_id="conflict_456")
    assert r.label == "Role"
    assert r.role_type == RoleType.MEDIATOR


# ─── Serialization / Deserialization ─────────────────────────────────────────

def test_all_node_types_serializable():
    """Ensure all 15 node types can be serialized to dict and back."""
    samples = {
        "Actor": Actor(name="Test", actor_type=ActorType.PERSON),
        "Conflict": Conflict(name="Test", scale=ConflictScale.MICRO, domain=ConflictDomain.WORKPLACE, status=ConflictStatus.ACTIVE),
        "Event": Event(event_type=EventType.AGREE, severity=0.5, occurred_at=datetime.now()),
        "Issue": Issue(name="Test", issue_type=InterestType.SUBSTANTIVE),
        "Interest": Interest(description="Test", interest_type=InterestType.SUBSTANTIVE),
        "Norm": Norm(name="Test", norm_type=NormType.CONTRACT),
        "Process": Process(process_type=ProcessType.NEGOTIATION, resolution_approach=ResolutionApproach.INTEREST_BASED, status=ProcessStatus.ACTIVE),
        "Outcome": Outcome(outcome_type=OutcomeType.AGREEMENT),
        "Narrative": Narrative(content="Test", narrative_type=NarrativeType.DOMINANT),
        "EmotionalState": EmotionalState(primary_emotion=PrimaryEmotion.JOY, intensity=EmotionIntensity.LOW),
        "TrustState": TrustState(perceived_ability=0.5, perceived_benevolence=0.5, perceived_integrity=0.5, overall_trust=0.5),
        "PowerDynamic": PowerDynamic(power_domain=PowerDomain.COERCIVE, magnitude=0.5, direction=PowerDirection.SYMMETRIC),
        "Location": Location(name="Test", location_type=LocationType.CITY),
        "Evidence": Evidence(evidence_type=EvidenceType.DOCUMENT, description="Test"),
        "Role": Role(role_type=RoleType.MEDIATOR),
    }
    assert len(samples) == 15
    for name, node in samples.items():
        d = node.model_dump()
        assert "id" in d
        assert d["label"] == name
        # Round-trip
        cls = NODE_TYPES[name]
        restored = cls.model_validate(d)
        assert restored.id == node.id
