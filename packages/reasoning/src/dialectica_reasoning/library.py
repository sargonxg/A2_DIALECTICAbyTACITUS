"""Curated reasoning question library for the May demo theatre.

The library is editorial data, not generated benchmark filler. API adapters load
it at startup/request time and combine it with the live graph reasoning engine.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CuratedQuestion:
    id: str
    scenario_id: str
    text: str
    stake: str
    academic_anchor: str
    primary_framework: str
    symbolic_rules: tuple[str, ...]
    counterfactual_supported: bool
    similarity_supported: bool


def default_library_path() -> Path:
    configured = os.getenv("DIALECTICA_REASONING_LIBRARY_PATH")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parents[4] / "data" / "seed" / "reasoning_library.json"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
        raise ValueError(f"Reasoning library {path} must contain a questions array.")
    return data


def load_curated_library(path: Path | None = None) -> dict[str, CuratedQuestion]:
    resolved = path or default_library_path()
    data = _load_json(resolved)
    questions: dict[str, CuratedQuestion] = {}
    for raw in data["questions"]:
        if not isinstance(raw, dict):
            raise ValueError("Each curated question must be an object.")
        question = CuratedQuestion(
            id=str(raw["id"]),
            scenario_id=str(raw["scenario_id"]),
            text=str(raw["text"]),
            stake=str(raw["stake"]),
            academic_anchor=str(raw["academic_anchor"]),
            primary_framework=str(raw["primary_framework"]),
            symbolic_rules=tuple(str(rule) for rule in raw.get("symbolic_rules", [])),
            counterfactual_supported=bool(raw.get("counterfactual_supported", False)),
            similarity_supported=bool(raw.get("similarity_supported", False)),
        )
        if question.id in questions:
            raise ValueError(f"Duplicate curated question id: {question.id}")
        questions[question.id] = question
    if len(questions) != 23:
        raise ValueError(f"Expected 23 curated questions, found {len(questions)}.")
    return questions


@lru_cache(maxsize=1)
def get_curated_library() -> dict[str, CuratedQuestion]:
    return load_curated_library()
