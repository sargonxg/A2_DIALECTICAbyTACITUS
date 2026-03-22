"""Tests for dialectica_ontology.theory_graph — Theory knowledge graph node/edge types."""

from datetime import datetime

from dialectica_ontology.theory_graph import (
    THEORY_EDGE_TYPES,
    THEORY_NODE_TYPES,
    Methodology,
    Pattern,
    Principle,
    Publication,
    Theorist,
    TheoryConcept,
    TheoryNode,
)

# ─── TheoryNode (base) ────────────────────────────────────────────────────────


class TestTheoryNode:
    """Tests for the TheoryNode base model."""

    def test_creation(self):
        node = TheoryNode(id="tn1", label="TestNode")
        assert node.id == "tn1"
        assert node.label == "TestNode"
        assert isinstance(node.created_at, datetime)
        assert node.metadata == {}

    def test_default_metadata_is_empty_dict(self):
        node = TheoryNode(id="tn1", label="X")
        assert node.metadata == {}

    def test_custom_metadata(self):
        node = TheoryNode(id="tn1", label="X", metadata={"key": "value"})
        assert node.metadata == {"key": "value"}

    def test_created_at_auto_set(self):
        before = datetime.utcnow()
        node = TheoryNode(id="tn1", label="X")
        after = datetime.utcnow()
        assert before <= node.created_at <= after


# ─── TheoryConcept ─────────────────────────────────────────────────────────────


class TestTheoryConcept:
    """Tests for the TheoryConcept model."""

    def test_creation(self):
        concept = TheoryConcept(
            id="tc1",
            name="BATNA",
            framework_id="fisher_ury",
            description="Best Alternative to a Negotiated Agreement",
        )
        assert concept.id == "tc1"
        assert concept.label == "TheoryConcept"
        assert concept.name == "BATNA"
        assert concept.framework_id == "fisher_ury"
        assert concept.description == "Best Alternative to a Negotiated Agreement"
        assert concept.category == ""
        assert concept.key_authors == []

    def test_label_default(self):
        concept = TheoryConcept(
            id="tc1",
            name="X",
            framework_id="f",
            description="d",
        )
        assert concept.label == "TheoryConcept"

    def test_with_optional_fields(self):
        concept = TheoryConcept(
            id="tc1",
            name="MHS",
            framework_id="zartman",
            description="Mutually Hurting Stalemate",
            category="ripeness",
            key_authors=["Zartman", "Touval"],
        )
        assert concept.category == "ripeness"
        assert concept.key_authors == ["Zartman", "Touval"]

    def test_inherits_theory_node(self):
        concept = TheoryConcept(
            id="tc1",
            name="X",
            framework_id="f",
            description="d",
        )
        assert isinstance(concept, TheoryNode)
        assert isinstance(concept.created_at, datetime)
        assert concept.metadata == {}


# ─── Theorist ──────────────────────────────────────────────────────────────────


class TestTheorist:
    """Tests for the Theorist model."""

    def test_creation(self):
        t = Theorist(id="th1", name="Friedrich Glasl")
        assert t.id == "th1"
        assert t.label == "Theorist"
        assert t.name == "Friedrich Glasl"
        assert t.affiliation == ""
        assert t.key_works == []
        assert t.birth_year is None

    def test_with_all_fields(self):
        t = Theorist(
            id="th1",
            name="Roger Fisher",
            affiliation="Harvard Law School",
            key_works=["Getting to Yes"],
            birth_year=1922,
        )
        assert t.affiliation == "Harvard Law School"
        assert t.key_works == ["Getting to Yes"]
        assert t.birth_year == 1922

    def test_inherits_theory_node(self):
        t = Theorist(id="th1", name="X")
        assert isinstance(t, TheoryNode)


# ─── Publication ───────────────────────────────────────────────────────────────


class TestPublication:
    """Tests for the Publication model."""

    def test_creation(self):
        pub = Publication(
            id="pub1",
            title="Getting to Yes",
            year=1981,
            authors=["Roger Fisher", "William Ury"],
        )
        assert pub.id == "pub1"
        assert pub.label == "Publication"
        assert pub.title == "Getting to Yes"
        assert pub.year == 1981
        assert pub.authors == ["Roger Fisher", "William Ury"]
        assert pub.publisher == ""
        assert pub.isbn == ""

    def test_with_optional_fields(self):
        pub = Publication(
            id="pub1",
            title="Conflict Management and Resolution",
            year=2020,
            authors=["Author A"],
            publisher="Cambridge University Press",
            isbn="978-0-1234-5678-9",
        )
        assert pub.publisher == "Cambridge University Press"
        assert pub.isbn == "978-0-1234-5678-9"

    def test_inherits_theory_node(self):
        pub = Publication(
            id="pub1",
            title="T",
            year=2000,
            authors=["A"],
        )
        assert isinstance(pub, TheoryNode)


# ─── Methodology ───────────────────────────────────────────────────────────────


