"""Reasoning queries over the Cozo-style mirror."""

from __future__ import annotations

from typing import Any

from app.graph_reasoning.cozo_client import CozoReasoningClient
from app.graph_reasoning.schema import ObjectKind


class ReasoningQueries:
    """Datalog-style query facade over relation-shaped mirror data."""

    def __init__(self, cozo: CozoReasoningClient) -> None:
        self.cozo = cozo

    def actor_profile(self, actor_id: str, workspace_id: str | None = None) -> dict[str, Any]:
        actor = self.cozo.get_object(actor_id)
        edges = self.cozo.edges_for(actor_id, workspace_id)
        related = [self.cozo.get_object(_other_id(edge, actor_id)) for edge in edges]
        related = [item for item in related if item is not None]
        return {
            "actor": actor,
            "claims": _filter_related(related, ObjectKind.CLAIM),
            "interests": _filter_related(related, ObjectKind.INTEREST),
            "constraints": _filter_related(related, ObjectKind.CONSTRAINT),
            "leverage": _filter_related(related, ObjectKind.LEVERAGE),
            "commitments": _filter_related(related, ObjectKind.COMMITMENT),
            "events": _filter_related(related, ObjectKind.EVENT),
            "narratives": _filter_related(related, ObjectKind.NARRATIVE),
            "edges": edges,
        }

    def indirect_constraints(
        self, actor_id: str, workspace_id: str | None = None
    ) -> dict[str, Any]:
        direct_edges = self.cozo.edges_for(actor_id, workspace_id)
        direct_constraints = []
        indirect_constraints = []
        seen = set()
        for edge in direct_edges:
            other = self.cozo.get_object(_other_id(edge, actor_id))
            if other and other.get("kind") == "Constraint":
                direct_constraints.append(other)
                seen.add(other["id"])
            if other and other.get("kind") in {"Commitment", "Leverage", "Claim"}:
                for second_edge in self.cozo.edges_for(other["id"], workspace_id):
                    candidate = self.cozo.get_object(_other_id(second_edge, other["id"]))
                    if (
                        candidate
                        and candidate.get("kind") == "Constraint"
                        and candidate["id"] not in seen
                    ):
                        indirect_constraints.append(
                            {
                                "constraint": candidate,
                                "via": other,
                                "path": [actor_id, other["id"], candidate["id"]],
                            }
                        )
                        seen.add(candidate["id"])
        return {
            "actor_id": actor_id,
            "direct": direct_constraints,
            "indirect": indirect_constraints,
        }

    def leverage_map(self, actor_id: str, workspace_id: str | None = None) -> dict[str, Any]:
        profile = self.actor_profile(actor_id, workspace_id)
        outgoing = [edge for edge in profile["edges"] if edge.get("source_id") == actor_id]
        incoming = [edge for edge in profile["edges"] if edge.get("target_id") == actor_id]
        return {
            "actor_id": actor_id,
            "leverage": profile["leverage"],
            "outgoing": outgoing,
            "incoming": incoming,
            "targets": [
                self.cozo.get_object(edge.get("target_id", ""))
                for edge in outgoing
                if edge.get("kind") in {"HAS_LEVERAGE", "TARGETS"}
            ],
        }

    def provenance_trace(self, object_id: str, workspace_id: str | None = None) -> dict[str, Any]:
        obj = self.cozo.get_object(object_id)
        if obj is None:
            return {
                "object_id": object_id,
                "object": None,
                "sources": [],
                "evidence": [],
                "edges": [],
            }
        source_ids = set(obj.get("source_ids", []))
        edges = self.cozo.edges_for(object_id, workspace_id)
        for edge in edges:
            source_ids.update(edge.get("source_ids", []))
        linked = [self.cozo.get_object(source_id) for source_id in source_ids]
        linked = [item for item in linked if item is not None]
        return {
            "object_id": object_id,
            "object": obj,
            "sources": [item for item in linked if item.get("kind") == "Source"],
            "evidence": [item for item in linked if item.get("kind") == "Evidence"],
            "edges": edges,
        }

    def timeline(
        self,
        actor_ids: list[str],
        start: str | None = None,
        end: str | None = None,
        workspace_id: str | None = None,
    ) -> dict[str, Any]:
        return {
            "actor_ids": actor_ids,
            "events": self.cozo.timeline(
                actor_ids, start=start, end=end, workspace_id=workspace_id
            ),
        }

    def changed_since(self, timestamp: str, workspace_id: str | None = None) -> dict[str, Any]:
        return self.cozo.changed_since(timestamp, workspace_id=workspace_id)


def _other_id(edge: dict[str, Any], object_id: str) -> str:
    if edge.get("source_id") == object_id:
        return str(edge.get("target_id", ""))
    return str(edge.get("source_id", ""))


def _filter_related(items: list[dict[str, Any]], kind: ObjectKind) -> list[dict[str, Any]]:
    return [item for item in items if item.get("kind") == kind.value]
