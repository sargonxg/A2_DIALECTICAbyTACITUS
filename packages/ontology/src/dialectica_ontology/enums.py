"""
Conflict Enumerations — StrEnum classes for all 25+ DIALECTICA controlled vocabularies.

Every enum value is drawn directly from ontology.py ENUMS{} dict.
Source attributions are preserved as class-level docstrings.
"""

from __future__ import annotations

from enum import StrEnum


# ─── Actor ──────────────────────────────────────────────────────────────────

class ActorType(StrEnum):
    """Source: CAMEO/ACLED synthesis"""
    PERSON = "person"
    ORGANIZATION = "organization"
    STATE = "state"
    COALITION = "coalition"
    INFORMAL_GROUP = "informal_group"


# ─── Conflict ───────────────────────────────────────────────────────────────

class ConflictScale(StrEnum):
    """Source: Lederach nested paradigm.
    micro=interpersonal, meso=organizational/community, macro=national/international, meta=civilizational
    """
    MICRO = "micro"
    MESO = "meso"
    MACRO = "macro"
    META = "meta"


class ConflictDomain(StrEnum):
    """Source: TACITUS synthesis"""
    INTERPERSONAL = "interpersonal"
    WORKPLACE = "workplace"
    COMMERCIAL = "commercial"
    LEGAL = "legal"
    POLITICAL = "political"
    ARMED = "armed"


class ConflictStatus(StrEnum):
    """Source: Kriesberg + Lederach"""
    LATENT = "latent"
    ACTIVE = "active"
    DORMANT = "dormant"
    RESOLVED = "resolved"
    TRANSFORMED = "transformed"


class KriesbergPhase(StrEnum):
    """Source: Kriesberg: Constructive Conflicts"""
    LATENT = "latent"
    EMERGING = "emerging"
    ESCALATING = "escalating"
    STALEMATE = "stalemate"
    DE_ESCALATING = "de_escalating"
    TERMINATING = "terminating"
    POST_CONFLICT = "post_conflict"


class GlaslStage(StrEnum):
    """Source: Glasl: Confronting Conflict.
    9-stage escalation model with three levels (win-win, win-lose, lose-lose).
    """
    HARDENING = "hardening"
    DEBATE_AND_POLEMICS = "debate_and_polemics"
    ACTIONS_NOT_WORDS = "actions_not_words"
    IMAGES_AND_COALITIONS = "images_and_coalitions"
    LOSS_OF_FACE = "loss_of_face"
    STRATEGIES_OF_THREATS = "strategies_of_threats"
    LIMITED_DESTRUCTIVE_BLOWS = "limited_destructive_blows"
    FRAGMENTATION = "fragmentation"
    TOGETHER_INTO_THE_ABYSS = "together_into_the_abyss"

    @property
    def stage_number(self) -> int:
        return list(GlaslStage).index(self) + 1

    @property
    def level(self) -> str:
        n = self.stage_number
        if n <= 3:
            return "win_win"
        elif n <= 6:
            return "win_lose"
        else:
            return "lose_lose"

    @property
    def intervention_type(self) -> str:
        _map = {
            1: "moderation",
            2: "moderation",
            3: "facilitation",
            4: "process_consultation",
            5: "mediation",
            6: "mediation",
            7: "arbitration",
            8: "power_intervention",
            9: "power_intervention",
        }
        return _map[self.stage_number]


class GlaslLevel(StrEnum):
    """Source: Glasl (derived from stage 1-3, 4-6, 7-9)"""
    WIN_WIN = "win_win"
    WIN_LOSE = "win_lose"
    LOSE_LOSE = "lose_lose"


class Incompatibility(StrEnum):
    """Source: UCDP + Galtung extended"""
    GOVERNMENT = "government"
    TERRITORY = "territory"
    RESOURCE = "resource"
    RIGHTS = "rights"
    RELATIONSHIP = "relationship"
    IDENTITY = "identity"


class ViolenceType(StrEnum):
    """Source: Galtung violence triangle"""
    DIRECT = "direct"
    STRUCTURAL = "structural"
    CULTURAL = "cultural"
    NONE = "none"


