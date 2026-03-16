"""
Conflict Primitives — Pydantic v2 models for all 15 DIALECTICA node types.

Implements: Actor, Conflict, Event, Issue, Interest, Norm, Process, Outcome,
Narrative, EmotionalState, TrustState, PowerDynamic, Location, Evidence, Role

All inherit from ConflictNode base with tenant isolation, workspace scoping,
source text tracking, and extraction confidence scoring.

Theoretical basis: TACITUS Core Ontology v2.0 (see ontology.py)
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from ulid import ULID

from dialectica_ontology.enums import (
    ActorType,
    BatnaStrength,
    ConflictDomain,
    ConflictMode,
    ConflictScale,
    ConflictStatus,
    Durability,
    EmotionIntensity,
    Enforceability,
    EvidenceType,
    EventContext,
    EventMode,
    EventType,
    Formality,
    QuadClass,
    FrameType,
    GlaslLevel,
    GlaslStage,
    Incompatibility,
    Intensity,
    InterestType,
    KriesbergPhase,
    LocationType,
    NarrativeType,
    NormType,
    OutcomeType,
    PowerDirection,
    PowerDomain,
    PrimaryEmotion,
    ProcessStage,
    ProcessStatus,
    ProcessType,
    ResolutionApproach,
    RoleType,
    TrustBasis,
    ViolenceType,
)


def _ulid() -> str:
    return str(ULID())


class ConflictNode(BaseModel):
    """Base class for all 15 DIALECTICA node types."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )

    id: str = Field(default_factory=_ulid)
    label: str = ""
    workspace_id: str = ""
    tenant_id: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source_text: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    extraction_method: str | None = None
    embedding: list[float] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("embedding")
    @classmethod
    def validate_embedding_dim(cls, v: list[float] | None) -> list[float] | None:
        if v is not None and len(v) not in (0, 128, 768):
            raise ValueError("embedding must be 128-dim or 768-dim")
        return v


# ─── 1. ACTOR ───────────────────────────────────────────────────────────────

class Actor(ConflictNode):
    """Any entity capable of agency in a conflict.
    Theoretical basis: CAMEO/ACLED actor coding + Fisher/Ury 'negotiator'
    """
    label: str = "Actor"
    name: str
    actor_type: ActorType
    description: str | None = None
    influence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    # Multi-label extra properties (Person)
    role_title: str | None = None
    gender: str | None = None
    age: int | None = None
    # Multi-label extra properties (Organization)
    org_type: str | None = None
    jurisdiction: str | None = None
    size: int | None = None
    sector: str | None = None
    # Multi-label extra properties (State)
    sovereignty: str | None = None
    regime_type: str | None = None
    iso_code: str | None = None
    # Multi-label extra properties (Coalition)
    formation_date: datetime | None = None
    cohesion: float | None = Field(default=None, ge=0.0, le=1.0)
    # Multi-label extra properties (InformalGroup)
    estimated_size: int | None = None
    structure: str | None = None
    # Aliases for matching
    aliases: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)


# ─── 2. CONFLICT ────────────────────────────────────────────────────────────

class Conflict(ConflictNode):
    """A sustained pattern of friction between parties around an incompatibility.
    Theoretical basis: UCDP incompatibility + Galtung ABC + Glasl escalation + Kriesberg lifecycle
    """
    label: str = "Conflict"
    name: str
    scale: ConflictScale
    domain: ConflictDomain
    status: ConflictStatus
    incompatibility: Incompatibility | None = None
    glasl_stage: int | None = Field(default=None, ge=1, le=9)
    glasl_level: GlaslLevel | None = None
    kriesberg_phase: KriesbergPhase | None = None
    violence_type: ViolenceType | None = None
    intensity: Intensity | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    summary: str | None = None

    @model_validator(mode="after")
    def derive_glasl_level(self) -> "Conflict":
        if self.glasl_stage is not None and self.glasl_level is None:
            if self.glasl_stage <= 3:
                self.glasl_level = GlaslLevel.WIN_WIN
            elif self.glasl_stage <= 6:
                self.glasl_level = GlaslLevel.WIN_LOSE
            else:
                self.glasl_level = GlaslLevel.LOSE_LOSE
        return self


# ─── 3. EVENT ───────────────────────────────────────────────────────────────

