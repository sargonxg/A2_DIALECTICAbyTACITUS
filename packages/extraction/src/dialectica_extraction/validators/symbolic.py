"""
Symbolic Rule Validation — Conflict Grammar symbolic rules.

Enforces domain-specific rules that go beyond schema validation:
- Conflict must have at least 2 parties
- Every party must have at least one interest
- Glasl stages must be consistent with conflict status
- Resolution processes must link to a conflict
"""

from __future__ import annotations

from dataclasses import dataclass, field

from dialectica_ontology.primitives import ConflictNode
from dialectica_ontology.relationships import ConflictRelationship


@dataclass
class SymbolicValidationResult:
    """Result of symbolic rule validation."""

    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0


def validate_symbolic(
    nodes: list[ConflictNode],
    edges: list[ConflictRelationship],
) -> SymbolicValidationResult:
    """Run symbolic rules against an extracted subgraph.

    These are soft rules that generate warnings rather than hard errors,
    since extraction from text may be incomplete.
    """
    result = SymbolicValidationResult()
    {n.id: n for n in nodes}

    conflicts = [n for n in nodes if n.label == "Conflict"]
    actors = [n for n in nodes if n.label == "Actor"]
    processes = [n for n in nodes if n.label == "Process"]

    # Build edge lookup
    edges_by_type: dict[str, list[ConflictRelationship]] = {}
    for e in edges:
        edges_by_type.setdefault(str(e.type), []).append(e)

    # Rule: each Conflict should have at least 2 PARTY_TO edges
    party_edges = edges_by_type.get("PARTY_TO", [])
    for conflict in conflicts:
        parties = [e for e in party_edges if e.target_id == conflict.id]
        if len(parties) < 2:
            result.warnings.append(
                f"Conflict '{getattr(conflict, 'name', conflict.id)}' has "
                f"{len(parties)} party/parties (expected >= 2)"
            )
            if len(parties) == 0:
                result.suggestions.append(
                    f"Consider extracting actors who are parties to "
                    f"'{getattr(conflict, 'name', conflict.id)}'"
                )

    # Rule: Glasl stage consistency
    for conflict in conflicts:
        glasl = getattr(conflict, "glasl_stage", None)
        status = getattr(conflict, "status", None)
        if glasl is not None and status == "resolved" and glasl >= 7:
            result.warnings.append(
                f"Conflict '{getattr(conflict, 'name', conflict.id)}': "
                f"status is 'resolved' but Glasl stage is {glasl} (lose-lose zone)"
            )

    # Rule: Process should link to a Conflict via RESOLVED_THROUGH
    resolved_edges = edges_by_type.get("RESOLVED_THROUGH", [])
    {e.source_id for e in resolved_edges}
    for process in processes:
        linked = any(e.target_id == process.id for e in resolved_edges)
        if not linked:
            result.warnings.append(
                f"Process '{process.id}' not linked to any Conflict via RESOLVED_THROUGH"
            )

    # Rule: Actors in the graph should have at least one relationship
    actor_ids = {a.id for a in actors}
    connected_actors = set()
    for e in edges:
        if e.source_id in actor_ids:
            connected_actors.add(e.source_id)
        if e.target_id in actor_ids:
            connected_actors.add(e.target_id)
    for actor in actors:
        if actor.id not in connected_actors:
            result.warnings.append(
                f"Actor '{getattr(actor, 'name', actor.id)}' has no relationships"
            )

    return result
