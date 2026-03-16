"""
Ontology Tiers — Three-tier access model for DIALECTICA.

Essential: 7 node types, 6 edge types — Quick conflict mapping
Standard: 12 node types, 13 edge types — Structured analysis
Full:     15 node types, 20 edge types — Complete neurosymbolic intelligence

Includes TIER_CONFIGS dict and helper functions for tier-based access control.
"""
from __future__ import annotations

from enum import StrEnum
from typing import FrozenSet


# ─── Tier Enum ─────────────────────────────────────────────────────────────────

class OntologyTier(StrEnum):
    """Three-tier access model for progressive disclosure of ontology complexity."""
    ESSENTIAL = "essential"
    STANDARD = "standard"
    FULL = "full"


# ─── Node Tier Mappings ───────────────────────────────────────────────────────

_ESSENTIAL_NODES: frozenset[str] = frozenset({
    "Actor",
    "Conflict",
    "Event",
    "Issue",
    "Process",
    "Outcome",
    "Location",
})

_STANDARD_NODES: frozenset[str] = _ESSENTIAL_NODES | frozenset({
    "Interest",
    "Norm",
    "Narrative",
    "Evidence",
    "Role",
})

_FULL_NODES: frozenset[str] = _STANDARD_NODES | frozenset({
    "EmotionalState",
    "TrustState",
    "PowerDynamic",
})

TIER_NODES: dict[OntologyTier, frozenset[str]] = {
    OntologyTier.ESSENTIAL: _ESSENTIAL_NODES,
    OntologyTier.STANDARD: _STANDARD_NODES,
    OntologyTier.FULL: _FULL_NODES,
}


# ─── Edge Tier Mappings ──────────────────────────────────────────────────────

_ESSENTIAL_EDGES: frozenset[str] = frozenset({
    "PARTY_TO",
    "PARTICIPATES_IN",
    "PART_OF",
    "AT_LOCATION",
    "RESOLVED_THROUGH",
    "PRODUCES",
})

_STANDARD_EDGES: frozenset[str] = _ESSENTIAL_EDGES | frozenset({
    "HAS_INTEREST",
    "GOVERNED_BY",
    "VIOLATES",
    "ABOUT",
    "EVIDENCED_BY",
    "WITHIN",
    "MEMBER_OF",
})

_FULL_EDGES: frozenset[str] = _STANDARD_EDGES | frozenset({
    "EXPERIENCES",
    "TRUSTS",
    "PROMOTES",
    "HAS_POWER_OVER",
    "ALLIED_WITH",
    "OPPOSED_TO",
    "CAUSED",
})

TIER_EDGES: dict[OntologyTier, frozenset[str]] = {
    OntologyTier.ESSENTIAL: _ESSENTIAL_EDGES,
    OntologyTier.STANDARD: _STANDARD_EDGES,
    OntologyTier.FULL: _FULL_EDGES,
}


# ─── Feature Tier Mappings ───────────────────────────────────────────────────

_ESSENTIAL_FEATURES: frozenset[str] = frozenset({
    "conflict_mapping",
    "event_timeline",
    "actor_identification",
    "spatial_mapping",
    "process_tracking",
    "outcome_recording",
})

_STANDARD_FEATURES: frozenset[str] = _ESSENTIAL_FEATURES | frozenset({
    "interest_analysis",
    "norm_compliance",
    "narrative_analysis",
    "evidence_linking",
    "role_assignment",
    "glasl_escalation",
    "kriesberg_lifecycle",
})

_FULL_FEATURES: frozenset[str] = _STANDARD_FEATURES | frozenset({
    "emotion_tracking",
    "trust_assessment",
    "power_analysis",
    "alliance_detection",
    "causal_reasoning",
    "neurosymbolic_inference",
    "plutchik_wheel",
    "french_raven_power",
    "mayer_trust_model",
})

TIER_FEATURES: dict[OntologyTier, frozenset[str]] = {
    OntologyTier.ESSENTIAL: _ESSENTIAL_FEATURES,
    OntologyTier.STANDARD: _STANDARD_FEATURES,
    OntologyTier.FULL: _FULL_FEATURES,
}


# ─── Tier Configuration Summary ──────────────────────────────────────────────

TIER_CONFIGS: dict[OntologyTier, dict[str, int | str | frozenset[str]]] = {
    OntologyTier.ESSENTIAL: {
        "name": "Essential",
        "description": "Core conflict mapping — actors, events, locations, and resolution processes",
        "node_count": len(_ESSENTIAL_NODES),
        "edge_count": len(_ESSENTIAL_EDGES),
        "feature_count": len(_ESSENTIAL_FEATURES),
        "nodes": _ESSENTIAL_NODES,
        "edges": _ESSENTIAL_EDGES,
        "features": _ESSENTIAL_FEATURES,
    },
    OntologyTier.STANDARD: {
        "name": "Standard",
        "description": "Structured analysis — adds interests, norms, narratives, evidence, and roles",
        "node_count": len(_STANDARD_NODES),
        "edge_count": len(_STANDARD_EDGES),
        "feature_count": len(_STANDARD_FEATURES),
        "nodes": _STANDARD_NODES,
        "edges": _STANDARD_EDGES,
        "features": _STANDARD_FEATURES,
    },
    OntologyTier.FULL: {
        "name": "Full",
        "description": "Complete neurosymbolic intelligence — emotions, trust, power dynamics, causal reasoning",
        "node_count": len(_FULL_NODES),
        "edge_count": len(_FULL_EDGES),
        "feature_count": len(_FULL_FEATURES),
        "nodes": _FULL_NODES,
        "edges": _FULL_EDGES,
        "features": _FULL_FEATURES,
    },
}


# ─── Helper Functions ────────────────────────────────────────────────────────

def get_available_nodes(tier: OntologyTier) -> set[str]:
    """Return the set of node type names available at the given tier.

    Each tier includes all nodes from lower tiers:
        ESSENTIAL -> STANDARD -> FULL (cumulative).

    Args:
        tier: The ontology access tier.

    Returns:
        Set of node type name strings (e.g. {"Actor", "Conflict", ...}).
    """
    return set(TIER_NODES[tier])


def get_available_edges(tier: OntologyTier) -> set[str]:
    """Return the set of edge type names available at the given tier.

    Each tier includes all edges from lower tiers:
        ESSENTIAL -> STANDARD -> FULL (cumulative).

    Args:
        tier: The ontology access tier.

    Returns:
        Set of edge type name strings (e.g. {"PARTY_TO", "PART_OF", ...}).
    """
    return set(TIER_EDGES[tier])


def get_available_features(tier: OntologyTier) -> set[str]:
    """Return the set of analysis feature names available at the given tier.

    Each tier includes all features from lower tiers:
        ESSENTIAL -> STANDARD -> FULL (cumulative).

    Args:
        tier: The ontology access tier.

    Returns:
        Set of feature name strings (e.g. {"conflict_mapping", ...}).
    """
    return set(TIER_FEATURES[tier])
