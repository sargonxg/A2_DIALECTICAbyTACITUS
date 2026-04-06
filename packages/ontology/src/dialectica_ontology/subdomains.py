"""
Conflict Subdomains — Domain-specific ontology specifications for DIALECTICA.

Maps each conflict subdomain (geopolitical, workplace, commercial, legal, armed,
environmental) to its primary node/edge types, applicable theories, vocabulary,
and escalation indicators. Enables automatic subdomain detection from graph structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class ConflictSubdomain(StrEnum):
    """Conflict subdomain classification."""

    GEOPOLITICAL = "geopolitical"
    WORKPLACE = "workplace"
    COMMERCIAL = "commercial"
    LEGAL = "legal"
    ARMED = "armed"
    ENVIRONMENTAL = "environmental"


@dataclass
class SubdomainSpec:
    """Specification for a conflict subdomain.

    Defines which ontology elements are most relevant, which theories apply,
    domain-specific vocabulary, and escalation indicators.
    """

    subdomain: ConflictSubdomain
    description: str
    primary_node_types: list[str] = field(default_factory=list)
    primary_edge_types: list[str] = field(default_factory=list)
    applicable_theories: list[str] = field(default_factory=list)
    vocabulary: list[str] = field(default_factory=list)
    escalation_indicators: list[str] = field(default_factory=list)


SUBDOMAIN_SPECS: dict[ConflictSubdomain, SubdomainSpec] = {
    ConflictSubdomain.GEOPOLITICAL: SubdomainSpec(
        subdomain=ConflictSubdomain.GEOPOLITICAL,
        description="Interstate and diplomatic conflicts including treaty disputes, sanctions, and UN processes.",
        primary_node_types=["Actor", "Conflict", "Event", "Norm", "Process", "Interest"],
        primary_edge_types=[
            "PARTY_TO", "ALLIED_WITH", "OPPOSED_TO", "GOVERNED_BY", "VIOLATES",
        ],
        applicable_theories=[
            "glasl", "zartman", "kriesberg", "galtung", "azar_protracted",
            "kelman_problem_solving", "deutsch_cooperation",
        ],
        vocabulary=[
            "sovereignty", "sanctions", "treaty", "diplomacy", "deterrence",
            "bilateral", "multilateral", "ceasefire", "embargo", "ratification",
        ],
        escalation_indicators=[
            "sanctions_imposed", "ambassador_recalled", "military_mobilization",
            "treaty_violation", "ultimatum_issued",
        ],
    ),
    ConflictSubdomain.WORKPLACE: SubdomainSpec(
        subdomain=ConflictSubdomain.WORKPLACE,
        description="Organizational and interpersonal workplace disputes including harassment, discrimination, and management conflicts.",
        primary_node_types=["Actor", "Conflict", "Event", "EmotionalState", "TrustState", "Role"],
        primary_edge_types=[
            "PARTY_TO", "HAS_POWER_OVER", "EXPERIENCES", "TRUSTS", "MEMBER_OF",
        ],
        applicable_theories=[
            "fisher_ury", "mayer_trust", "french_raven", "plutchik",
            "thomas_kilmann", "burton_basic_needs", "deutsch_cooperation",
        ],
        vocabulary=[
            "grievance", "harassment", "mediation", "HR", "policy",
            "termination", "promotion", "performance", "retaliation", "whistleblower",
        ],
        escalation_indicators=[
            "formal_complaint_filed", "legal_threat", "resignation_threat",
            "public_accusation", "regulatory_involvement",
        ],
    ),
    ConflictSubdomain.COMMERCIAL: SubdomainSpec(
        subdomain=ConflictSubdomain.COMMERCIAL,
        description="Business and commercial disputes including contract breaches, IP conflicts, and partnership dissolution.",
        primary_node_types=["Actor", "Conflict", "Interest", "Norm", "Process", "Outcome"],
        primary_edge_types=[
            "PARTY_TO", "HAS_INTEREST", "GOVERNED_BY", "VIOLATES", "RESOLVED_THROUGH",
        ],
        applicable_theories=[
            "fisher_ury", "ury_brett_goldberg", "deutsch_cooperation",
            "kriesberg", "lederach_transformation",
        ],
        vocabulary=[
            "breach", "damages", "liability", "arbitration", "settlement",
            "injunction", "indemnity", "fiduciary", "consideration", "force_majeure",
        ],
        escalation_indicators=[
            "litigation_filed", "injunction_sought", "regulatory_complaint",
            "public_disclosure", "contract_termination",
        ],
    ),
    ConflictSubdomain.LEGAL: SubdomainSpec(
        subdomain=ConflictSubdomain.LEGAL,
        description="Legal proceedings, regulatory disputes, and rights-based conflicts.",
        primary_node_types=["Actor", "Conflict", "Norm", "Evidence", "Process", "Outcome"],
        primary_edge_types=[
            "GOVERNED_BY", "VIOLATES", "EVIDENCED_BY", "RESOLVED_THROUGH", "PRODUCES",
        ],
        applicable_theories=[
            "fisher_ury", "ury_brett_goldberg", "pearl_causal", "kriesberg",
        ],
        vocabulary=[
            "jurisdiction", "precedent", "statute", "ruling", "appeal",
            "discovery", "testimony", "verdict", "compliance", "enforcement",
        ],
        escalation_indicators=[
            "appeal_filed", "contempt_motion", "injunction_granted",
            "class_action_certification", "criminal_referral",
        ],
    ),
    ConflictSubdomain.ARMED: SubdomainSpec(
        subdomain=ConflictSubdomain.ARMED,
        description="Armed conflicts including civil wars, insurgencies, and military operations.",
        primary_node_types=[
            "Actor", "Conflict", "Event", "Location", "Evidence", "PowerDynamic",
        ],
        primary_edge_types=[
            "PARTY_TO", "ALLIED_WITH", "OPPOSED_TO", "AT_LOCATION",
            "HAS_POWER_OVER", "CAUSED",
        ],
        applicable_theories=[
            "glasl", "zartman", "galtung", "azar_protracted",
            "kriesberg", "kelman_problem_solving",
        ],
        vocabulary=[
            "ceasefire", "combatant", "civilian", "atrocity", "IHL",
            "peacekeeping", "disarmament", "demobilization", "reintegration", "buffer_zone",
        ],
        escalation_indicators=[
            "civilian_casualties", "weapons_escalation", "territorial_advance",
            "ceasefire_violation", "humanitarian_crisis",
        ],
    ),
    ConflictSubdomain.ENVIRONMENTAL: SubdomainSpec(
        subdomain=ConflictSubdomain.ENVIRONMENTAL,
        description="Environmental and resource conflicts including water rights, land use, and climate disputes.",
        primary_node_types=[
            "Actor", "Conflict", "Issue", "Location", "Interest", "Narrative",
        ],
        primary_edge_types=[
            "PARTY_TO", "HAS_INTEREST", "AT_LOCATION", "ABOUT", "OPPOSED_TO",
        ],
        applicable_theories=[
            "burton_basic_needs", "galtung", "lederach_transformation",
            "fisher_ury", "winslade_monk",
        ],
        vocabulary=[
            "resource_scarcity", "pollution", "displacement", "indigenous_rights",
            "sustainability", "extraction", "conservation", "climate", "watershed", "biodiversity",
        ],
        escalation_indicators=[
            "protest_action", "legal_injunction", "resource_blockade",
            "forced_displacement", "environmental_damage",
        ],
    ),
}


def detect_subdomain(
    node_labels: list[str],
    edge_types: list[str],
) -> ConflictSubdomain:
    """Detect the most likely conflict subdomain from graph structure.

    Scores each subdomain by overlap between the graph's node labels / edge types
    and the subdomain's primary types. Returns the best match.

    Args:
        node_labels: List of node type labels present in the graph (e.g. ["Actor", "Event"]).
        edge_types: List of edge types present in the graph (e.g. ["PARTY_TO", "ALLIED_WITH"]).

    Returns:
        The ConflictSubdomain with the highest overlap score.
    """
    node_set = set(node_labels)
    edge_set = set(edge_types)

    best_subdomain = ConflictSubdomain.GEOPOLITICAL
    best_score = -1.0

    for subdomain, spec in SUBDOMAIN_SPECS.items():
        node_overlap = len(node_set & set(spec.primary_node_types))
        edge_overlap = len(edge_set & set(spec.primary_edge_types))

        # Normalise by the spec's total type count to avoid biasing toward larger specs
        total_types = len(spec.primary_node_types) + len(spec.primary_edge_types)
        score = (node_overlap + edge_overlap) / max(1, total_types)

        if score > best_score:
            best_score = score
            best_subdomain = subdomain

    return best_subdomain
