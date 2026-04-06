"""
DIALECTICA Ontology Package — TACITUS Core Ontology v2.0

The Conflict Grammar: 15 node types, 20 edge types, 25+ controlled vocabularies.
Provides Pydantic v2 models, StrEnum classes, tier configs, validators,
symbolic rules, and theory framework implementations.

Usage:
    from dialectica_ontology import Actor, Conflict, Event
    from dialectica_ontology.enums import ConflictDomain, GlaslStage
    from dialectica_ontology.tiers import OntologyTier
"""

__version__ = "2.1.0"

# Node types (primitives)
# Compatibility mappers
from dialectica_ontology.compatibility import (
    acled_actor_to_dialectica,
    acled_to_dialectica,
    cameo_event_to_dialectica,
    cameo_to_dialectica,
    dialectica_actor_to_acled,
    dialectica_to_acled,
    dialectica_to_cameo,
    dialectica_to_cameo_event,
    dialectica_to_plover,
    dialectica_to_ucdp_incompatibility,
    event_type_quadclass,
    plover_quadclass,
    plover_to_dialectica,
    ucdp_conflict_type_label,
    ucdp_conflict_type_to_domain,
    ucdp_conflict_type_to_violence,
    ucdp_to_dialectica_incompatibility,
    ucdp_to_dialectica_intensity,
)

# Confidence types
from dialectica_ontology.confidence import (
    Conclusion,
    ConfidenceType,
)

# Core enums (re-export most commonly used)
from dialectica_ontology.enums import (
    ActorType,
    ConflictDomain,
    ConflictMode,
    ConflictScale,
    ConflictStatus,
    Durability,
    EmotionIntensity,
    Enforceability,
    EventContext,
    EventMode,
    EventType,
    GlaslLevel,
    GlaslStage,
    Incompatibility,
    Intensity,
    InterestType,
    KriesbergPhase,
    NarrativeType,
    NormType,
    OutcomeType,
    PowerDomain,
    PrimaryEmotion,
    ProcessStatus,
    ProcessType,
    QuadClass,
    ResolutionApproach,
    RoleType,
    ViolenceType,
)
from dialectica_ontology.primitives import (
    NODE_TYPES,
    Actor,
    Conflict,
    ConflictNode,
    EmotionalState,
    Event,
    Evidence,
    Interest,
    Issue,
    Location,
    Narrative,
    Norm,
    Outcome,
    PowerDynamic,
    Process,
    Role,
    TrustState,
)

# Relationships
from dialectica_ontology.relationships import (
    EDGE_SCHEMA,
    ConflictRelationship,
    EdgeType,
    validate_relationship,
)

# Schema generators
from dialectica_ontology.schemas import (
    generate_cypher_ddl,
    generate_gql_schema,
    generate_json_schema,
    generate_spanner_ddl,
    generate_turtle,
)

# Theory frameworks
from dialectica_ontology.theory import (
    BurtonFramework,
    ConflictSnapshot,
    DeutschFramework,
    DiagnosticQuestion,
    FisherUryFramework,
    FrenchRavenFramework,
    GaltungFramework,
    GlaslFramework,
    Intervention,
    KriesbergFramework,
    LederachFramework,
    MayerTrustFramework,
    PearlCausalFramework,
    PlutchikFramework,
    TheoryAssessment,
    TheoryConcept,
    TheoryFramework,
    ThomasKilmannFramework,
    UryBrettGoldbergFramework,
    WinsladeMonkFramework,
    ZartmanFramework,
)

# Benchmark questions
from dialectica_ontology.benchmark_questions import (
    ALL_QUESTIONS,
    BenchmarkQuestion,
    CONFLICT_WARFARE_QUESTIONS,
    CROSS_DOMAIN_QUESTIONS,
    HUMAN_FRICTION_QUESTIONS,
    get_minimum_coverage_questions,
    get_questions_by_difficulty,
    get_questions_by_mode,
    get_questions_by_theory,
    get_questions_for_domain,
)

# ConflictCorpus
from dialectica_ontology.corpus import (
    ConflictCorpus,
    CorpusAnalytics,
    CorpusBenchmarkScore,
    SourceDocument,
)

# Domain specialization
from dialectica_ontology.domains import (
    CONFLICT_WARFARE,
    DOMAIN_SPECS,
    HUMAN_FRICTION,
    DomainSpec,
    FrictionSubdomain,
    TacitusDomain,
    WarfareSubdomain,
    detect_domain_from_conflict_domain,
    detect_domain_from_scale,
    get_domain_spec,
    get_extraction_prompt_for_domain,
    get_theories_for_domain,
)

