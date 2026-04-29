"""In-memory graph adapter for tests and local dry runs."""

from __future__ import annotations

from collections import defaultdict

from dialectica.ontology.models import GraphPrimitive


class MemoryGraphAdapter:
    """Append-only in-memory graph store."""

    def __init__(self) -> None:
        self.nodes: dict[str, GraphPrimitive] = {}
        self.by_case: dict[tuple[str, str], list[str]] = defaultdict(list)

    def initialize_schema(self) -> None:
        return None

    def write_primitive(self, primitive: GraphPrimitive) -> str:
        data = primitive.model_dump()
        workspace_id = str(data.get("workspace_id") or "")
        case_id = str(data.get("case_id") or "")
        if not workspace_id or not case_id:
            raise ValueError("All graph writes require workspace_id and case_id")
        if "episode_id" in data and not data["episode_id"]:
            raise ValueError("Episode-scoped graph writes require episode_id")

        self.nodes[primitive.id] = primitive
        self.by_case[(workspace_id, case_id)].append(primitive.id)
        return primitive.id

    def write_primitives(self, primitives: list[GraphPrimitive]) -> list[str]:
        return [self.write_primitive(primitive) for primitive in primitives]

    def query(self, question: str, workspace_id: str, case_id: str) -> list[dict]:
        lowered = question.lower()
        items = [self.nodes[node_id] for node_id in self.by_case.get((workspace_id, case_id), [])]
        if "commitment" in lowered and "constrain" in lowered:
            return [
                item.model_dump(mode="json")
                for item in items
                if item.__class__.__name__ in {"Commitment", "Constraint"}
            ]
        if "changed" in lowered or "episode" in lowered:
            return [
                item.model_dump(mode="json")
                for item in items
                if item.__class__.__name__ in {"Episode", "ActorState", "Event"}
            ]
        return [item.model_dump(mode="json") for item in items]

    def episodes(self, workspace_id: str, case_id: str) -> list[dict]:
        return [
            self.nodes[node_id].model_dump(mode="json")
            for node_id in self.by_case.get((workspace_id, case_id), [])
            if self.nodes[node_id].__class__.__name__ == "Episode"
        ]

    def close(self) -> None:
        return None