class Event(ConflictNode):
    """A discrete, time-bounded occurrence that alters a conflict's state.
    Theoretical basis: PLOVER event-mode-context + ACLED event taxonomy
    """
    label: str = "Event"
    event_type: EventType
    mode: EventMode | None = None
    context: EventContext | None = None
    quad_class: QuadClass | None = None
    severity: float = Field(ge=0.0, le=1.0)
    description: str | None = None
    occurred_at: datetime
    source_count: int | None = Field(default=None, ge=0)
    fatalities: int | None = Field(default=None, ge=0)
    location_text: str | None = None


# ─── 4. ISSUE ───────────────────────────────────────────────────────────────

class Issue(ConflictNode):
    """The subject matter or incompatibility at stake.
    Theoretical basis: UCDP incompatibility + Fisher/Ury 'the problem'
    """
    label: str = "Issue"
    name: str
    issue_type: InterestType
    domain_category: str | None = None
    salience: float | None = Field(default=None, ge=0.0, le=1.0)
    divisibility: float | None = Field(default=None, ge=0.0, le=1.0)


# ─── 5. INTEREST ────────────────────────────────────────────────────────────

class Interest(ConflictNode):
    """An underlying need, desire, concern, or fear. The WHY behind a position.
    Theoretical basis: Fisher/Ury 'Getting to Yes' + Rothman identity-based conflict
    """
    label: str = "Interest"
    description: str  # type: ignore[assignment]
    interest_type: InterestType
    priority: int | None = Field(default=None, ge=1, le=5)
    stated: bool | None = None
    stated_position: str | None = None
    satisfaction: float | None = Field(default=None, ge=0.0, le=1.0)
    batna_description: str | None = None
    batna_strength: BatnaStrength | None = None
    reservation_value: float | None = None


# ─── 6. NORM ────────────────────────────────────────────────────────────────

class Norm(ConflictNode):
    """Any rule, standard, or shared expectation governing behavior.
    Theoretical basis: LKIF + CLO + Fisher/Ury 'objective criteria'
    """
    label: str = "Norm"
    name: str
    norm_type: NormType
    jurisdiction: str | None = None
    enforceability: Enforceability | None = None
    text: str | None = None
    effective_from: datetime | None = None
    effective_to: datetime | None = None


# ─── 7. PROCESS ─────────────────────────────────────────────────────────────

class Process(ConflictNode):
    """Any procedure or mechanism for addressing conflict.
    Theoretical basis: Ury/Brett/Goldberg + ADR taxonomy + Glasl intervention mapping
    """
    label: str = "Process"
    process_type: ProcessType
    resolution_approach: ResolutionApproach
    status: ProcessStatus
    formality: Formality | None = None
    binding: bool | None = None
    voluntary: bool | None = None
    current_stage: ProcessStage | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    governing_rules: str | None = None


# ─── 8. OUTCOME ─────────────────────────────────────────────────────────────

class Outcome(ConflictNode):
    """The result of a conflict resolution process or the conflict itself.
    Theoretical basis: Mnookin 'Beyond Winning' (value creation) + ADR outcomes
    """
    label: str = "Outcome"
    outcome_type: OutcomeType
    description: str | None = None  # type: ignore[assignment]
    monetary_value: float | None = None
    satisfaction_a: float | None = Field(default=None, ge=0.0, le=1.0)
    satisfaction_b: float | None = Field(default=None, ge=0.0, le=1.0)
    joint_value: float | None = Field(default=None, ge=0.0, le=1.0)
    durability: Durability | None = None
    compliance_rate: float | None = Field(default=None, ge=0.0, le=1.0)
    decided_at: datetime | None = None
    terms: list[str] = Field(default_factory=list)


# ─── 9. NARRATIVE ───────────────────────────────────────────────────────────

class Narrative(ConflictNode):
    """A dominant story, account, or frame that shapes how a conflict is understood.
    Theoretical basis: Winslade & Monk + Sara Cobb + Dewulf framing + Lakoff
    """
    label: str = "Narrative"
    content: str
    narrative_type: NarrativeType
    perspective: str | None = None
    frame_type: FrameType | None = None
    coherence: float | None = Field(default=None, ge=0.0, le=1.0)
    reach: float | None = Field(default=None, ge=0.0, le=1.0)
    moral_order: str | None = None
    dominant_frame: str | None = None
    counter_frame: str | None = None
    media_prevalence: float | None = Field(default=None, ge=0.0, le=1.0)


