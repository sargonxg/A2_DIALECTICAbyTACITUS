"""
Theory Framework Base — Abstract base class for all 15 DIALECTICA theory modules.

Defines:
  TheoryFramework(ABC): Abstract base with classify() + recommend() + diagnostic_questions()
  TheoryConcept: Name, description, related node/edge types
  ConflictSnapshot: Workspace summary for theory analysis
  TheoryAssessment: Results with findings, confidence, recommendations
  Intervention: Specific intervention recommendation with theory basis
  DiagnosticQuestion: Framework-specific diagnostic question

All 15 theory modules inherit from TheoryFramework and implement real analytical logic.
"""
from __future__ import annotations

# TODO: Implement in Prompt 4
# from abc import ABC, abstractmethod
