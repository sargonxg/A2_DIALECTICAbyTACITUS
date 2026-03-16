"""
Conflict Relationships — Pydantic v2 models for all 20 DIALECTICA edge types.

Implements: ConflictRelationship base + EdgeType enum + EDGE_SCHEMA validation.
All 20 edges from ontology.py EDGES{} with source/target constraints.

Theoretical basis: TACITUS Core Ontology v2.0 EDGES dict (see ontology.py)
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from ulid import ULID


def _ulid() -> str:
    return str(ULID())


class EdgeType(StrEnum):
    """All 20 DIALECTICA edge types."""
    PARTY_TO = "PARTY_TO"
    PARTICIPATES_IN = "PARTICIPATES_IN"
    HAS_INTEREST = "HAS_INTEREST"
    PART_OF = "PART_OF"
    CAUSED = "CAUSED"
    AT_LOCATION = "AT_LOCATION"
    WITHIN = "WITHIN"
    ALLIED_WITH = "ALLIED_WITH"
    OPPOSED_TO = "OPPOSED_TO"
    HAS_POWER_OVER = "HAS_POWER_OVER"
    MEMBER_OF = "MEMBER_OF"
    GOVERNED_BY = "GOVERNED_BY"
    VIOLATES = "VIOLATES"
    RESOLVED_THROUGH = "RESOLVED_THROUGH"
    PRODUCES = "PRODUCES"
    EXPERIENCES = "EXPERIENCES"
    TRUSTS = "TRUSTS"
    PROMOTES = "PROMOTES"
    ABOUT = "ABOUT"
    EVIDENCED_BY = "EVIDENCED_BY"


# Edge schema: (valid_source_labels, valid_target_labels, required_properties, optional_properties)
EDGE_SCHEMA: dict[EdgeType, dict[str, Any]] = {
    EdgeType.PARTY_TO: {
        "source": ["Actor"],
        "target": ["Conflict"],
        "required": [],
        "optional": ["role", "side", "joined_at", "left_at"],
    },
    EdgeType.PARTICIPATES_IN: {
        "source": ["Actor"],
        "target": ["Event"],
        "required": [],
        "optional": ["role_type", "influence"],
    },
    EdgeType.HAS_INTEREST: {
        "source": ["Actor"],
        "target": ["Interest"],
        "required": [],
        "optional": ["priority", "in_conflict", "stated"],
    },
    EdgeType.PART_OF: {
        "source": ["Event"],
        "target": ["Conflict"],
        "required": [],
        "optional": [],
    },
    EdgeType.CAUSED: {
        "source": ["Event"],
        "target": ["Event"],
        "required": [],
        "optional": ["mechanism", "strength", "lag", "confidence"],
    },
    EdgeType.AT_LOCATION: {
        "source": ["Event"],
        "target": ["Location"],
        "required": [],
        "optional": ["precision"],
    },
    EdgeType.WITHIN: {
        "source": ["Location"],
        "target": ["Location"],
        "required": [],
        "optional": [],
    },
    EdgeType.ALLIED_WITH: {
        "source": ["Actor"],
        "target": ["Actor"],
        "required": [],
        "optional": ["strength", "formality", "since", "confidence"],
    },
    EdgeType.OPPOSED_TO: {
        "source": ["Actor"],
        "target": ["Actor"],
        "required": [],
        "optional": ["intensity", "since"],
    },
    EdgeType.HAS_POWER_OVER: {
        "source": ["Actor"],
        "target": ["Actor"],
        "required": [],
        "optional": ["power_dynamic_id", "domain", "magnitude"],
    },
    EdgeType.MEMBER_OF: {
        "source": ["Actor"],
        "target": ["Actor"],
        "required": [],
        "optional": ["role", "since", "until"],
    },
    EdgeType.GOVERNED_BY: {
        "source": ["Conflict"],
        "target": ["Norm"],
        "required": [],
        "optional": ["applicability"],
    },
    EdgeType.VIOLATES: {
        "source": ["Event"],
        "target": ["Norm"],
        "required": [],
        "optional": ["severity", "intentional"],
    },
    EdgeType.RESOLVED_THROUGH: {
        "source": ["Conflict"],
        "target": ["Process"],
        "required": [],
        "optional": ["initiated_at", "initiated_by"],
    },
    EdgeType.PRODUCES: {
        "source": ["Process"],
        "target": ["Outcome"],
        "required": [],
        "optional": [],
    },
    EdgeType.EXPERIENCES: {
        "source": ["Actor"],
        "target": ["EmotionalState"],
        "required": [],
        "optional": ["context_event_id", "context_conflict_id"],
    },
    EdgeType.TRUSTS: {
        "source": ["Actor"],
        "target": ["Actor"],
        "required": [],
        "optional": ["trust_state_id", "overall_trust"],
    },
    EdgeType.PROMOTES: {
        "source": ["Actor"],
        "target": ["Narrative"],
        "required": [],
        "optional": ["strength", "since"],
    },
    EdgeType.ABOUT: {
        "source": ["Narrative"],
        "target": ["Conflict"],
        "required": [],
        "optional": [],
    },
    EdgeType.EVIDENCED_BY: {
        "source": ["Event"],
        "target": ["Evidence"],
        "required": [],
        "optional": ["relevance"],
    },
}


class ConflictRelationship(BaseModel):
    """Base class for all DIALECTICA edge types."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    id: str = Field(default_factory=_ulid)
    type: EdgeType
    source_id: str
    target_id: str
    source_label: str = ""
    target_label: str = ""
    workspace_id: str = ""
    tenant_id: str = ""
    properties: dict[str, Any] = Field(default_factory=dict)
    weight: float = Field(default=1.0, ge=0.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    temporal_start: datetime | None = None
    temporal_end: datetime | None = None
    source_text: str | None = None


def validate_relationship(rel: ConflictRelationship) -> list[str]:
    """Validate a relationship against EDGE_SCHEMA constraints.
    Returns a list of validation error messages (empty if valid).
    """
    errors: list[str] = []
    schema = EDGE_SCHEMA.get(EdgeType(rel.type))
    if schema is None:
        errors.append(f"Unknown edge type: {rel.type}")
        return errors

    if rel.source_label and rel.source_label not in schema["source"]:
        errors.append(
            f"{rel.type}: source must be {schema['source']}, got '{rel.source_label}'"
        )
    if rel.target_label and rel.target_label not in schema["target"]:
        errors.append(
            f"{rel.type}: target must be {schema['target']}, got '{rel.target_label}'"
        )

    for req_prop in schema["required"]:
        if req_prop not in rel.properties:
            errors.append(f"{rel.type}: missing required property '{req_prop}'")

    return errors
