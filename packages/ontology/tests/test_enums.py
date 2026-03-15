"""Tests for dialectica_ontology.enums — All 25+ StrEnum classes."""

from dialectica_ontology.enums import (
    ActorType,
    AllianceFormality,
    BatnaStrength,
    CausalMechanism,
    ConflictDomain,
    ConflictMode,
    ConflictScale,
    ConflictStatus,
    Durability,
    EmotionIntensity,
    Enforceability,
    EventContext,
    EventMode,
    EventType,
    EvidenceType,
    Formality,
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
    QuadClass,
    ResolutionApproach,
    RoleType,
    Side,
    TrustBasis,
    ViolenceType,
)


# ─── Value counts match ontology.py ─────────────────────────────────────────

def test_actor_type_values():
    assert len(ActorType) == 5
    assert ActorType.PERSON == "person"
    assert ActorType.STATE == "state"


def test_conflict_scale_values():
    assert len(ConflictScale) == 4
    assert ConflictScale.MICRO == "micro"
    assert ConflictScale.META == "meta"


def test_conflict_domain_values():
    assert len(ConflictDomain) == 6
    assert "armed" in [d.value for d in ConflictDomain]


def test_conflict_status_values():
    assert len(ConflictStatus) == 5


def test_kriesberg_phase_values():
    assert len(KriesbergPhase) == 7
    assert KriesbergPhase.LATENT == "latent"
    assert KriesbergPhase.POST_CONFLICT == "post_conflict"


def test_glasl_stage_values():
    assert len(GlaslStage) == 9
    assert GlaslStage.HARDENING == "hardening"
    assert GlaslStage.TOGETHER_INTO_THE_ABYSS == "together_into_the_abyss"


def test_glasl_stage_numbers():
    assert GlaslStage.HARDENING.stage_number == 1
    assert GlaslStage.TOGETHER_INTO_THE_ABYSS.stage_number == 9


def test_glasl_stage_levels():
    assert GlaslStage.HARDENING.level == "win_win"
    assert GlaslStage.DEBATE_AND_POLEMICS.level == "win_win"
    assert GlaslStage.ACTIONS_NOT_WORDS.level == "win_win"
    assert GlaslStage.IMAGES_AND_COALITIONS.level == "win_lose"
    assert GlaslStage.LOSS_OF_FACE.level == "win_lose"
    assert GlaslStage.STRATEGIES_OF_THREATS.level == "win_lose"
    assert GlaslStage.LIMITED_DESTRUCTIVE_BLOWS.level == "lose_lose"
    assert GlaslStage.FRAGMENTATION.level == "lose_lose"
    assert GlaslStage.TOGETHER_INTO_THE_ABYSS.level == "lose_lose"


def test_glasl_stage_interventions():
    assert GlaslStage.HARDENING.intervention_type == "moderation"
    assert GlaslStage.ACTIONS_NOT_WORDS.intervention_type == "facilitation"
    assert GlaslStage.IMAGES_AND_COALITIONS.intervention_type == "process_consultation"
    assert GlaslStage.LOSS_OF_FACE.intervention_type == "mediation"
    assert GlaslStage.LIMITED_DESTRUCTIVE_BLOWS.intervention_type == "arbitration"
    assert GlaslStage.FRAGMENTATION.intervention_type == "power_intervention"


def test_glasl_level_values():
    assert len(GlaslLevel) == 3


def test_incompatibility_values():
    assert len(Incompatibility) == 6
    vals = {i.value for i in Incompatibility}
    assert vals == {"government", "territory", "resource", "rights", "relationship", "identity"}


def test_violence_type_values():
    assert len(ViolenceType) == 4


def test_intensity_values():
    assert len(Intensity) == 5


def test_event_type_values():
    assert len(EventType) == 16
    # Check cooperative + neutral + conflict = 6 + 1 + 9 = 16
    assert EventType.AGREE == "agree"
    assert EventType.ASSAULT == "assault"
    assert EventType.INVESTIGATE == "investigate"


