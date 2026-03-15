"""
Theory Framework Base — Abstract base class for all 15 DIALECTICA theory modules.

Defines:
  TheoryFramework(ABC): Abstract base with describe(), assess(), score()
  TheoryConcept: Name, description, related node/edge types
  ConflictSnapshot: Workspace summary for theory analysis
  TheoryAssessment: Results with findings, confidence, recommendations
  Intervention: Specific intervention recommendation with theory basis
  DiagnosticQuestion: Framework-specific diagnostic question

All 15 theory modules inherit from TheoryFramework and implement real analytical logic.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TheoryConcept:
    """A named concept within a theory framework."""

    name: str
    description: str
    related_node_types: list[str] = field(default_factory=list)
    related_edge_types: list[str] = field(default_factory=list)


@dataclass
class ConflictSnapshot:
    """Workspace summary passed to theory frameworks for analysis."""

    parties: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    emotions: list[str] = field(default_factory=list)
    power_dynamics: dict[str, Any] = field(default_factory=dict)
    history: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class Intervention:
    """A specific intervention recommendation grounded in theory."""

    name: str
    description: str
    theory_basis: str
    priority: str = "medium"  # low, medium, high, critical
    prerequisites: list[str] = field(default_factory=list)


@dataclass
class DiagnosticQuestion:
    """A framework-specific diagnostic question for conflict analysis."""

    question: str
    framework: str
    purpose: str
    response_type: str = "open"  # open, scale, boolean, choice


@dataclass
class TheoryAssessment:
    """Results from a theory framework assessment."""

    framework_name: str
    findings: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    recommendations: list[Intervention] = field(default_factory=list)
    diagnostic_questions: list[DiagnosticQuestion] = field(default_factory=list)
    raw_score: float = 0.0


class TheoryFramework(ABC):
    """Abstract base class for all DIALECTICA theory framework implementations.

    Each subclass models a specific conflict resolution theory and provides
    analytical methods to classify, assess, and score conflict situations.
    """

    name: str = ""
    author: str = ""
    key_concepts: list[str] = []

    def __init__(self) -> None:
        """Initialize the framework. Subclasses should set name, author, key_concepts."""

    @abstractmethod
    def describe(self) -> str:
        """Return a human-readable description of this theory framework."""
        ...

    @abstractmethod
    def assess(self, graph_context: dict) -> dict:
        """Analyze a conflict context and return structured assessment results.

        Args:
            graph_context: Dictionary containing conflict graph data such as
                parties, issues, emotions, power dynamics, and history.

        Returns:
            Dictionary with assessment findings keyed by aspect name.
        """
        ...

    @abstractmethod
    def score(self, graph_context: dict) -> float:
        """Compute a relevance/applicability score for this framework.

        Args:
            graph_context: Dictionary containing conflict graph data.

        Returns:
            Float between 0.0 and 1.0 indicating how relevant this framework
            is to the given conflict context.
        """
        ...

    def get_concepts(self) -> list[TheoryConcept]:
        """Return the theory concepts defined by this framework.

        Subclasses may override to provide richer concept metadata.
        """
        return [
            TheoryConcept(name=c, description=f"{c} concept from {self.name}")
            for c in self.key_concepts
        ]

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        """Return diagnostic questions for this framework.

        Subclasses may override to provide framework-specific questions.
        """
        return []

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name!r}, author={self.author!r})>"
