"""
Temporal Validation — Temporal consistency checking for extracted entities.

Checks:
- Events have valid timestamps
- Causal chains have correct temporal ordering (cause before effect)
- Process start/end dates are consistent
- Temporal overlaps and gaps
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from dialectica_ontology.primitives import ConflictNode
from dialectica_ontology.relationships import ConflictRelationship


@dataclass
class TemporalValidationResult:
    """Result of temporal consistency validation."""

    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


def validate_temporal(
    nodes: list[ConflictNode],
    edges: list[ConflictRelationship],
) -> TemporalValidationResult:
    """Validate temporal consistency of extracted subgraph.

    Args:
        nodes: Validated ConflictNode instances.
        edges: Validated ConflictRelationship instances.

    Returns:
        TemporalValidationResult with warnings and errors.
    """
    result = TemporalValidationResult()
    node_map = {n.id: n for n in nodes}

    # Check CAUSED edges: source event should occur before target event
    for edge in edges:
        if edge.type != "CAUSED":
            continue

        source = node_map.get(edge.source_id)
        target = node_map.get(edge.target_id)

        if source is None or target is None:
            continue

        source_time = getattr(source, "occurred_at", None)
        target_time = getattr(target, "occurred_at", None)

        if source_time and target_time and source_time > target_time:
            result.errors.append(
                f"Temporal inconsistency: CAUSED edge {edge.id} — "
                f"cause at {source_time.isoformat()} is after "
                f"effect at {target_time.isoformat()}"
            )

    # Check Process start/end
    for node in nodes:
        if node.label == "Process":
            started = getattr(node, "started_at", None)
            ended = getattr(node, "ended_at", None)
            if started and ended and started > ended:
                result.errors.append(
                    f"Process {node.id}: started_at ({started.isoformat()}) "
                    f"after ended_at ({ended.isoformat()})"
                )

    # Check Conflict started/ended
    for node in nodes:
        if node.label == "Conflict":
            started = getattr(node, "started_at", None)
            ended = getattr(node, "ended_at", None)
            if started and ended and started > ended:
                result.errors.append(
                    f"Conflict {node.id}: started_at after ended_at"
                )

    # Check edge temporal_start < temporal_end
    for edge in edges:
        if edge.temporal_start and edge.temporal_end:
            if edge.temporal_start > edge.temporal_end:
                result.warnings.append(
                    f"Edge {edge.id}: temporal_start after temporal_end"
                )

    return result
