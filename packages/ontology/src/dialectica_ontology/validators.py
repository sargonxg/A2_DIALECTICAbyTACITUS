"""
Conflict Grammar Validators — Structural constraint checking for the ontology.

Implements:
  - validate_relationship_types(): Check valid source→target type combinations
  - validate_subgraph(): Full structural constraint validation
  - validate_temporal_consistency(): CAUSED edge temporal ordering
  - validate_tier_compliance(): Node/edge types within selected tier

Based on cardinality and symbolic_rules from ontology.py EDGES and NODES dicts.
"""
from __future__ import annotations

# TODO: Implement in Prompt 3