# Tiers
from dialectica_ontology.tiers import (
    TIER_CONFIGS,
    TIER_EDGES,
    TIER_FEATURES,
    TIER_NODES,
    OntologyTier,
    get_available_edges,
    get_available_features,
    get_available_nodes,
)

# Validators
from dialectica_ontology.validators import (
    validate_relationship_types,
    validate_subgraph,
    validate_temporal_consistency,
    validate_tier_compliance,
)

__all__ = [
    # Version
    "__version__",
    # Base
    "ConflictNode",
    # 15 node types
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
    "NODE_TYPES",
    # Relationships
    "ConflictRelationship",
    "EdgeType",
    "EDGE_SCHEMA",
    "validate_relationship",
    # Enums
    "ActorType",
    "ConflictScale",
    "ConflictDomain",
    "ConflictStatus",
    "KriesbergPhase",
    "GlaslStage",
    "GlaslLevel",
    "Incompatibility",
    "ViolenceType",
    "Intensity",
    "EventType",
    "EventMode",
    "EventContext",
    "QuadClass",
    "InterestType",
    "NormType",
    "Enforceability",
    "ProcessType",
    "ResolutionApproach",
    "ProcessStatus",
    "OutcomeType",
    "Durability",
    "PrimaryEmotion",
    "EmotionIntensity",
    "NarrativeType",
    "ConflictMode",
    "PowerDomain",
    "RoleType",
    # Tiers
    "OntologyTier",
    "TIER_NODES",
    "TIER_EDGES",
    "TIER_FEATURES",
    "TIER_CONFIGS",
    "get_available_nodes",
    "get_available_edges",
    "get_available_features",
    # Validators
    "validate_relationship_types",
    "validate_subgraph",
    "validate_temporal_consistency",
    "validate_tier_compliance",
    # Schema generators
    "generate_cypher_ddl",
    "generate_spanner_ddl",
    "generate_gql_schema",
    "generate_json_schema",
    "generate_turtle",
    # Theory frameworks
    "TheoryFramework",
    "TheoryConcept",
    "ConflictSnapshot",
    "TheoryAssessment",
    "Intervention",
    "DiagnosticQuestion",
    "GlaslFramework",
    "FisherUryFramework",
    "KriesbergFramework",
    "GaltungFramework",
    "LederachFramework",
    "ZartmanFramework",
    "DeutschFramework",
    "ThomasKilmannFramework",
    "FrenchRavenFramework",
    "MayerTrustFramework",
    "PlutchikFramework",
    "PearlCausalFramework",
    "WinsladeMonkFramework",
    "UryBrettGoldbergFramework",
    "BurtonFramework",
    # Confidence types
    "ConfidenceType",
    "Conclusion",
    # Domains
    "TacitusDomain",
    "FrictionSubdomain",
    "WarfareSubdomain",
    "FrictionSubdomain",
    "DomainSpec",
    "DOMAIN_SPECS",
    "HUMAN_FRICTION",
    "CONFLICT_WARFARE",
    "detect_domain_from_scale",
    "detect_domain_from_conflict_domain",
    "get_domain_spec",
    "get_theories_for_domain",
    "get_extraction_prompt_for_domain",
    # ConflictCorpus
    "ConflictCorpus",
    "CorpusAnalytics",
    "CorpusBenchmarkScore",
    "SourceDocument",
    # Benchmark Questions
    "BenchmarkQuestion",
    "ALL_QUESTIONS",
    "CROSS_DOMAIN_QUESTIONS",
    "HUMAN_FRICTION_QUESTIONS",
    "CONFLICT_WARFARE_QUESTIONS",
    "get_questions_for_domain",
    "get_questions_by_mode",
    "get_questions_by_theory",
    "get_questions_by_difficulty",
    "get_minimum_coverage_questions",
    # Compatibility mappers
    "plover_to_dialectica",
    "dialectica_to_plover",
    "plover_quadclass",
    "event_type_quadclass",
    "acled_to_dialectica",
    "dialectica_to_acled",
    "acled_actor_to_dialectica",
    "dialectica_actor_to_acled",
    "cameo_to_dialectica",
    "dialectica_to_cameo",
    "cameo_event_to_dialectica",
    "dialectica_to_cameo_event",
    "ucdp_to_dialectica_incompatibility",
    "dialectica_to_ucdp_incompatibility",
    "ucdp_to_dialectica_intensity",
    "ucdp_conflict_type_to_domain",
    "ucdp_conflict_type_to_violence",
    "ucdp_conflict_type_label",
]
