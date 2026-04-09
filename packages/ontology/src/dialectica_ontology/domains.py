"""
DIALECTICA Two-Domain Specialization — Human Friction & Conflict/Warfare.

DIALECTICA serves two primary domains:

1. **HUMAN FRICTION** (micro-meso scale)
   Interpersonal, workplace, commercial, and legal disputes.
   Focus: mediation, negotiation, interest-based resolution, trust repair.
   Theories: Fisher/Ury, Mayer/Davis/Schoorman, Thomas-Kilmann, Deutsch, Plutchik.
   Scale: micro (interpersonal) to meso (organizational/community).

2. **CONFLICT & WARFARE** (macro-meta scale)
   Geopolitical, armed, political, and protracted social conflicts.
   Focus: escalation tracking, ripeness analysis, causal chains, intervention design.
   Theories: Glasl, Zartman, Galtung, Azar, Kelman, Kriesberg, Lederach.
   Scale: macro (national/international) to meta (civilizational).

Both domains share the same Conflict Grammar ontology (15 node types, 20 edge types)
but differ in which theories, indicators, and intervention strategies are primary.

This module defines domain-aware configuration, theory selection, and extraction hints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


# ─── Domain Enums ─────────────────────────────────────────────────────────────


class TacitusDomain(StrEnum):
    """The two primary TACITUS/DIALECTICA application domains."""

    HUMAN_FRICTION = "human_friction"
    CONFLICT_WARFARE = "conflict_warfare"


class FrictionSubdomain(StrEnum):
    """Subdomains within Human Friction."""

    INTERPERSONAL = "interpersonal"
    WORKPLACE = "workplace"
    COMMERCIAL = "commercial"
    LEGAL = "legal"
    FAMILY = "family"
    COMMUNITY = "community"


class WarfareSubdomain(StrEnum):
    """Subdomains within Conflict & Warfare."""

    GEOPOLITICAL = "geopolitical"
    ARMED_CONFLICT = "armed_conflict"
    POLITICAL = "political"
    PROTRACTED_SOCIAL = "protracted_social"
    INSURGENCY = "insurgency"
    HYBRID_WARFARE = "hybrid_warfare"


# ─── Domain Specifications ────────────────────────────────────────────────────


@dataclass(frozen=True)
class DomainSpec:
    """Complete specification for a DIALECTICA application domain."""

    domain: TacitusDomain
    display_name: str
    description: str
    subdomains: tuple[str, ...]
    scale_range: tuple[str, str]  # (min_scale, max_scale)

    # Which of the 15 node types are PRIMARY for this domain
    primary_node_types: tuple[str, ...]
    # Which are SECONDARY (available but less common)
    secondary_node_types: tuple[str, ...]

    # Which of the 20 edge types are most used
    primary_edge_types: tuple[str, ...]

    # Which of the 15 theories are most applicable
    primary_theories: tuple[str, ...]
    secondary_theories: tuple[str, ...]

    # Extraction hints for Gemini/LLM
    extraction_focus: str
    example_actors: tuple[str, ...]
    example_events: tuple[str, ...]

    # Escalation indicators specific to this domain
    escalation_indicators: tuple[str, ...]
    de_escalation_indicators: tuple[str, ...]

    # Intervention approaches
    intervention_types: tuple[str, ...]

    # Benchmark question categories
    benchmark_categories: tuple[str, ...]


HUMAN_FRICTION = DomainSpec(
    domain=TacitusDomain.HUMAN_FRICTION,
    display_name="Human Friction",
    description=(
        "Interpersonal, workplace, commercial, and legal disputes. "
        "Focus on mediation, negotiation, interest-based resolution, and trust repair. "
        "Scale ranges from micro (individual) to meso (organizational/community)."
    ),
    subdomains=(
        "interpersonal", "workplace", "commercial",
        "legal", "family", "community",
    ),
    scale_range=("micro", "meso"),
    primary_node_types=(
        "Actor", "Conflict", "Event", "Issue", "Interest",
        "EmotionalState", "TrustState", "Process", "Outcome",
    ),
    secondary_node_types=(
        "Norm", "Narrative", "PowerDynamic", "Role", "Evidence",
    ),
    primary_edge_types=(
        "PARTY_TO", "HAS_INTEREST", "TRUSTS", "CAUSED",
        "PARTICIPATES_IN", "RESOLVED_THROUGH", "PRODUCES",
        "FEELS", "HAS_POWER_OVER",
    ),
    primary_theories=(
        "fisher_ury", "mayer_trust", "thomas_kilmann", "deutsch_cooperation",
        "plutchik", "glasl", "ury_brett_goldberg",
    ),
    secondary_theories=(
        "french_raven", "winslade_monk", "burton_basic_needs",
        "kriesberg", "pearl_causal",
    ),
    extraction_focus=(
        "Extract parties, their interests, emotions, trust levels, "
        "and resolution processes. Focus on underlying needs (WHY) "
        "not stated positions. Identify BATNA for each party. "
        "Track emotional escalation and trust dynamics over time."
    ),
    example_actors=(
        "employee", "manager", "team", "department", "company",
        "contractor", "client", "mediator", "arbiter", "counsel",
        "family member", "neighbor", "community group",
    ),
    example_events=(
        "complaint filed", "mediation session", "grievance hearing",
        "contract breach", "policy violation", "performance review",
        "settlement offer", "arbitration ruling", "apology",
        "trust breakdown", "escalation to management",
    ),
    escalation_indicators=(
        "formal_complaint", "legal_threat", "hr_escalation",
        "communication_breakdown", "third_party_involvement",
        "public_accusation", "resignation_threat", "litigation",
    ),
    de_escalation_indicators=(
        "direct_dialogue", "mediation_agreed", "apology_offered",
        "accommodation_made", "interest_alignment", "trust_rebuilt",
        "settlement_reached", "process_engagement",
    ),
    intervention_types=(
        "facilitation", "mediation", "conciliation", "coaching",
        "negotiation_support", "restorative_justice", "ombudsman",
        "peer_review", "grievance_procedure",
    ),
    benchmark_categories=(
        "party_identification", "interest_mapping", "emotion_detection",
        "trust_assessment", "escalation_tracking", "process_evaluation",
        "outcome_prediction", "batna_analysis",
    ),
)

CONFLICT_WARFARE = DomainSpec(
    domain=TacitusDomain.CONFLICT_WARFARE,
    display_name="Conflict & Warfare",
    description=(
        "Geopolitical, armed, political, and protracted social conflicts. "
        "Focus on escalation tracking, ripeness analysis, causal chains, "
        "and intervention design. "
        "Scale ranges from macro (national/international) to meta (civilizational)."
    ),
    subdomains=(
        "geopolitical", "armed_conflict", "political",
        "protracted_social", "insurgency", "hybrid_warfare",
    ),
    scale_range=("macro", "meta"),
    primary_node_types=(
        "Actor", "Conflict", "Event", "Issue", "Interest", "Norm",
        "Narrative", "Location", "Evidence", "Process", "Outcome",
    ),
    secondary_node_types=(
        "EmotionalState", "TrustState", "PowerDynamic", "Role",
    ),
    primary_edge_types=(
        "PARTY_TO", "CAUSED", "ALLIED_WITH", "OPPOSED_TO",
        "HAS_POWER_OVER", "VIOLATED", "OCCURRED_AT",
        "PARTICIPATES_IN", "ABOUT", "PART_OF",
    ),
    primary_theories=(
        "glasl", "zartman", "galtung", "azar_protracted",
        "kelman_problem_solving", "kriesberg", "lederach_transformation",
        "pearl_causal",
    ),
    secondary_theories=(
        "fisher_ury", "french_raven", "burton_basic_needs",
        "winslade_monk", "deutsch_cooperation",
    ),
    extraction_focus=(
        "Extract state and non-state actors, conflicts with Glasl staging, "
        "events with causal chains, norms/treaties with violation tracking, "
        "narratives and counter-narratives, power dynamics and alliances. "
        "Apply UCDP/ACLED coding standards. Track territorial and "
        "governmental incompatibilities."
    ),
    example_actors=(
        "state", "military", "non-state armed group", "militia",
        "peacekeeping force", "international organization", "NGO",
        "diplomatic envoy", "insurgent group", "coalition",
        "intelligence agency", "proxy force",
    ),
    example_events=(
        "military offensive", "ceasefire", "peace talks",
        "sanctions imposed", "treaty signed", "treaty violated",
        "territorial seizure", "civilian casualties", "arms transfer",
        "diplomatic recall", "UN resolution", "coup attempt",
    ),
    escalation_indicators=(
        "military_mobilization", "sanctions_imposed", "diplomatic_expulsion",
        "treaty_violation", "arms_buildup", "proxy_activation",
        "civilian_targeting", "territorial_expansion", "nuclear_escalation",
        "information_warfare", "economic_warfare",
    ),
    de_escalation_indicators=(
        "ceasefire_declared", "peace_talks_initiated", "sanctions_relief",
        "prisoner_exchange", "back_channel_contact", "confidence_building",
        "peacekeeping_deployment", "arms_control_agreement",
        "humanitarian_corridor", "ddr_program",
    ),
    intervention_types=(
        "preventive_diplomacy", "mediation", "arbitration",
        "peacekeeping", "peacebuilding", "sanctions",
        "arms_embargo", "humanitarian_intervention",
        "transitional_justice", "power_sharing",
    ),
    benchmark_categories=(
        "actor_identification", "conflict_classification", "escalation_assessment",
        "causal_chain_extraction", "norm_violation_detection", "alliance_mapping",
        "power_analysis", "ripeness_assessment", "intervention_design",
        "scenario_forecasting",
    ),
)


# ─── Domain Registry ──────────────────────────────────────────────────────────


DOMAIN_SPECS: dict[TacitusDomain, DomainSpec] = {
    TacitusDomain.HUMAN_FRICTION: HUMAN_FRICTION,
    TacitusDomain.CONFLICT_WARFARE: CONFLICT_WARFARE,
}


def detect_domain_from_scale(scale: str) -> TacitusDomain:
    """Infer domain from conflict scale."""
    if scale in ("micro", "meso"):
        return TacitusDomain.HUMAN_FRICTION
    return TacitusDomain.CONFLICT_WARFARE


def detect_domain_from_conflict_domain(domain: str) -> TacitusDomain:
    """Infer TACITUS domain from ConflictDomain enum value."""
    friction_domains = {"interpersonal", "workplace", "commercial", "legal"}
    if domain in friction_domains:
        return TacitusDomain.HUMAN_FRICTION
    return TacitusDomain.CONFLICT_WARFARE


def get_domain_spec(domain: TacitusDomain) -> DomainSpec:
    """Get the full specification for a domain."""
    return DOMAIN_SPECS[domain]


def get_theories_for_domain(domain: TacitusDomain) -> list[str]:
    """Get ordered list of theories (primary first, then secondary)."""
    spec = DOMAIN_SPECS[domain]
    return list(spec.primary_theories) + list(spec.secondary_theories)


def get_extraction_prompt_for_domain(domain: TacitusDomain) -> str:
    """Get domain-specific extraction focus text for LLM prompts."""
    return DOMAIN_SPECS[domain].extraction_focus
