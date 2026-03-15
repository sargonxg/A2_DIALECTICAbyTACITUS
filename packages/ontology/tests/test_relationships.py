"""Tests for dialectica_ontology.relationships — All 20 edge type models."""

from dialectica_ontology.relationships import (
    ConflictRelationship,
    EdgeType,
    EDGE_SCHEMA,
    validate_relationship,
)


def test_edge_type_count():
    assert len(EdgeType) == 20


def test_edge_type_values():
    expected = {
        "PARTY_TO", "PARTICIPATES_IN", "HAS_INTEREST", "PART_OF", "CAUSED",
        "AT_LOCATION", "WITHIN", "ALLIED_WITH", "OPPOSED_TO", "HAS_POWER_OVER",
        "MEMBER_OF", "GOVERNED_BY", "VIOLATES", "RESOLVED_THROUGH", "PRODUCES",
        "EXPERIENCES", "TRUSTS", "PROMOTES", "ABOUT", "EVIDENCED_BY",
    }
    assert {e.value for e in EdgeType} == expected


def test_edge_schema_count():
    assert len(EDGE_SCHEMA) == 20


def test_edge_schema_has_all_types():
    for et in EdgeType:
        assert et in EDGE_SCHEMA, f"Missing schema for {et}"


def test_relationship_creation():
    r = ConflictRelationship(
        type=EdgeType.PARTY_TO,
        source_id="actor_1",
        target_id="conflict_1",
        source_label="Actor",
        target_label="Conflict",
    )
    assert r.id  # ULID generated
    assert r.type == EdgeType.PARTY_TO
    assert r.weight == 1.0
    assert r.confidence == 1.0


def test_relationship_serialization():
    r = ConflictRelationship(
        type=EdgeType.CAUSED,
        source_id="event_1",
        target_id="event_2",
    )
    d = r.model_dump()
    assert d["type"] == "CAUSED"
    assert d["source_id"] == "event_1"


def test_validate_valid_relationship():
    r = ConflictRelationship(
        type=EdgeType.PARTY_TO,
        source_id="a1",
        target_id="c1",
        source_label="Actor",
        target_label="Conflict",
    )
    errors = validate_relationship(r)
    assert errors == []


def test_validate_invalid_source():
    r = ConflictRelationship(
        type=EdgeType.PARTY_TO,
        source_id="e1",
        target_id="c1",
        source_label="Event",
        target_label="Conflict",
    )
    errors = validate_relationship(r)
    assert len(errors) == 1
    assert "source must be" in errors[0]


def test_validate_invalid_target():
    r = ConflictRelationship(
        type=EdgeType.PARTY_TO,
        source_id="a1",
        target_id="e1",
        source_label="Actor",
        target_label="Event",
    )
    errors = validate_relationship(r)
    assert len(errors) == 1
    assert "target must be" in errors[0]


def test_validate_no_labels_passes():
    """Validation should pass when labels are not provided (can't check)."""
    r = ConflictRelationship(
        type=EdgeType.PARTY_TO,
        source_id="a1",
        target_id="c1",
    )
    errors = validate_relationship(r)
    assert errors == []


def test_all_edge_schemas_valid_structure():
    for edge_type, schema in EDGE_SCHEMA.items():
        assert "source" in schema, f"{edge_type} missing source"
        assert "target" in schema, f"{edge_type} missing target"
        assert "required" in schema, f"{edge_type} missing required"
        assert "optional" in schema, f"{edge_type} missing optional"
        assert isinstance(schema["source"], list)
        assert isinstance(schema["target"], list)


def test_edge_schema_source_targets():
    """Verify specific edge source/target constraints from ontology.py."""
    assert EDGE_SCHEMA[EdgeType.PARTY_TO]["source"] == ["Actor"]
    assert EDGE_SCHEMA[EdgeType.PARTY_TO]["target"] == ["Conflict"]
    assert EDGE_SCHEMA[EdgeType.CAUSED]["source"] == ["Event"]
    assert EDGE_SCHEMA[EdgeType.CAUSED]["target"] == ["Event"]
    assert EDGE_SCHEMA[EdgeType.WITHIN]["source"] == ["Location"]
    assert EDGE_SCHEMA[EdgeType.WITHIN]["target"] == ["Location"]
    assert EDGE_SCHEMA[EdgeType.GOVERNED_BY]["source"] == ["Conflict"]
    assert EDGE_SCHEMA[EdgeType.GOVERNED_BY]["target"] == ["Norm"]
    assert EDGE_SCHEMA[EdgeType.PRODUCES]["source"] == ["Process"]
    assert EDGE_SCHEMA[EdgeType.PRODUCES]["target"] == ["Outcome"]
    assert EDGE_SCHEMA[EdgeType.ABOUT]["source"] == ["Narrative"]
    assert EDGE_SCHEMA[EdgeType.ABOUT]["target"] == ["Conflict"]
