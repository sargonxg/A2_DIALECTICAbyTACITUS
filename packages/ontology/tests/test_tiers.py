"""Tests for dialectica_ontology.tiers — Tier configuration and compliance."""

from dialectica_ontology.tiers import (
    OntologyTier,
    get_available_edges,
    get_available_features,
    get_available_nodes,
)


def test_tier_enum():
    assert len(OntologyTier) == 3
    assert OntologyTier.ESSENTIAL == "essential"
    assert OntologyTier.STANDARD == "standard"
    assert OntologyTier.FULL == "full"


def test_essential_nodes():
    nodes = get_available_nodes(OntologyTier.ESSENTIAL)
    assert "Actor" in nodes
    assert "Conflict" in nodes
    assert "Event" in nodes
    assert "Issue" in nodes
    assert "Process" in nodes
    assert "Outcome" in nodes
    assert "Location" in nodes
    assert len(nodes) == 7


def test_standard_nodes():
    nodes = get_available_nodes(OntologyTier.STANDARD)
    assert len(nodes) == 12
    assert "Interest" in nodes
    assert "Norm" in nodes
    assert "Narrative" in nodes
    assert "Evidence" in nodes
    assert "Role" in nodes


def test_full_nodes():
    nodes = get_available_nodes(OntologyTier.FULL)
    # Full tier now has 18 nodes: 15 original + ReasoningTrace + InferredFact
    # + TheoryFrameworkNode (added in TACITUS Core Ontology v2.1)
    assert len(nodes) == 18
    assert "EmotionalState" in nodes
    assert "TrustState" in nodes
    assert "PowerDynamic" in nodes
    assert "ReasoningTrace" in nodes
    assert "InferredFact" in nodes
    assert "TheoryFrameworkNode" in nodes


def test_tier_cumulative_nodes():
    essential = get_available_nodes(OntologyTier.ESSENTIAL)
    standard = get_available_nodes(OntologyTier.STANDARD)
    full = get_available_nodes(OntologyTier.FULL)
    assert essential.issubset(standard)
    assert standard.issubset(full)


def test_essential_edges():
    edges = get_available_edges(OntologyTier.ESSENTIAL)
    assert "PARTY_TO" in edges
    assert "PARTICIPATES_IN" in edges
    assert "PART_OF" in edges
    assert "AT_LOCATION" in edges
    assert "RESOLVED_THROUGH" in edges
    assert "PRODUCES" in edges
    assert len(edges) == 6


def test_full_edges():
    edges = get_available_edges(OntologyTier.FULL)
    assert len(edges) == 20


def test_tier_cumulative_edges():
    essential = get_available_edges(OntologyTier.ESSENTIAL)
    standard = get_available_edges(OntologyTier.STANDARD)
    full = get_available_edges(OntologyTier.FULL)
    assert essential.issubset(standard)
    assert standard.issubset(full)


def test_features_exist():
    features = get_available_features(OntologyTier.FULL)
    assert "conflict_mapping" in features
    assert "neurosymbolic_inference" in features


def test_tier_cumulative_features():
    essential = get_available_features(OntologyTier.ESSENTIAL)
    standard = get_available_features(OntologyTier.STANDARD)
    full = get_available_features(OntologyTier.FULL)
    assert essential.issubset(standard)
    assert standard.issubset(full)
