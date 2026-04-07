"""Tests for TheoryFrameworkNode — theory layer graph node for ASSESSED_VIA traversal."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from dialectica_ontology import TheoryFrameworkNode
from dialectica_ontology.primitives import NODE_TYPES, ConflictNode

# ─── Model creation ──────────────────────────────────────────────────────────


class TestTheoryFrameworkNodeCreation:
    """TheoryFrameworkNode Pydantic model creation tests."""

    def test_minimal_creation(self):
        node = TheoryFrameworkNode(
            framework_id="glasl",
            display_name="Glasl 9-Stage Escalation Model",
            domain="conflict_warfare",
        )
        assert node.framework_id == "glasl"
        assert node.display_name == "Glasl 9-Stage Escalation Model"
        assert node.domain == "conflict_warfare"
        assert node.label == "TheoryFrameworkNode"
        assert node.node_type == "TheoryFrameworkNode"

    def test_id_auto_generated(self):
        node = TheoryFrameworkNode(
            framework_id="zartman",
            display_name="Zartman Ripeness Theory",
            domain="conflict_warfare",
        )
        assert node.id  # truthy — auto-generated ULID
        assert len(node.id) > 0

    def test_created_at_auto_set(self):
        before = datetime.utcnow()
        node = TheoryFrameworkNode(
            framework_id="fisher_ury",
            display_name="Fisher & Ury",
            domain="human_friction",
        )
        after = datetime.utcnow()
        assert before <= node.created_at <= after

    def test_all_list_fields_default_to_empty(self):
        node = TheoryFrameworkNode(
            framework_id="galtung",
            display_name="Galtung Conflict Triangle",
            domain="universal",
        )
        assert node.core_concepts == []
        assert node.key_propositions == []
        assert node.escalation_indicators == []
        assert node.de_escalation_levers == []
        assert node.primary_questions == []
        assert node.citations == []

    def test_full_creation_with_all_fields(self):
        node = TheoryFrameworkNode(
            framework_id="burton",
            display_name="Burton Basic Human Needs Theory",
            domain="universal",
            workspace_id="ws_theory_scaffold",
            tenant_id="shared",
            core_concepts=["Basic human needs", "Provention"],
            key_propositions=[
                "Deep-rooted conflicts arise from denial of basic human needs",
                "Basic human needs are non-negotiable",
            ],
            escalation_indicators=["Identity needs denied", "Security needs unmet"],
            de_escalation_levers=["Problem-solving workshops", "Structural change"],
            primary_questions=["Which basic human needs are being frustrated?"],
            citations=["Burton, J. (1990). Conflict: Resolution and Provention."],
        )
        assert node.framework_id == "burton"
        assert len(node.core_concepts) == 2
        assert len(node.key_propositions) == 2
        assert len(node.escalation_indicators) == 2
        assert len(node.de_escalation_levers) == 2
        assert len(node.primary_questions) == 1
        assert len(node.citations) == 1

    def test_inherits_from_conflict_node(self):
        node = TheoryFrameworkNode(
            framework_id="glasl",
            display_name="Glasl",
            domain="conflict_warfare",
        )
        assert isinstance(node, ConflictNode)

    def test_confidence_field_inherited_from_conflict_node(self):
        node = TheoryFrameworkNode(
            framework_id="glasl",
            display_name="Glasl",
            domain="conflict_warfare",
            confidence=0.95,
        )
        assert node.confidence == 0.95

    def test_confidence_validation_bounds(self):
        with pytest.raises(ValidationError):
            TheoryFrameworkNode(
                framework_id="glasl",
                display_name="Glasl",
                domain="conflict_warfare",
                confidence=1.5,  # out of range
            )

    def test_domain_values(self):
        for domain in ("human_friction", "conflict_warfare", "universal"):
            node = TheoryFrameworkNode(
                framework_id=f"test_{domain}",
                display_name="Test",
                domain=domain,
            )
            assert node.domain == domain

    def test_metadata_default_empty_dict(self):
        node = TheoryFrameworkNode(
            framework_id="glasl",
            display_name="Glasl",
            domain="conflict_warfare",
        )
        assert node.metadata == {}

    def test_serialization_roundtrip(self):
        node = TheoryFrameworkNode(
            framework_id="mayer_trust",
            display_name="Mayer Trust Framework",
            domain="universal",
            core_concepts=["Perceived ability", "Benevolence", "Integrity"],
            citations=["Mayer et al. (1995). AMR."],
        )
        dumped = node.model_dump()
        assert dumped["framework_id"] == "mayer_trust"
        assert dumped["label"] == "TheoryFrameworkNode"
        assert dumped["node_type"] == "TheoryFrameworkNode"
        assert dumped["core_concepts"] == ["Perceived ability", "Benevolence", "Integrity"]


# ─── NODE_TYPES registry ─────────────────────────────────────────────────────


class TestNodeTypesRegistry:
    """Verify TheoryFrameworkNode is in the NODE_TYPES registry."""

    def test_theory_framework_node_in_registry(self):
        assert "TheoryFrameworkNode" in NODE_TYPES

    def test_registry_maps_to_correct_class(self):
        assert NODE_TYPES["TheoryFrameworkNode"] is TheoryFrameworkNode

    def test_registry_still_has_all_original_types(self):
        original_types = [
            "Actor", "Conflict", "Event", "Issue", "Interest", "Norm",
            "Process", "Outcome", "Narrative", "EmotionalState", "TrustState",
            "PowerDynamic", "Location", "Evidence", "Role",
        ]
        for t in original_types:
            assert t in NODE_TYPES, f"{t!r} missing from NODE_TYPES"

    def test_registry_instantiable_from_label(self):
        cls = NODE_TYPES["TheoryFrameworkNode"]
        node = cls(
            framework_id="plutchik",
            display_name="Plutchik Emotion Wheel",
            domain="human_friction",
        )
        assert node.label == "TheoryFrameworkNode"


# ─── __init__ exports ────────────────────────────────────────────────────────


class TestInitExports:
    """Verify TheoryFrameworkNode is exported from the package __init__."""

    def test_import_from_package(self):
        from dialectica_ontology import TheoryFrameworkNode as ImportedNode  # noqa: PLC2401

        assert ImportedNode is TheoryFrameworkNode

    def test_node_types_exported_from_package(self):
        from dialectica_ontology import NODE_TYPES as NT

        assert "TheoryFrameworkNode" in NT

    def test_in_all_list(self):
        import dialectica_ontology

        assert "TheoryFrameworkNode" in dialectica_ontology.__all__


# ─── 15 framework IDs ────────────────────────────────────────────────────────

EXPECTED_FRAMEWORK_IDS = [
    "glasl",
    "zartman",
    "fisher_ury",
    "galtung",
    "lederach",
    "kriesberg",
    "deutsch",
    "thomas_kilmann",
    "french_raven",
    "mayer_trust",
    "plutchik",
    "pearl_causal",
    "winslade_monk",
    "ury_brett_goldberg",
    "burton",
]


class TestAllFifteenFrameworks:
    """Verify that all 15 expected framework IDs are valid TheoryFrameworkNode values."""

    @pytest.mark.parametrize("framework_id", EXPECTED_FRAMEWORK_IDS)
    def test_framework_node_creatable(self, framework_id: str):
        node = TheoryFrameworkNode(
            framework_id=framework_id,
            display_name=f"Test: {framework_id}",
            domain="universal",
        )
        assert node.framework_id == framework_id
        assert node.node_type == "TheoryFrameworkNode"

    def test_fifteen_framework_ids_defined(self):
        assert len(EXPECTED_FRAMEWORK_IDS) == 15
