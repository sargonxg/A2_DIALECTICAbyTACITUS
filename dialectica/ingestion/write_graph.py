"""Write extracted primitives through a graph adapter."""

from __future__ import annotations

from pathlib import Path

from dialectica.graph.base import GraphAdapter
from dialectica.ontology.models import GraphPrimitive


def write_graph(adapter: GraphAdapter, primitives: list[GraphPrimitive]) -> list[str]:
    adapter.initialize_schema()
    return adapter.write_primitives(primitives)


def write_jsonl(path: str | Path, primitives: list[GraphPrimitive]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for primitive in primitives:
            handle.write(primitive.model_dump_json() + "\n")
