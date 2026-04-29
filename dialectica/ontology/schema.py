"""Load the TACITUS core v1 YAML ontology contract."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

DEFAULT_ONTOLOGY_PATH = Path(__file__).resolve().parents[2] / "ontology" / "tacitus_core_v1.yaml"


def load_core_schema(path: str | Path | None = None) -> dict[str, Any]:
    schema_path = Path(path) if path else DEFAULT_ONTOLOGY_PATH
    with schema_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if not isinstance(loaded, dict):
        raise ValueError(f"Ontology schema at {schema_path} did not load as a mapping")
    return loaded


def core_primitive_names(path: str | Path | None = None) -> set[str]:
    schema = load_core_schema(path)
    primitives = schema.get("core_primitives", {})
    if not isinstance(primitives, dict):
        raise ValueError("core_primitives must be a mapping")
    return set(primitives)