# ─── 10. EMOTIONAL STATE ────────────────────────────────────────────────────

class EmotionalState(ConflictNode):
    """An actor's emotional condition at a point in time.
    Theoretical basis: Plutchik wheel + Smith & Ellsworth appraisal theory
    """
    label: str = "EmotionalState"
    primary_emotion: PrimaryEmotion
    intensity: EmotionIntensity
    secondary_emotion: str | None = None
    valence: float | None = Field(default=None, ge=-1.0, le=1.0)
    arousal: float | None = Field(default=None, ge=0.0, le=1.0)
    is_group_emotion: bool | None = None
    trigger_event_id: str | None = None
    observed_at: datetime = Field(default_factory=datetime.utcnow)


# ─── 11. TRUST STATE ────────────────────────────────────────────────────────

class TrustState(ConflictNode):
    """Trust level between two actors. Mayer/Davis/Schoorman integrative model.
    trust = f(ability, benevolence, integrity)
    """
    label: str = "TrustState"
    perceived_ability: float = Field(ge=0.0, le=1.0)
    perceived_benevolence: float = Field(ge=0.0, le=1.0)
    perceived_integrity: float = Field(ge=0.0, le=1.0)
    propensity_to_trust: float | None = Field(default=None, ge=0.0, le=1.0)
    overall_trust: float = Field(ge=0.0, le=1.0)
    trust_basis: TrustBasis | None = None
    assessed_at: datetime = Field(default_factory=datetime.utcnow)


# ─── 12. POWER DYNAMIC ──────────────────────────────────────────────────────

class PowerDynamic(ConflictNode):
    """A measured power relationship between actors.
    Theoretical basis: French & Raven 5 bases of power + Ury/Brett/Goldberg
    """
    label: str = "PowerDynamic"
    power_domain: PowerDomain
    magnitude: float = Field(ge=0.0, le=1.0)
    direction: PowerDirection
    legitimacy: float | None = Field(default=None, ge=0.0, le=1.0)
    exercised: bool | None = None
    reversible: bool | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None


# ─── 13. LOCATION ───────────────────────────────────────────────────────────

class Location(ConflictNode):
    """Geographic entity. Hierarchically structured via WITHIN edges.
    Theoretical basis: ACLED/UCDP spatial coding
    """
    label: str = "Location"
    name: str
    location_type: LocationType
    latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    longitude: float | None = Field(default=None, ge=-180.0, le=180.0)
    country_code: str | None = None
    admin_level: int | None = None

    @field_validator("country_code")
    @classmethod
    def validate_country_code(cls, v: str | None) -> str | None:
        if v is not None and len(v) != 3:
            raise ValueError("country_code must be ISO 3166-1 alpha-3 (3 chars)")
        return v


# ─── 14. EVIDENCE ───────────────────────────────────────────────────────────

class Evidence(ConflictNode):
    """Supporting material for claims, events, or assertions.
    Theoretical basis: Legal evidence law + ACLED source methodology
    """
    label: str = "Evidence"
    evidence_type: EvidenceType
    description: str  # type: ignore[assignment]
    source_name: str | None = None
    reliability: float | None = Field(default=None, ge=0.0, le=1.0)
    url: str | None = None
    collected_at: datetime | None = None


# ─── 15. ROLE ───────────────────────────────────────────────────────────────

class Role(ConflictNode):
    """A contextual role played by an actor in a specific conflict or event.
    Theoretical basis: SEM (Simple Event Model) role reification
    """
    label: str = "Role"
    role_type: RoleType
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    actor_id: str | None = None
    context_id: str | None = None


# ─── Registry ───────────────────────────────────────────────────────────────

NODE_TYPES: dict[str, type[ConflictNode]] = {
    "Actor": Actor,
    "Conflict": Conflict,
    "Event": Event,
    "Issue": Issue,
    "Interest": Interest,
    "Norm": Norm,
    "Process": Process,
    "Outcome": Outcome,
    "Narrative": Narrative,
    "EmotionalState": EmotionalState,
    "TrustState": TrustState,
    "PowerDynamic": PowerDynamic,
    "Location": Location,
    "Evidence": Evidence,
    "Role": Role,
}
