"""
Conflict Relationships — Pydantic v2 models for all 20 DIALECTICA edge types.

Implements: ConflictRelationship base + typed subclasses for all 20 edges:
PARTY_TO, PARTICIPATES_IN, HAS_INTEREST, PART_OF, CAUSED, AT_LOCATION, WITHIN,
GOVERNED_BY, VIOLATES, RESOLVED_THROUGH, PRODUCES, ALLIED_WITH, OPPOSED_TO,
HAS_POWER_OVER, MEMBER_OF, EXPERIENCES, TRUSTS, PROMOTES, ABOUT, EVIDENCED_BY

Theoretical basis: TACITUS Core Ontology v2.0 EDGES dict (see ontology.py)
"""
from __future__ import annotations

# TODO: Implement in Prompt 2
