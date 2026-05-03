"""Schema for the optional graph reasoning subsystem."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ObjectKind(StrEnum):
    ACTOR = "Actor"
    CLAIM = "Claim"
    INTEREST = "Interest"
    CONSTRAINT = "Constraint"
    LEVERAGE = "Leverage"
    COMMITMENT = "Commitment"
    EVENT = "Event"
    NARRATIVE = "Narrative"
    SOURCE = "Source"
    EVIDENCE = "Evidence"


class EdgeKind(StrEnum):
    MENTIONS = "MENTIONS"
    EVIDENCES = "EVIDENCES"
    MAKES_CLAIM = "MAKES_CLAIM"
    HAS_INTEREST = "HAS_INTEREST"
    HAS_CONSTRAINT = "HAS_CONSTRAINT"
    HAS_LEVERAGE = "HAS_LEVERAGE"
    COMMITS_TO = "COMMITS_TO"
    PARTICIPATES_IN = "PARTICIPATES_IN"
    PROMOTES = "PROMOTES"
    RELATED_TO = "RELATED_TO"
    CONSTRAINS = "CONSTRAINS"
    TARGETS = "TARGETS"
    SOURCED_FROM = "SOURCED_FROM"


def utc_now() -> datetime:
    return datetime.now(UTC)


def stable_hash(*parts: Any, length: int = 24) -> str:
    encoded = json.dumps(parts, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:length]


def stable_object_id(
    kind: ObjectKind | str, workspace_id: str, content: str, source_ids: list[str]
) -> str:
    prefix = str(kind).lower()
    return (
        f"{prefix}_{stable_hash(workspace_id, kind, content.strip().lower(), sorted(source_ids))}"
    )


def stable_edge_id(
    source_id: str,
    target_id: str,
    kind: EdgeKind | str,
    source_ids: list[str],
    valid_from: datetime | None = None,
) -> str:
    return f"edge_{stable_hash(source_id, target_id, kind, sorted(source_ids), valid_from)}"


class GraphReasoningObject(BaseModel):
    """A provenance-carrying reasoning object mirrored across graph layers."""

    model_config = ConfigDict(use_enum_values=True)

    id: str
    kind: ObjectKind
    workspace_id: str = Field(min_length=1)
    tenant_id: str = Field(default="default", min_length=1)
    name: str | None = None
    text: str | None = None
    description: str | None = None
    source_ids: list[str] = Field(min_length=1)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    properties: dict[str, Any] = Field(default_factory=dict)

    @field_validator("source_ids")
    @classmethod
    def source_ids_must_be_nonempty(cls, value: list[str]) -> list[str]:
        cleaned = [item for item in value if item]
        if not cleaned:
            raise ValueError("source_ids must include at least one source identifier")
        return sorted(set(cleaned))

    @model_validator(mode="after")
    def valid_window_is_ordered(self) -> GraphReasoningObject:
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to cannot be earlier than valid_from")
        return self

    def to_neo4j_props(self) -> dict[str, Any]:
        data = self.model_dump(mode="python")
        data["kind"] = str(self.kind)
        data["properties_json"] = json.dumps(data.pop("properties"), sort_keys=True, default=str)
        for key, value in list(data.items()):
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif value is None:
                data.pop(key)
        return data


class GraphReasoningEdge(BaseModel):
    """A typed edge that never exists without provenance."""

    model_config = ConfigDict(use_enum_values=True)

    id: str
    kind: EdgeKind
    source_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    workspace_id: str = Field(min_length=1)
    tenant_id: str = Field(default="default", min_length=1)
    source_ids: list[str] = Field(min_length=1)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    properties: dict[str, Any] = Field(default_factory=dict)

    @field_validator("source_ids")
    @classmethod
    def edge_source_ids_must_be_nonempty(cls, value: list[str]) -> list[str]:
        cleaned = [item for item in value if item]
        if not cleaned:
            raise ValueError("source_ids must include at least one source identifier")
        return sorted(set(cleaned))

    @model_validator(mode="after")
    def edge_valid_window_is_ordered(self) -> GraphReasoningEdge:
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to cannot be earlier than valid_from")
        return self

    def to_neo4j_props(self) -> dict[str, Any]:
        data = self.model_dump(mode="python")
        data["kind"] = str(self.kind)
        data["properties_json"] = json.dumps(data.pop("properties"), sort_keys=True, default=str)
        for key, value in list(data.items()):
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif value is None:
                data.pop(key)
        return data


class IngestTextRequest(BaseModel):
    text: str = Field(min_length=1)
    workspace_id: str = "default"
    source_title: str = "inline text"
    source_uri: str | None = None
    source_type: str = "text"
    objective: str = "Understand the conflict"
    ontology_profile: str = "human-friction"
    occurred_at: datetime | None = None
    force: bool = False


class IngestResult(BaseModel):
    status: str
    duplicate: bool = False
    source_id: str
    episode_id: str | None = None
    object_count: int = 0
    edge_count: int = 0
    object_ids: list[str] = Field(default_factory=list)
    edge_ids: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    pipeline: dict[str, Any] = Field(default_factory=dict)


class HealthCheck(BaseModel):
    service: str
    status: str
    mode: str = ""
    details: str = ""


class GraphReasoningHealth(BaseModel):
    status: str
    checks: dict[str, HealthCheck]
