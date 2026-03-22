"""
Schema Validation — Pydantic validation wrapper for extracted entities.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from pydantic import ValidationError

from dialectica_ontology.primitives import NODE_TYPES, ConflictNode
from dialectica_ontology.relationships import ConflictRelationship, validate_relationship
from dialectica_ontology.tiers import TIER_EDGES, TIER_NODES, OntologyTier

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of schema validation."""

    valid_nodes: list[ConflictNode] = field(default_factory=list)
    valid_edges: list[ConflictRelationship] = field(default_factory=list)
    invalid_entities: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def all_valid(self) -> bool:
        return len(self.errors) == 0 and len(self.invalid_entities) == 0


def validate_raw_nodes(
    raw_nodes: list[dict],
    tier: OntologyTier,
    workspace_id: str = "",
    tenant_id: str = "",
) -> ValidationResult:
    """Validate raw extracted node dicts against Pydantic models.

    Args:
        raw_nodes: List of dicts from Gemini extraction.
        tier: Ontology tier (determines which node types are allowed).
        workspace_id: Target workspace.
        tenant_id: Owning tenant.

    Returns:
        ValidationResult with valid nodes and error details for invalid ones.
    """
    result = ValidationResult()
    allowed_labels = TIER_NODES[tier]

    for raw in raw_nodes:
        label = raw.get("label", "")

        # Check label is allowed for this tier
        if label not in allowed_labels:
            result.invalid_entities.append(raw)
            result.errors.append(f"Node label '{label}' not allowed in {tier.value} tier")
            continue

        # Get the Pydantic model class
        cls = NODE_TYPES.get(label)
        if cls is None:
            result.invalid_entities.append(raw)
            result.errors.append(f"Unknown node label: '{label}'")
            continue

        # Attempt Pydantic validation
        try:
            node_data = dict(raw)
            node_data.setdefault("workspace_id", workspace_id)
            node_data.setdefault("tenant_id", tenant_id)
            node = cls.model_validate(node_data)
            result.valid_nodes.append(node)
        except ValidationError as e:
            result.invalid_entities.append(raw)
            for err in e.errors():
                loc = ".".join(str(part) for part in err["loc"])
                result.errors.append(f"{label}.{loc}: {err['msg']}")

    return result


def validate_raw_edges(
    raw_edges: list[dict],
    tier: OntologyTier,
    node_ids: set[str] | None = None,
    workspace_id: str = "",
    tenant_id: str = "",
) -> ValidationResult:
    """Validate raw extracted edge dicts against Pydantic models.

    Args:
        raw_edges: List of dicts from Gemini extraction.
        tier: Ontology tier.
        node_ids: Set of valid node IDs (for referential integrity check).
        workspace_id: Target workspace.
        tenant_id: Owning tenant.

    Returns:
        ValidationResult with valid edges and error details.
    """
    result = ValidationResult()
    allowed_types = TIER_EDGES[tier]

    for raw in raw_edges:
        edge_type = raw.get("type", "")

        if edge_type not in allowed_types:
            result.invalid_entities.append(raw)
            result.errors.append(f"Edge type '{edge_type}' not allowed in {tier.value} tier")
            continue

        try:
            edge_data = dict(raw)
            edge_data.setdefault("workspace_id", workspace_id)
            edge_data.setdefault("tenant_id", tenant_id)
            edge_data.setdefault("properties", edge_data.pop("properties", {}))
            edge = ConflictRelationship.model_validate(edge_data)

            # Validate against schema constraints
            schema_errors = validate_relationship(edge)
            if schema_errors:
                result.invalid_entities.append(raw)
                result.errors.extend(schema_errors)
                continue

            # Referential integrity
            if node_ids is not None:
                if edge.source_id not in node_ids:
                    result.invalid_entities.append(raw)
                    result.errors.append(f"Edge {edge.id}: source_id '{edge.source_id}' not found")
                    continue
                if edge.target_id not in node_ids:
                    result.invalid_entities.append(raw)
                    result.errors.append(f"Edge {edge.id}: target_id '{edge.target_id}' not found")
                    continue

            result.valid_edges.append(edge)
        except (ValidationError, ValueError) as e:
            result.invalid_entities.append(raw)
            result.errors.append(f"Edge validation error: {e}")

    return result
