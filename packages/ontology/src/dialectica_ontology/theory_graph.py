"""
Theory Knowledge Graph — Node and edge types for the meta-layer theory graph.

This separate graph captures conflict resolution theory itself:
theorists, publications, concepts, methodologies, principles, and patterns.
It is shared across all tenants as the universal theory scaffold.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class TheoryNode(BaseModel):
    """Base for all theory graph nodes."""

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    id: str
    label: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TheoryConcept(TheoryNode):
    """A named concept from a theory (e.g., BATNA, Hurting Stalemate)."""

    label: str = "TheoryConcept"
    name: str
    framework_id: str
    description: str
    category: str = ""
    key_authors: list[str] = Field(default_factory=list)


class Theorist(TheoryNode):
    """A person who developed a conflict resolution theory."""

    label: str = "Theorist"
    name: str
    affiliation: str = ""
    key_works: list[str] = Field(default_factory=list)
    birth_year: int | None = None


class Publication(TheoryNode):
    """A key publication in conflict resolution theory."""

    label: str = "Publication"
    title: str
    year: int
    authors: list[str]
    publisher: str = ""
    isbn: str = ""


class Methodology(TheoryNode):
    """A method for conflict analysis or resolution."""

    label: str = "Methodology"
    name: str
    description: str
    applicable_stages: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)


class Principle(TheoryNode):
    """A normative principle for conflict resolution."""

    label: str = "Principle"
    name: str
    description: str
    source_framework: str = ""


class Pattern(TheoryNode):
    """A recurring conflict pattern recognized by theory."""

    label: str = "Pattern"
    name: str
    description: str
    indicators: list[str] = Field(default_factory=list)
    graph_signature: dict[str, Any] = Field(default_factory=dict)


# ─── Theory Edge Types ─────────────────────────────────────────────────────

THEORY_EDGE_TYPES = {
    "BUILDS_ON": {
        "source": "TheoryConcept",
        "target": "TheoryConcept",
        "description": "Intellectual lineage between concepts",
    },
    "CONTRADICTS": {
        "source": "TheoryConcept",
        "target": "TheoryConcept",
        "description": "Theoretical disagreement between concepts",
    },
    "AUTHORED_BY": {
        "source": "Publication",
        "target": "Theorist",
        "description": "Authorship relation",
    },
    "INTRODUCES": {
        "source": "Publication",
        "target": "TheoryConcept",
        "description": "Publication introduces a concept",
    },
    "APPLIES_VIA": {
        "source": "Methodology",
        "target": "TheoryConcept",
        "description": "Method applies a concept",
    },
    "EXEMPLIFIES": {
        "source": "Pattern",
        "target": "TheoryConcept",
        "description": "Pattern exemplifies a concept",
    },
    "PRESCRIBES": {
        "source": "Principle",
        "target": "Methodology",
        "description": "Principle prescribes a methodology",
    },
}

THEORY_NODE_TYPES = [
    TheoryConcept,
    Theorist,
    Publication,
    Methodology,
    Principle,
    Pattern,
]