class TestMethodology:
    """Tests for the Methodology model."""

    def test_creation(self):
        m = Methodology(
            id="m1",
            name="Facilitative Mediation",
            description="Third party assists negotiation without deciding",
        )
        assert m.id == "m1"
        assert m.label == "Methodology"
        assert m.name == "Facilitative Mediation"
        assert m.applicable_stages == []
        assert m.prerequisites == []

    def test_with_optional_fields(self):
        m = Methodology(
            id="m1",
            name="Arbitration",
            description="Binding third-party decision",
            applicable_stages=["stage_7", "stage_8", "stage_9"],
            prerequisites=["consent_of_parties", "arbitration_clause"],
        )
        assert m.applicable_stages == ["stage_7", "stage_8", "stage_9"]
        assert m.prerequisites == ["consent_of_parties", "arbitration_clause"]

    def test_inherits_theory_node(self):
        m = Methodology(id="m1", name="X", description="d")
        assert isinstance(m, TheoryNode)


# ─── Principle ─────────────────────────────────────────────────────────────────


class TestPrinciple:
    """Tests for the Principle model."""

    def test_creation(self):
        p = Principle(
            id="pr1",
            name="Interest-Based Negotiation",
            description="Focus on interests, not positions",
        )
        assert p.id == "pr1"
        assert p.label == "Principle"
        assert p.name == "Interest-Based Negotiation"
        assert p.description == "Focus on interests, not positions"
        assert p.source_framework == ""

    def test_with_source_framework(self):
        p = Principle(
            id="pr1",
            name="Separate people from problems",
            description="Avoid personal attacks",
            source_framework="fisher_ury",
        )
        assert p.source_framework == "fisher_ury"

    def test_inherits_theory_node(self):
        p = Principle(id="pr1", name="X", description="d")
        assert isinstance(p, TheoryNode)


# ─── Pattern ───────────────────────────────────────────────────────────────────


class TestPattern:
    """Tests for the Pattern model."""

    def test_creation(self):
        pat = Pattern(
            id="pat1",
            name="Tit-for-Tat Escalation",
            description="Reciprocal escalation cycle",
        )
        assert pat.id == "pat1"
        assert pat.label == "Pattern"
        assert pat.name == "Tit-for-Tat Escalation"
        assert pat.indicators == []
        assert pat.graph_signature == {}

    def test_with_optional_fields(self):
        pat = Pattern(
            id="pat1",
            name="Hurting Stalemate",
            description="Both parties locked in costly impasse",
            indicators=["no_progress", "high_cost", "mutual_pain"],
            graph_signature={"min_parties": 2, "phase": "stalemate"},
        )
        assert pat.indicators == ["no_progress", "high_cost", "mutual_pain"]
        assert pat.graph_signature == {"min_parties": 2, "phase": "stalemate"}

    def test_inherits_theory_node(self):
        pat = Pattern(id="pat1", name="X", description="d")
        assert isinstance(pat, TheoryNode)


# ─── THEORY_EDGE_TYPES ────────────────────────────────────────────────────────


class TestTheoryEdgeTypes:
    """Tests for the THEORY_EDGE_TYPES constant dict."""

    def test_has_expected_keys(self):
        expected = {
            "BUILDS_ON",
            "CONTRADICTS",
            "AUTHORED_BY",
            "INTRODUCES",
            "APPLIES_VIA",
            "EXEMPLIFIES",
            "PRESCRIBES",
        }
        assert set(THEORY_EDGE_TYPES.keys()) == expected

    def test_count(self):
        assert len(THEORY_EDGE_TYPES) == 7

    def test_each_entry_has_source_target_description(self):
        for edge_name, schema in THEORY_EDGE_TYPES.items():
            assert "source" in schema, f"{edge_name} missing 'source'"
            assert "target" in schema, f"{edge_name} missing 'target'"
            assert "description" in schema, f"{edge_name} missing 'description'"

    def test_builds_on(self):
        e = THEORY_EDGE_TYPES["BUILDS_ON"]
        assert e["source"] == "TheoryConcept"
        assert e["target"] == "TheoryConcept"

    def test_authored_by(self):
        e = THEORY_EDGE_TYPES["AUTHORED_BY"]
        assert e["source"] == "Publication"
        assert e["target"] == "Theorist"

    def test_introduces(self):
        e = THEORY_EDGE_TYPES["INTRODUCES"]
        assert e["source"] == "Publication"
        assert e["target"] == "TheoryConcept"

    def test_prescribes(self):
        e = THEORY_EDGE_TYPES["PRESCRIBES"]
        assert e["source"] == "Principle"
        assert e["target"] == "Methodology"


# ─── THEORY_NODE_TYPES ────────────────────────────────────────────────────────


class TestTheoryNodeTypes:
    """Tests for the THEORY_NODE_TYPES list."""

    def test_has_6_entries(self):
        assert len(THEORY_NODE_TYPES) == 6

    def test_contains_all_types(self):
        assert TheoryConcept in THEORY_NODE_TYPES
        assert Theorist in THEORY_NODE_TYPES
        assert Publication in THEORY_NODE_TYPES
        assert Methodology in THEORY_NODE_TYPES
        assert Principle in THEORY_NODE_TYPES
        assert Pattern in THEORY_NODE_TYPES

    def test_all_inherit_from_theory_node(self):
        for cls in THEORY_NODE_TYPES:
            assert issubclass(cls, TheoryNode)