def test_event_mode_values():
    assert len(EventMode) == 11


def test_event_context_values():
    assert len(EventContext) == 12


def test_quad_class_values():
    assert len(QuadClass) == 4


def test_interest_type_values():
    assert len(InterestType) == 4


def test_norm_type_values():
    assert len(NormType) == 9


def test_enforceability_values():
    assert len(Enforceability) == 3


def test_process_type_values():
    assert len(ProcessType) == 13


def test_resolution_approach_values():
    assert len(ResolutionApproach) == 3


def test_process_status_values():
    assert len(ProcessStatus) == 6


def test_outcome_type_values():
    assert len(OutcomeType) == 11


def test_durability_values():
    assert len(Durability) == 3


def test_primary_emotion_values():
    assert len(PrimaryEmotion) == 8
    vals = {e.value for e in PrimaryEmotion}
    assert vals == {"joy", "trust", "fear", "surprise", "sadness", "disgust", "anger", "anticipation"}


def test_primary_emotion_opposites():
    assert PrimaryEmotion.JOY.opposite == PrimaryEmotion.SADNESS
    assert PrimaryEmotion.FEAR.opposite == PrimaryEmotion.ANGER
    assert PrimaryEmotion.TRUST.opposite == PrimaryEmotion.DISGUST
    assert PrimaryEmotion.SURPRISE.opposite == PrimaryEmotion.ANTICIPATION


def test_primary_emotion_dyads():
    dyads = PrimaryEmotion.dyads()
    assert len(dyads) == 8
    assert dyads["optimism"] == (PrimaryEmotion.ANTICIPATION, PrimaryEmotion.JOY)
    assert dyads["contempt"] == (PrimaryEmotion.DISGUST, PrimaryEmotion.ANGER)
    assert dyads["love"] == (PrimaryEmotion.JOY, PrimaryEmotion.TRUST)


def test_emotion_intensity_values():
    assert len(EmotionIntensity) == 3


def test_narrative_type_values():
    assert len(NarrativeType) == 4


def test_conflict_mode_values():
    assert len(ConflictMode) == 5


def test_conflict_mode_dual_concern():
    assert ConflictMode.COMPETING.assertiveness == "high"
    assert ConflictMode.COMPETING.cooperativeness == "low"
    assert ConflictMode.COLLABORATING.assertiveness == "high"
    assert ConflictMode.COLLABORATING.cooperativeness == "high"
    assert ConflictMode.COMPROMISING.assertiveness == "medium"
    assert ConflictMode.COMPROMISING.cooperativeness == "medium"
    assert ConflictMode.AVOIDING.assertiveness == "low"
    assert ConflictMode.AVOIDING.cooperativeness == "low"
    assert ConflictMode.ACCOMMODATING.assertiveness == "low"
    assert ConflictMode.ACCOMMODATING.cooperativeness == "high"


def test_power_domain_values():
    assert len(PowerDomain) == 8


def test_role_type_values():
    assert len(RoleType) == 18


def test_batna_strength():
    assert len(BatnaStrength) == 3


def test_formality():
    assert len(Formality) == 3


def test_process_stage():
    assert len(ProcessStage) == 5


def test_frame_type():
    assert len(FrameType) == 6


def test_trust_basis():
    assert len(TrustBasis) == 3


def test_power_direction():
    assert len(PowerDirection) == 3


def test_location_type():
    assert len(LocationType) == 7


def test_evidence_type():
    assert len(EvidenceType) == 6


def test_side():
    assert len(Side) == 4


def test_causal_mechanism():
    assert len(CausalMechanism) == 6


def test_alliance_formality():
    assert len(AllianceFormality) == 2


def test_str_enum_serialization():
    """All enums should serialize to strings."""
    assert ActorType.PERSON.value == "person"
    # StrEnum's str() returns the value directly
    assert str(ActorType.PERSON) == "person"
