"""
Theory Knowledge Graph — Node and edge types for the DIALECTICA theory layer.

Encodes conflict resolution theory as structured, queryable knowledge:
  TheoryConcept: Named concept from a framework (BATNA, Hurting Stalemate, etc.)
  ConflictPattern: Recurring pattern across conflicts (Escalation Spiral, etc.)
  AnalyticalProcedure: Step-by-step methodology (Stakeholder Mapping, etc.)

Theory graph edge types:
  BUILDS_ON: TheoryConcept -> TheoryConcept (intellectual lineage)
  CONTRADICTS: TheoryConcept -> TheoryConcept
  APPLIES_TO: TheoryConcept -> ConflictPattern
  DETECTS: AnalyticalProcedure -> ConflictPattern
  RECOMMENDS: ConflictPattern -> AnalyticalProcedure
  PREREQUISITE: AnalyticalProcedure -> AnalyticalProcedure
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProcedureStep(BaseModel):
    step_number: int
    title: str
    description: str
    required_data: list[str] = Field(default_factory=list)
    output: str = ""


class TheoryConcept(BaseModel):
    """A named concept from a conflict resolution theory framework."""
    id: str
    name: str
    framework_id: str
    definition: str
    examples: list[str] = Field(default_factory=list)
    related_conflict_node_types: list[str] = Field(default_factory=list)
    detection_indicators: list[str] = Field(default_factory=list)
    builds_on: list[str] = Field(default_factory=list)      # other concept IDs
    contradicts: list[str] = Field(default_factory=list)    # other concept IDs


class ConflictPattern(BaseModel):
    """A recurring structural pattern across conflicts."""
    id: str
    name: str
    description: str
    graph_signature: str  # Cypher/GQL pattern that detects it
    theory_concepts: list[str] = Field(default_factory=list)  # TheoryConcept IDs
    historical_examples: list[str] = Field(default_factory=list)
    intervention_strategies: list[str] = Field(default_factory=list)
    frequency: str = "common"  # "rare" | "occasional" | "common"


class AnalyticalProcedure(BaseModel):
    """A step-by-step analytical methodology from the practitioner literature."""
    id: str
    name: str
    source: str
    description: str
    steps: list[ProcedureStep] = Field(default_factory=list)
    required_data: list[str] = Field(default_factory=list)
    output_type: str
    detects_patterns: list[str] = Field(default_factory=list)  # ConflictPattern IDs
    prerequisites: list[str] = Field(default_factory=list)     # other procedure IDs
    time_required: str = "1-2 hours"
    skill_level: str = "intermediate"


class TheoryMatch(BaseModel):
    """Result of matching workspace patterns against theory graph."""
    pattern_id: str
    pattern_name: str
    confidence: float
    applicable_concepts: list[str] = Field(default_factory=list)
    recommended_procedures: list[str] = Field(default_factory=list)


class TheoryGuidance(BaseModel):
    """Framework-specific guidance contextualised to a workspace."""
    framework_id: str
    framework_name: str
    workspace_id: str
    applicable_concepts: list[TheoryConcept] = Field(default_factory=list)
    detected_patterns: list[ConflictPattern] = Field(default_factory=list)
    recommended_procedures: list[AnalyticalProcedure] = Field(default_factory=list)
    synthesis: str = ""


class RecommendedProcedure(BaseModel):
    """An analytical procedure recommended for a workspace's current state."""
    procedure: AnalyticalProcedure
    rationale: str
    priority: int = 1
    estimated_value: float = 0.5


# ---------------------------------------------------------------------------
# Theory graph edge type constants
# ---------------------------------------------------------------------------

THEORY_EDGE_BUILDS_ON = "BUILDS_ON"
THEORY_EDGE_CONTRADICTS = "CONTRADICTS"
THEORY_EDGE_APPLIES_TO = "APPLIES_TO"
THEORY_EDGE_DETECTS = "DETECTS"
THEORY_EDGE_RECOMMENDS = "RECOMMENDS"
THEORY_EDGE_PREREQUISITE = "PREREQUISITE"

THEORY_EDGE_TYPES = [
    THEORY_EDGE_BUILDS_ON,
    THEORY_EDGE_CONTRADICTS,
    THEORY_EDGE_APPLIES_TO,
    THEORY_EDGE_DETECTS,
    THEORY_EDGE_RECOMMENDS,
    THEORY_EDGE_PREREQUISITE,
]

# ---------------------------------------------------------------------------
# WORKSPACE_ID for the shared theory graph
# ---------------------------------------------------------------------------

THEORY_WORKSPACE_ID = "__theory__"