class Intensity(StrEnum):
    """Source: Synthesis (maps to UCDP minor/war thresholds)"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    EXTREME = "extreme"


# ─── Event ──────────────────────────────────────────────────────────────────

class EventType(StrEnum):
    """Source: PLOVER 16-type ontology.
    Domain add-ons map specific events to these universal types.
    """
    # Cooperative spectrum
    AGREE = "agree"
    CONSULT = "consult"
    SUPPORT = "support"
    COOPERATE = "cooperate"
    AID = "aid"
    YIELD = "yield"
    # Neutral
    INVESTIGATE = "investigate"
    # Conflict spectrum
    DEMAND = "demand"
    DISAPPROVE = "disapprove"
    REJECT = "reject"
    THREATEN = "threaten"
    PROTEST = "protest"
    EXHIBIT_FORCE_POSTURE = "exhibit_force_posture"
    REDUCE_RELATIONS = "reduce_relations"
    COERCE = "coerce"
    ASSAULT = "assault"


class EventMode(StrEnum):
    """Source: PLOVER mode concept (extended for non-geopolitical domains)"""
    VERBAL = "verbal"
    WRITTEN = "written"
    DIPLOMATIC = "diplomatic"
    LEGAL = "legal"
    ECONOMIC = "economic"
    CYBER = "cyber"
    CONVENTIONAL_MILITARY = "conventional_military"
    UNCONVENTIONAL = "unconventional"
    ADMINISTRATIVE = "administrative"
    PROCEDURAL = "procedural"
    SYMBOLIC = "symbolic"


class EventContext(StrEnum):
    """Source: PLOVER context concept (extended)"""
    POLITICAL = "political"
    TERRITORIAL = "territorial"
    ECONOMIC = "economic"
    ETHNIC = "ethnic"
    RELIGIOUS = "religious"
    ENVIRONMENTAL = "environmental"
    LABOR = "labor"
    CONTRACTUAL = "contractual"
    REGULATORY = "regulatory"
    INTERPERSONAL = "interpersonal"
    ORGANIZATIONAL = "organizational"
    TECHNOLOGICAL = "technological"


class QuadClass(StrEnum):
    """Source: CAMEO/PLOVER QuadClass"""
    VERBAL_COOPERATION = "verbal_cooperation"
    MATERIAL_COOPERATION = "material_cooperation"
    VERBAL_CONFLICT = "verbal_conflict"
    MATERIAL_CONFLICT = "material_conflict"


# ─── Interest ───────────────────────────────────────────────────────────────

class InterestType(StrEnum):
    """Source: Fisher/Ury + Rothman identity-based conflict"""
    SUBSTANTIVE = "substantive"
    PROCEDURAL = "procedural"
    PSYCHOLOGICAL = "psychological"
    IDENTITY = "identity"


# ─── Norm ───────────────────────────────────────────────────────────────────

class NormType(StrEnum):
    """Source: LKIF + CLO synthesis"""
    STATUTE = "statute"
    REGULATION = "regulation"
    TREATY = "treaty"
    CONTRACT = "contract"
    POLICY = "policy"
    SOCIAL_NORM = "social_norm"
    CUSTOMARY_LAW = "customary_law"
    PRECEDENT = "precedent"
    PROFESSIONAL_STANDARD = "professional_standard"


class Enforceability(StrEnum):
    """Source: CLO (Core Legal Ontology)"""
    BINDING = "binding"
    ADVISORY = "advisory"
    ASPIRATIONAL = "aspirational"


# ─── Process ────────────────────────────────────────────────────────────────

class ProcessType(StrEnum):
    """Source: ADR taxonomy synthesis"""
    NEGOTIATION = "negotiation"
    MEDIATION_FACILITATIVE = "mediation_facilitative"
    MEDIATION_EVALUATIVE = "mediation_evaluative"
    MEDIATION_TRANSFORMATIVE = "mediation_transformative"
    MEDIATION_NARRATIVE = "mediation_narrative"
    ARBITRATION = "arbitration"
    ADJUDICATION = "adjudication"
    INVESTIGATION = "investigation"
    GRIEVANCE_PROCEDURE = "grievance_procedure"
    OMBUDS = "ombuds"
    CONCILIATION = "conciliation"
    EARLY_NEUTRAL_EVALUATION = "early_neutral_evaluation"
    ONLINE_DISPUTE_RESOLUTION = "online_dispute_resolution"


class ResolutionApproach(StrEnum):
    """Source: Ury/Brett/Goldberg: Getting Disputes Resolved.
    THE meta-framework: conflicts most efficiently resolved at interest level;
    rights/power escalate cost.
    """
    INTEREST_BASED = "interest_based"
    RIGHTS_BASED = "rights_based"
    POWER_BASED = "power_based"


class ProcessStatus(StrEnum):
    """Source: ADR lifecycle synthesis"""
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    APPEALED = "appealed"


# ─── Outcome ────────────────────────────────────────────────────────────────

class OutcomeType(StrEnum):
    """Source: Multi-domain synthesis"""
    AGREEMENT = "agreement"
    SETTLEMENT = "settlement"
    AWARD = "award"
    JUDGMENT = "judgment"
    CONSENT_ORDER = "consent_order"
    WITHDRAWAL = "withdrawal"
    NO_RESOLUTION = "no_resolution"
    CEASEFIRE = "ceasefire"
    PEACE_AGREEMENT = "peace_agreement"
    TRANSFORMATION = "transformation"
    ACQUIESCENCE = "acquiescence"


class Durability(StrEnum):
    """Source: Peace research (positive vs negative peace)"""
    TEMPORARY = "temporary"
    DURABLE = "durable"
    PERMANENT = "permanent"


# ─── Emotion ────────────────────────────────────────────────────────────────

class PrimaryEmotion(StrEnum):
    """Source: Plutchik wheel of emotions.
    8 primary emotions with dyads (combinations) and opposites.
    """
    JOY = "joy"
    TRUST = "trust"
    FEAR = "fear"
    SURPRISE = "surprise"
    SADNESS = "sadness"
    DISGUST = "disgust"
    ANGER = "anger"
    ANTICIPATION = "anticipation"

    @property
    def opposite(self) -> PrimaryEmotion:
        _opposites = {
            "joy": "sadness",
            "sadness": "joy",
            "trust": "disgust",
            "disgust": "trust",
            "fear": "anger",
            "anger": "fear",
            "surprise": "anticipation",
            "anticipation": "surprise",
        }
        return PrimaryEmotion(_opposites[self.value])

    @classmethod
    def dyads(cls) -> dict[str, tuple[PrimaryEmotion, PrimaryEmotion]]:
        return {
            "optimism": (cls.ANTICIPATION, cls.JOY),
            "love": (cls.JOY, cls.TRUST),
            "submission": (cls.TRUST, cls.FEAR),
            "awe": (cls.FEAR, cls.SURPRISE),
            "disapproval": (cls.SURPRISE, cls.SADNESS),
            "remorse": (cls.SADNESS, cls.DISGUST),
            "contempt": (cls.DISGUST, cls.ANGER),
            "aggressiveness": (cls.ANGER, cls.ANTICIPATION),
        }


class EmotionIntensity(StrEnum):
    """Source: Plutchik (e.g., annoyance -> anger -> rage)"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ─── Narrative ──────────────────────────────────────────────────────────────

