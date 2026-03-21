"""Tests for PLOVER → ACO mapping and entity resolver."""
from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_ontology.enums import EventType, QuadClass
from dialectica_ontology.compatibility.plover import (
    PloverEventType,
    plover_to_dialectica,
    dialectica_to_plover,
    plover_quadclass,
    event_type_quadclass,
    plover_severity,
    plover_to_primitives,
)
from dialectica_ontology.primitives import Actor, Event
from dialectica_extraction.connectors.entity_resolver import EntityResolver


# ═══════════════════════════════════════════════════════════════════════════
#  PLOVER TYPE MAPPING
# ═══════════════════════════════════════════════════════════════════════════


class TestPloverToDialectica:
    def test_agree(self):
        assert plover_to_dialectica("AGREE") == EventType.AGREE

    def test_assault(self):
        assert plover_to_dialectica("ASSAULT") == EventType.ASSAULT

    def test_protest(self):
        assert plover_to_dialectica("PROTEST") == EventType.PROTEST

    def test_case_insensitive(self):
        assert plover_to_dialectica("agree") == EventType.AGREE
        assert plover_to_dialectica("Protest") == EventType.PROTEST

    def test_all_16_types_mapped(self):
        for pt in PloverEventType:
            result = plover_to_dialectica(pt.value)
            assert isinstance(result, EventType)

    def test_unknown_raises(self):
        with pytest.raises(KeyError):
            plover_to_dialectica("NONEXISTENT")


class TestDialecticaToPlover:
    def test_roundtrip(self):
        for code in ["AGREE", "ASSAULT", "PROTEST", "THREATEN", "DEMAND"]:
            event_type = plover_to_dialectica(code)
            back = dialectica_to_plover(event_type)
            # Note: some types map many-to-one, so roundtrip may differ
            assert isinstance(back, str)


# ═══════════════════════════════════════════════════════════════════════════
#  QUADCLASS MAPPING
# ═══════════════════════════════════════════════════════════════════════════


class TestQuadClass:
    def test_agree_is_verbal_cooperation(self):
        assert plover_quadclass("AGREE") == QuadClass.VERBAL_COOPERATION

    def test_assault_is_material_conflict(self):
        assert plover_quadclass("ASSAULT") == QuadClass.MATERIAL_CONFLICT

    def test_demand_is_verbal_conflict(self):
        assert plover_quadclass("DEMAND") == QuadClass.VERBAL_CONFLICT

    def test_aid_is_material_cooperation(self):
        assert plover_quadclass("AID") == QuadClass.MATERIAL_COOPERATION

    def test_all_16_have_quadclass(self):
        for pt in PloverEventType:
            qc = plover_quadclass(pt.value)
            assert isinstance(qc, QuadClass)


# ═══════════════════════════════════════════════════════════════════════════
#  SEVERITY MAPPING
# ═══════════════════════════════════════════════════════════════════════════


class TestPloverSeverity:
    def test_protest_riot_high_severity(self):
        sev = plover_severity("PROTEST", mode="riot")
        assert sev == 0.8

    def test_protest_peaceful_low_severity(self):
        sev = plover_severity("PROTEST", mode="peaceful")
        assert sev == 0.3

    def test_assault_default(self):
        sev = plover_severity("ASSAULT")
        assert sev == 0.8

    def test_agree_low(self):
        sev = plover_severity("AGREE")
        assert sev == 0.1

    def test_unknown_mode_uses_default(self):
        sev = plover_severity("PROTEST", mode="unknown_mode")
        assert sev == 0.4  # Default for PROTEST


# ═══════════════════════════════════════════════════════════════════════════
#  PLOVER TO PRIMITIVES
# ═══════════════════════════════════════════════════════════════════════════


class TestPloverToPrimitives:
    def test_basic_conversion(self):
        result = plover_to_primitives("ASSAULT", performer="State A", target="Group B")
        assert result["event_type"] == "assault"
        assert result["severity"] == 0.8
        assert result["performer_id"] == "State A"
        assert result["target_id"] == "Group B"

    def test_with_mode(self):
        result = plover_to_primitives("PROTEST", mode="riot")
        assert result["severity"] == 0.8

    def test_source_text(self):
        result = plover_to_primitives("AGREE")
        assert "PLOVER:AGREE" in result["source_text"]


# ═══════════════════════════════════════════════════════════════════════════
#  ENTITY RESOLVER
# ═══════════════════════════════════════════════════════════════════════════


class TestEntityResolver:
    def test_exact_match(self):
        resolver = EntityResolver()
        actor = Actor(name="United Nations", actor_type="organization")
        resolver.register_actor(actor, aliases=["UN"])

        result = resolver.resolve("United Nations")
        assert result is not None
        assert result.name == "United Nations"

    def test_alias_match(self):
        resolver = EntityResolver()
        actor = Actor(name="United Nations", actor_type="organization")
        resolver.register_actor(actor, aliases=["UN"])

        result = resolver.resolve("UN")
        assert result is not None
        assert result.name == "United Nations"

    def test_fuzzy_match(self):
        resolver = EntityResolver()
        actor = Actor(name="United Nations Security Council", actor_type="organization")
        resolver.register_actor(actor)

        result = resolver.resolve("United Nations Security Counci")  # Typo
        assert result is not None

    def test_no_match(self):
        resolver = EntityResolver()
        actor = Actor(name="Iran", actor_type="state")
        resolver.register_actor(actor)

        result = resolver.resolve("Completely Different Name")
        assert result is None

    def test_resolve_or_create(self):
        resolver = EntityResolver()
        actor = resolver.resolve_or_create("New Actor", actor_type="person")
        assert actor.name == "New Actor"

        # Second call returns same
        actor2 = resolver.resolve_or_create("New Actor")
        assert actor2.id == actor.id

    def test_deduplicate_events(self):
        from datetime import datetime
        resolver = EntityResolver()

        e1 = Event(event_type="protest", severity=0.5, occurred_at=datetime(2024, 1, 1), confidence=0.9)
        e2 = Event(event_type="protest", severity=0.6, occurred_at=datetime(2024, 1, 1), confidence=0.7)
        e3 = Event(event_type="assault", severity=0.8, occurred_at=datetime(2024, 1, 1))

        result = resolver.deduplicate_events([e1, e2, e3])
        # e1 and e2 should be merged (same date + type), e3 is different type
        assert len(result) == 2
