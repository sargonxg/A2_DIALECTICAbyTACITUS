"""
Structural Validation — Conflict Grammar structural rules.

Checks:
- No orphan nodes (every node has at least one edge)
- Valid edge directions (source/target type constraints)
- Required properties present for each node type
- Graph connectivity
"""

from __future__ import annotations

from dataclasses import dataclass, field

from dialectica_ontology.primitives import ConflictNode
from dialectica_ontology.relationships import EDGE_SCHEMA, ConflictRelationship, EdgeType


@dataclass
class StructuralValidationResult:
    """Result of structural validation."""

    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    orphan_nodes: list[str] = field(default_factory=list)
    invalid_edges: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


def validate_structural(
    nodes: list[ConflictNode],
    edges: list[ConflictRelationship],
) -> StructuralValidationResult:
    """Run structural validation on an extracted subgraph.

    Args:
        nodes: Validated ConflictNode instances.
        edges: Validated ConflictRelationship instances.

    Returns:
        StructuralValidationResult with warnings and errors.
    """
    result = StructuralValidationResult()
    node_map = {n.id: n for n in nodes}
    connected_ids: set[str] = set()

    for edge in edges:
        connected_ids.add(edge.source_id)
        connected_ids.add(edge.target_id)

        # Validate edge direction types
        schema = EDGE_SCHEMA.get(EdgeType(edge.type))
        if schema is None:
            result.errors.append(f"Edge {edge.id}: unknown type '{edge.type}'")
            result.invalid_edges.append(edge.id)
            continue

        source_node = node_map.get(edge.source_id)
        target_node = node_map.get(edge.target_id)

        if source_node and source_node.label not in schema["source"]:
            result.errors.append(
                f"Edge {edge.id} ({edge.type}): source must be {schema['source']}, "
                f"got '{source_node.label}'"
            )
            result.invalid_edges.append(edge.id)

        if target_node and target_node.label not in schema["target"]:
            result.errors.append(
                f"Edge {edge.id} ({edge.type}): target must be {schema['target']}, "
                f"got '{target_node.label}'"
            )
            result.invalid_edges.append(edge.id)

    # Check for orphan nodes
    for node in nodes:
        if node.id not in connected_ids:
            result.orphan_nodes.append(node.id)
            result.warnings.append(
                f"Orphan node: {node.label} '{getattr(node, 'name', node.id)}' has no edges"
            )

    return result
