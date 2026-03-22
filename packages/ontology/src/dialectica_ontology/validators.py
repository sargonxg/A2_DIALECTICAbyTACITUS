"""
Conflict Grammar Validators — Structural constraint checking for the ontology.

Implements:
  - validate_relationship_types(): Check valid source->target type combinations
  - validate_subgraph(): Full structural constraint validation
  - validate_temporal_consistency(): CAUSED edge temporal ordering
  - validate_tier_compliance(): Node/edge types within selected tier
"""

from __future__ import annotations

from datetime import datetime

from dialectica_ontology.primitives import ConflictNode
from dialectica_ontology.relationships import (
    ConflictRelationship,
    EdgeType,
    validate_relationship,
)
from dialectica_ontology.tiers import OntologyTier, get_available_edges, get_available_nodes


def validate_relationship_types(rel: ConflictRelationship) -> list[str]:
    """Check valid source->target type combinations for a relationship."""
    return validate_relationship(rel)


def validate_subgraph(
    nodes: list[ConflictNode],
    relationships: list[ConflictRelationship],
) -> list[str]:
    """Full structural constraint validation for a subgraph."""
    errors: list[str] = []
    node_ids = {n.id for n in nodes}

    for rel in relationships:
        # Check source/target exist
        if rel.source_id not in node_ids:
            errors.append(f"Relationship {rel.id}: source_id '{rel.source_id}' not in graph")
        if rel.target_id not in node_ids:
            errors.append(f"Relationship {rel.id}: target_id '{rel.target_id}' not in graph")
        # Check edge schema
        errors.extend(validate_relationship(rel))

    return errors


def validate_temporal_consistency(
    relationships: list[ConflictRelationship],
    node_timestamps: dict[str, datetime],
) -> list[str]:
    """Validate CAUSED edge temporal ordering: cause must precede effect."""
    errors: list[str] = []
    for rel in relationships:
        if rel.type == EdgeType.CAUSED or rel.type == "CAUSED":
            source_ts = node_timestamps.get(rel.source_id)
            target_ts = node_timestamps.get(rel.target_id)
            if source_ts and target_ts and source_ts > target_ts:
                errors.append(
                    f"CAUSED edge {rel.id}: source event at {source_ts} is after "
                    f"target event at {target_ts} (cause must precede effect)"
                )
    return errors


def validate_tier_compliance(
    nodes: list[ConflictNode],
    relationships: list[ConflictRelationship],
    tier: OntologyTier,
) -> list[str]:
    """Check that all node/edge types are within the selected tier."""
    errors: list[str] = []
    allowed_nodes = get_available_nodes(tier)
    allowed_edges = get_available_edges(tier)

    for node in nodes:
        if node.label and node.label not in allowed_nodes:
            errors.append(
                f"Node '{node.id}' has label '{node.label}' not available in {tier.value} tier"
            )

    for rel in relationships:
        edge_name = rel.type if isinstance(rel.type, str) else rel.type.value
        if edge_name not in allowed_edges:
            errors.append(
                f"Edge '{rel.id}' has type '{edge_name}' not available in {tier.value} tier"
            )

    return errors
