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
]
