"""Pydantic models for TACITUS core v1.

These models are intentionally narrower than the existing ACO v2 package. They
enforce the separation, temporality, and provenance fields required for the
first graph-pipeline vertical slice.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ONTOLOGY_VERSION = "tacitus_core_v1"


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


class ScopedModel(BaseModel):
    """Base object requiring workspace and case separation."""

    model_config = ConfigDict(extra="forbid")

    id: str
    workspace_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    ontology_version: str = ONTOLOGY_VERSION


class ExtractionRun(ScopedModel):
    id: str = Field(default_factory=lambda: new_id("run"))
    primitive_type: Literal["ExtractionRun"] = "ExtractionRun"
    extraction_run_id: str = ""
    model_name: str = Field(min_length=1)
    extraction_method: str = Field(min_length=1)
    prompt_version: str = "local_rule_v1"
    schema_version: str = ONTOLOGY_VERSION
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def default_run_id(self) -> ExtractionRun:
        if not self.extraction_run_id:
            self.extraction_run_id = self.id
        return self


class SourceDocument(ScopedModel):
    id: str = Field(default_factory=lambda: new_id("doc"))
    primitive_type: Literal["SourceDocument"] = "SourceDocument"
    source_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    path: str | None = None
    text_sha256: str = Field(min_length=1)
    source_type: str = "text"
    trust_level: str = "user_direct"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SourceChunk(ScopedModel):
    id: str = Field(default_factory=lambda: new_id("chunk"))
    primitive_type: Literal["SourceChunk"] = "SourceChunk"
    source_id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    chunk_index: int = Field(ge=0)
    text: str = Field(min_length=1)
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=0)
    extraction_run_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_offsets(self) -> SourceChunk:
        if self.end_char <= self.start_char:
            raise ValueError("end_char must be greater than start_char")
        return self


class EvidenceSpan(ScopedModel):
    id: str = Field(default_factory=lambda: new_id("span"))
    primitive_type: Literal["EvidenceSpan"] = "EvidenceSpan"
    source_id: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)
    extraction_run_id: str = Field(min_length=1)
    provenance_span: str = Field(min_length=1)
    start_char: int = Field(ge=0)
    end_char: int = Field(ge=0)
    confidence: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_offsets(self) -> EvidenceSpan:
        if self.end_char <= self.start_char:
            raise ValueError("end_char must be greater than start_char")
        return self


class ProvenancedPrimitive(ScopedModel):
    """Base for extracted graph primitives with required provenance."""

    source_id: str = Field(min_length=1)
    extraction_run_id: str = Field(min_length=1)
    evidence_span_id: str = Field(min_length=1)
    provenance_span: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_temporal_window(self) -> ProvenancedPrimitive:
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValueError("valid_to cannot be earlier than valid_from")
        return self


class Episode(ScopedModel):
    id: str = Field(default_factory=lambda: new_id("episode"))
    primitive_type: Literal["Episode"] = "Episode"
    name: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_id: str = ""
    extraction_run_id: str = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class EpisodePrimitive(ProvenancedPrimitive):
    episode_id: str = Field(min_length=1)


class Actor(ProvenancedPrimitive):
    id: str = Field(default_factory=lambda: new_id("actor"))
    primitive_type: Literal["Actor"] = "Actor"
    name: str = Field(min_length=1)
    actor_type: str = "unknown"
    aliases: list[str] = Field(default_factory=list)


class Claim(EpisodePrimitive):
    id: str = Field(default_factory=lambda: new_id("claim"))
    primitive_type: Literal["Claim"] = "Claim"
    text: str = Field(min_length=1)
    claim_status: str = "extracted"
    assertion_type: str = "explicit"
    subject_actor_id: str | None = None


class Interest(EpisodePrimitive):
    id: str = Field(default_factory=lambda: new_id("interest"))
    primitive_type: Literal["Interest"] = "Interest"
    actor_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    interest_type: str = "unknown"


class Constraint(EpisodePrimitive):
    id: str = Field(default_factory=lambda: new_id("constraint"))
    primitive_type: Literal["Constraint"] = "Constraint"
    actor_id: str | None = None
    description: str = Field(min_length=1)
    constraint_type: str = "unknown"


class Leverage(EpisodePrimitive):
    id: str = Field(default_factory=lambda: new_id("leverage"))
    primitive_type: Literal["Leverage"] = "Leverage"
    actor_id: str = Field(min_length=1)
    target_actor_id: str | None = None
    leverage_type: str = "unknown"
    level: str = "unknown"


class Commitment(EpisodePrimitive):
    id: str = Field(default_factory=lambda: new_id("commitment"))
    primitive_type: Literal["Commitment"] = "Commitment"
    actor_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    commitment_status: str = "proposed"
    constrains_actor_id: str | None = None


class Event(EpisodePrimitive):
    id: str = Field(default_factory=lambda: new_id("event"))
    primitive_type: Literal["Event"] = "Event"
    description: str = Field(min_length=1)
    occurred_at: datetime | None = None
    event_type: str = "unknown"


class Narrative(EpisodePrimitive):
    id: str = Field(default_factory=lambda: new_id("narrative"))
    primitive_type: Literal["Narrative"] = "Narrative"
    actor_id: str | None = None
    content: str = Field(min_length=1)
    narrative_type: str = "unknown"


class ActorState(EpisodePrimitive):
    id: str = Field(default_factory=lambda: new_id("actor_state"))
    primitive_type: Literal["ActorState"] = "ActorState"
    actor_id: str = Field(min_length=1)
    leverage_level: str | None = None
    trust_level: str | None = None
    emotional_state: str | None = None
    source_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_state_value(self) -> ActorState:
        if not any([self.leverage_level, self.trust_level, self.emotional_state]):
            raise ValueError("ActorState requires leverage_level, trust_level, or emotional_state")
        return self


GraphPrimitive = (
    Actor
    | Claim
    | Interest
    | Constraint
    | Leverage
    | Commitment
    | Event
    | Narrative
    | Episode
    | ActorState
    | SourceDocument
    | SourceChunk
    | EvidenceSpan
    | ExtractionRun
)

PRIMITIVE_MODELS: dict[str, type[BaseModel]] = {
    "Actor": Actor,
    "Claim": Claim,
    "Interest": Interest,
    "Constraint": Constraint,
    "Leverage": Leverage,
    "Commitment": Commitment,
    "Event": Event,
    "Narrative": Narrative,
    "Episode": Episode,
    "ActorState": ActorState,
    "SourceDocument": SourceDocument,
    "SourceChunk": SourceChunk,
    "EvidenceSpan": EvidenceSpan,
    "ExtractionRun": ExtractionRun,
}