class NarrativeType(StrEnum):
    """Source: Winslade & Monk: Narrative Mediation"""
    DOMINANT = "dominant"
    ALTERNATIVE = "alternative"
    COUNTER = "counter"
    SUBJUGATED = "subjugated"


# ─── ConflictMode ───────────────────────────────────────────────────────────

class ConflictMode(StrEnum):
    """Source: Thomas-Kilmann Conflict Mode Instrument.
    Dual-concern model mapping assertiveness x cooperativeness.
    """
    COMPETING = "competing"
    COLLABORATING = "collaborating"
    COMPROMISING = "compromising"
    AVOIDING = "avoiding"
    ACCOMMODATING = "accommodating"

    @property
    def assertiveness(self) -> str:
        _map = {
            "competing": "high",
            "collaborating": "high",
            "compromising": "medium",
            "avoiding": "low",
            "accommodating": "low",
        }
        return _map[self.value]

    @property
    def cooperativeness(self) -> str:
        _map = {
            "competing": "low",
            "collaborating": "high",
            "compromising": "medium",
            "avoiding": "low",
            "accommodating": "high",
        }
        return _map[self.value]


# ─── Power ──────────────────────────────────────────────────────────────────

class PowerDomain(StrEnum):
    """Source: French & Raven + Ury/Brett/Goldberg"""
    COERCIVE = "coercive"
    ECONOMIC = "economic"
    POLITICAL = "political"
    INFORMATIONAL = "informational"
    POSITIONAL = "positional"
    REFERENT = "referent"
    LEGITIMATE = "legitimate"
    EXPERT = "expert"


