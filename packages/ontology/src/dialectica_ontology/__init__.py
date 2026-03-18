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

__version__ = "2.0.1"

# Node types (primitives)
from dialectica_ontology.primitives import (
    ConflictNode,
    Actor,
    Conflict,
    Event,
    Issue,
    Interest,
    Norm,
    Process,
    Outcome,
    Narrative,
    EmotionalState,
    TrustState,
    PowerDynamic,
    Location,
    Evidence,
    Role,
    NODE_TYPES,
)

# Relationships
from dialectica_ontology.relationships import (
    ConflictRelationship,
    EdgeType,
    EDGE_SCHEMA,
    validate_relationship,
)

# Core enums (re-export most commonly used)
from dialectica_ontology.enums import (
    ActorType,
    ConflictScale,
    ConflictDomain,
    ConflictStatus,
    KriesbergPhase,
    GlaslStage,
    GlaslLevel,
    Incompatibility,
    ViolenceType,
    Intensity,
    EventType,
    EventMode,
    EventContext,
    QuadClass,
    InterestType,
    NormType,
    Enforceability,
    ProcessType,
    ResolutionApproach,
    ProcessStatus,
    OutcomeType,
    Durability,
    PrimaryEmotion,
    EmotionIntensity,
    NarrativeType,
    ConflictMode,
    PowerDomain,
    RoleType,
)

# Tiers
from dialectica_ontology.tiers import (
    OntologyTier,
    TIER_NODES,
    TIER_EDGES,
    TIER_FEATURES,
    TIER_CONFIGS,
    get_available_nodes,
    get_available_edges,
    get_available_features,
)

# Validators
from dialectica_ontology.validators import (
    validate_relationship_types,
    validate_subgraph,
    validate_temporal_consistency,
    validate_tier_compliance,
)

# Schema generators
from dialectica_ontology.schemas import (
    generate_cypher_ddl,
    generate_spanner_ddl,
    generate_gql_schema,
    generate_json_schema,
    generate_turtle,
)

# Theory frameworks
from dialectica_ontology.theory import (
    TheoryFramework,
    TheoryConcept,
    ConflictSnapshot,
    TheoryAssessment,
    Intervention,
    DiagnosticQuestion,
    GlaslFramework,
    FisherUryFramework,
    KriesbergFramework,
    GaltungFramework,
    LederachFramework,
    ZartmanFramework,
    DeutschFramework,
    ThomasKilmannFramework,
    FrenchRavenFramework,
    MayerTrustFramework,
    PlutchikFramework,
    PearlCausalFramework,
    WinsladeMonkFramework,
    UryBrettGoldbergFramework,
    BurtonFramework,
)

# Compatibility mappers
from dialectica_ontology.compatibility import (
    plover_to_dialectica,
    dialectica_to_plover,
    plover_quadclass,
    event_type_quadclass,
    acled_to_dialectica,
    dialectica_to_acled,
    acled_actor_to_dialectica,
    dialectica_actor_to_acled,
    cameo_to_dialectica,
    dialectica_to_cameo,
    cameo_event_to_dialectica,
    dialectica_to_cameo_event,
    ucdp_to_dialectica_incompatibility,
    dialectica_to_ucdp_incompatibility,
    ucdp_to_dialectica_intensity,
    ucdp_conflict_type_to_domain,
    ucdp_conflict_type_to_violence,
    ucdp_conflict_type_label,
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
