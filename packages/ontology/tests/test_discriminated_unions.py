"""
Tests for Pydantic discriminated union dispatch across all 15 node types.
"""

from __future__ import annotations

from datetime import UTC, datetime

from dialectica_ontology.primitives import (
    NODE_TYPES,
    Actor,
    Conflict,
    Event,
)


class TestDiscriminatedUnionDispatch:
    """Test that each node type constructs with its correct label."""

    def test_actor_label(self):
        a = Actor(name="Test", actor_type="person")
        assert a.label == "Actor"

    def test_conflict_label(self):
        c = Conflict(name="Test", scale="micro", domain="workplace", status="active")
        assert c.label == "Conflict"

    def test_event_label(self):
        e = Event(event_type="protest", severity=0.5, occurred_at=datetime.now(UTC))
        assert e.label == "Event"

    def test_all_15_node_types_have_labels(self):
        # Registry now contains 18 types: the original 15 plus
        # ReasoningTrace, InferredFact, and TheoryFrameworkNode.
        assert len(NODE_TYPES) == 18
        labels = set(NODE_TYPES.keys())
        # Original 15 conflict-grammar types
        original_15 = {
            "Actor",
            "Conflict",
            "Event",
            "Issue",
            "Interest",
            "Norm",
            "Process",
            "Outcome",
            "Narrative",
            "EmotionalState",
            "TrustState",
            "PowerDynamic",
            "Location",
            "Evidence",
            "Role",
        }
        # Persistence / scaffold types added in the reasoning persistence layer
        new_types = {
            "ReasoningTrace",
            "InferredFact",
            "TheoryFrameworkNode",
        }
        assert original_15 | new_types == labels

    def test_each_node_type_has_unique_label(self):
        labels = list(NODE_TYPES.keys())
        assert len(labels) == len(set(labels))


class TestNodeTypeIds:
    """Test that all node types generate unique IDs."""

    def test_actor_has_id(self):
        a = Actor(name="Test", actor_type="person")
        assert a.id
        assert len(a.id) > 10

    def test_ids_are_unique(self):
        a1 = Actor(name="Same", actor_type="person")
        a2 = Actor(name="Same", actor_type="person")
        assert a1.id != a2.id

    def test_all_types_generate_ids(self):
        nodes = [
            Actor(name="A", actor_type="person"),
            Conflict(name="C", scale="micro", domain="workplace", status="active"),
            Event(event_type="protest", severity=0.5, occurred_at=datetime.now(UTC)),
        ]
        for node in nodes:
            assert node.id
            assert isinstance(node.id, str)


class TestNodeConfidence:
    """Test confidence field behavior."""

    def test_default_confidence(self):
        a = Actor(name="Test", actor_type="person")
        assert a.confidence is not None

    def test_confidence_bounds(self):
        a = Actor(name="Test", actor_type="person", confidence=0.95)
        assert 0.0 <= a.confidence <= 1.0