# ─── Role ───────────────────────────────────────────────────────────────────

class RoleType(StrEnum):
    """Source: Multi-domain synthesis"""
    CLAIMANT = "claimant"
    RESPONDENT = "respondent"
    MEDIATOR = "mediator"
    ARBITRATOR = "arbitrator"
    JUDGE = "judge"
    WITNESS = "witness"
    ADVOCATE = "advocate"
    AGGRESSOR = "aggressor"
    TARGET = "target"
    BYSTANDER = "bystander"
    FACILITATOR = "facilitator"
    PERPETRATOR = "perpetrator"
    VICTIM = "victim"
    ALLY = "ally"
    NEUTRAL = "neutral"
    GUARANTOR = "guarantor"
    SPOILER = "spoiler"
    PEACEMAKER = "peacemaker"


# ─── Additional inline enums used in node/edge properties ───────────────────

class BatnaStrength(StrEnum):
    """BATNA quality assessment for Interest node."""
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


class Formality(StrEnum):
    """Process formality level."""
    INFORMAL = "informal"
    SEMI_FORMAL = "semi_formal"
    FORMAL = "formal"


class ProcessStage(StrEnum):
    """Process lifecycle stage."""
    INTAKE = "intake"
    DIALOGUE = "dialogue"
    EVALUATION = "evaluation"
    RESOLUTION = "resolution"
    IMPLEMENTATION = "implementation"


class FrameType(StrEnum):
    """Dewulf frame classification for Narrative node."""
    IDENTITY = "identity"
    CHARACTERIZATION = "characterization"
    POWER = "power"
    RISK = "risk"
    LOSS_GAIN = "loss_gain"
    MORAL = "moral"


class TrustBasis(StrEnum):
    """Lewicki & Bunker trust development stage."""
    CALCULUS = "calculus"
    KNOWLEDGE = "knowledge"
    IDENTIFICATION = "identification"


class PowerDirection(StrEnum):
    """Direction of power asymmetry."""
    A_OVER_B = "a_over_b"
    B_OVER_A = "b_over_a"
    SYMMETRIC = "symmetric"


class LocationType(StrEnum):
    """Geographic hierarchy level."""
    POINT = "point"
    BUILDING = "building"
    CITY = "city"
    DISTRICT = "district"
    REGION = "region"
    COUNTRY = "country"
    GLOBAL = "global"


class EvidenceType(StrEnum):
    """Evidence classification."""
    DOCUMENT = "document"
    TESTIMONY = "testimony"
    EXPERT_OPINION = "expert_opinion"
    DIGITAL_RECORD = "digital_record"
    PHYSICAL = "physical"
    STATISTICAL = "statistical"


class Side(StrEnum):
    """UCDP convention for conflict sides."""
    SIDE_A = "side_a"
    SIDE_B = "side_b"
    THIRD_PARTY = "third_party"
    OBSERVER = "observer"


class CausalMechanism(StrEnum):
    """Causal mechanism for CAUSED edge."""
    ESCALATION = "escalation"
    RETALIATION = "retaliation"
    CONTAGION = "contagion"
    SPILLOVER = "spillover"
    PROVOCATION = "provocation"
    PRECEDENT = "precedent"


class AllianceFormality(StrEnum):
    """Alliance formality for ALLIED_WITH edge."""
    FORMAL = "formal"
    TACIT = "tacit"
