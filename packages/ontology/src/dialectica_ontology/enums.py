"""
Conflict Enumerations — StrEnum classes for all 25+ DIALECTICA controlled vocabularies.

Implements ALL values from ENUMS dict in ontology.py:
  ActorType, ConflictScale, ConflictDomain, ConflictStatus, KriesbergPhase,
  GlaslStage (IntEnum), GlaslLevel, Incompatibility, ViolenceType, Intensity,
  EventType (16 PLOVER types), EventMode, EventContext, QuadClass,
  InterestType, NormType, Enforceability, ProcessType (13 ADR types),
  ResolutionApproach, ProcessStatus, OutcomeType (11 types), Durability,
  PrimaryEmotion (Plutchik 8), EmotionIntensity, NarrativeType,
  ConflictMode (Thomas-Kilmann), PowerDomain (French/Raven), RoleType (18 types)

Also includes metadata constants:
  PLUTCHIK_DYADS, THOMAS_KILMANN_MAPPING, GLASL_METADATA
"""
from __future__ import annotations

# TODO: Implement in Prompt 2
# from enum import StrEnum, IntEnum
