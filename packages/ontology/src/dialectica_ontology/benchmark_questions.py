"""
Benchmark Question Library — Universal questions for evaluating ConflictCorpus analysis.

A structured library of diagnostic questions applicable to ANY ConflictCorpus,
organized by domain, theory, analysis mode, and difficulty level.

These questions serve as:
1. Benchmark evaluation criteria (does the system answer correctly?)
2. Guided analysis prompts (help analysts explore a corpus systematically)
3. Agent self-evaluation (does the agent cover all analytical dimensions?)
4. Quality gates (minimum questions that must be answerable for a corpus to be "complete")

Two domain sections: Human Friction and Conflict/Warfare.
Cross-domain questions apply to both.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class QuestionDomain(StrEnum):
    """Which domain a question applies to."""
    HUMAN_FRICTION = "human_friction"
    CONFLICT_WARFARE = "conflict_warfare"
    CROSS_DOMAIN = "cross_domain"


class AnalysisMode(StrEnum):
    """The reasoning mode needed to answer."""
    STRUCTURAL = "structural"       # Graph structure queries
    ESCALATION = "escalation"       # Glasl/Kriesberg analysis
    RIPENESS = "ripeness"           # Zartman ripeness assessment
    TRUST = "trust"                 # Mayer trust analysis
    POWER = "power"                 # French/Raven power analysis
    CAUSAL = "causal"               # Pearl causal chains
    NARRATIVE = "narrative"         # Winslade/Monk narrative analysis
    NETWORK = "network"             # Alliance/opposition network
    FORECASTING = "forecasting"     # Scenario prediction
    INTERVENTION = "intervention"   # Process/resolution recommendation
    EMOTION = "emotion"             # Plutchik emotional analysis
    GENERAL = "general"             # Full pipeline query


class Difficulty(StrEnum):
    """Question difficulty for benchmarking."""
    BASIC = "basic"          # Directly answerable from graph structure
    INTERMEDIATE = "intermediate"  # Requires symbolic reasoning
    ADVANCED = "advanced"    # Requires multi-hop reasoning + synthesis
    EXPERT = "expert"        # Requires theory integration + inference


class AnswerType(StrEnum):
    """Expected answer format."""
    DETERMINISTIC = "deterministic"  # Single correct answer from symbolic rules
    SCORED = "scored"                # Numeric score (0-1 or stage number)
    LIST = "list"                    # List of entities/items
    NARRATIVE = "narrative"          # Free-text analytical answer
    BOOLEAN = "boolean"              # Yes/no with justification
    COMPARATIVE = "comparative"      # Comparison between entities/scenarios


@dataclass(frozen=True)
class BenchmarkQuestion:
    """A single benchmark question for ConflictCorpus evaluation."""
    id: str
    text: str
    domain: QuestionDomain
    mode: AnalysisMode
    difficulty: Difficulty
    answer_type: AnswerType
    theory: str = ""  # Which theory framework this tests
    requires_node_types: tuple[str, ...] = ()  # Node types needed to answer
    requires_edge_types: tuple[str, ...] = ()  # Edge types needed to answer
    scoring_rubric: str = ""  # How to score the answer
    tags: tuple[str, ...] = ()


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-DOMAIN QUESTIONS (applicable to ANY ConflictCorpus)
# ═══════════════════════════════════════════════════════════════════════════════

CROSS_DOMAIN_QUESTIONS: tuple[BenchmarkQuestion, ...] = (
    # ── Structural ────────────────────────────────────────────────────────
    BenchmarkQuestion(
        id="cd-struct-01",
        text="How many distinct parties (actors) are involved in this conflict?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.STRUCTURAL,
        difficulty=Difficulty.BASIC,
        answer_type=AnswerType.SCORED,
        requires_node_types=("Actor",),
        scoring_rubric="Exact count match = 1.0, within 1 = 0.8, within 2 = 0.5",
    ),
    BenchmarkQuestion(
        id="cd-struct-02",
        text="What are the core issues at stake in this conflict?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.STRUCTURAL,
        difficulty=Difficulty.BASIC,
        answer_type=AnswerType.LIST,
        requires_node_types=("Issue",),
        scoring_rubric="Precision/recall of issue names vs gold standard",
    ),
    BenchmarkQuestion(
        id="cd-struct-03",
        text="What is the graph density of this conflict (ratio of edges to possible edges)?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.STRUCTURAL,
        difficulty=Difficulty.BASIC,
        answer_type=AnswerType.SCORED,
        scoring_rubric="Within 0.05 of actual density = 1.0",
    ),
    BenchmarkQuestion(
        id="cd-struct-04",
        text="Which actor has the highest degree centrality (most connections)?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.NETWORK,
        difficulty=Difficulty.INTERMEDIATE,
        answer_type=AnswerType.DETERMINISTIC,
        requires_node_types=("Actor",),
        scoring_rubric="Exact match = 1.0",
    ),

    # ── Escalation ────────────────────────────────────────────────────────
    BenchmarkQuestion(
        id="cd-esc-01",
        text="At what Glasl escalation stage is this conflict?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.ESCALATION,
        difficulty=Difficulty.INTERMEDIATE,
        answer_type=AnswerType.DETERMINISTIC,
        theory="glasl",
        requires_node_types=("Conflict", "Event"),
        scoring_rubric="Exact stage = 1.0, within 1 = 0.7, within 2 = 0.3",
    ),
    BenchmarkQuestion(
        id="cd-esc-02",
        text="Is the conflict escalating, de-escalating, or stable? What is the trajectory?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.ESCALATION,
        difficulty=Difficulty.INTERMEDIATE,
        answer_type=AnswerType.DETERMINISTIC,
        theory="glasl",
        requires_node_types=("Event",),
        scoring_rubric="Direction match = 0.6, velocity within 0.2 = 0.4",
    ),
    BenchmarkQuestion(
        id="cd-esc-03",
        text="What specific events have driven escalation in this conflict?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.CAUSAL,
        difficulty=Difficulty.ADVANCED,
        answer_type=AnswerType.LIST,
        theory="pearl_causal",
        requires_node_types=("Event",),
        requires_edge_types=("CAUSED",),
        scoring_rubric="Precision/recall of escalation-driving events",
    ),

    # ── Ripeness ──────────────────────────────────────────────────────────
    BenchmarkQuestion(
        id="cd-ripe-01",
        text="Is this conflict ripe for resolution? What are the MHS and MEO indicators?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.RIPENESS,
        difficulty=Difficulty.ADVANCED,
        answer_type=AnswerType.BOOLEAN,
        theory="zartman",
        scoring_rubric="Ripeness boolean match = 0.4, MHS score within 0.1 = 0.3, MEO within 0.1 = 0.3",
    ),

    # ── Trust ─────────────────────────────────────────────────────────────
    BenchmarkQuestion(
        id="cd-trust-01",
        text="What are the trust dynamics between the primary parties?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.TRUST,
        difficulty=Difficulty.INTERMEDIATE,
        answer_type=AnswerType.NARRATIVE,
        theory="mayer_trust",
        requires_node_types=("TrustState", "Actor"),
        requires_edge_types=("TRUSTS",),
        scoring_rubric="Identifies trust dyads with ability/benevolence/integrity breakdown",
    ),

    # ── Power ─────────────────────────────────────────────────────────────
    BenchmarkQuestion(
        id="cd-power-01",
        text="What power asymmetries exist between the parties? Which domains of power are most significant?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.POWER,
        difficulty=Difficulty.INTERMEDIATE,
        answer_type=AnswerType.NARRATIVE,
        theory="french_raven",
        requires_node_types=("PowerDynamic", "Actor"),
        requires_edge_types=("HAS_POWER_OVER",),
        scoring_rubric="Identifies power domains and asymmetries correctly",
    ),

    # ── Causal ────────────────────────────────────────────────────────────
    BenchmarkQuestion(
        id="cd-causal-01",
        text="What are the primary causal chains in this conflict? What triggered what?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.CAUSAL,
        difficulty=Difficulty.ADVANCED,
        answer_type=AnswerType.LIST,
        theory="pearl_causal",
        requires_edge_types=("CAUSED",),
        scoring_rubric="Causal chain accuracy (event ordering + causation links)",
    ),

    # ── Narrative ─────────────────────────────────────────────────────────
    BenchmarkQuestion(
        id="cd-narr-01",
        text="What are the dominant narratives held by each party? Are there counter-narratives?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.NARRATIVE,
        difficulty=Difficulty.ADVANCED,
        answer_type=AnswerType.NARRATIVE,
        theory="winslade_monk",
        requires_node_types=("Narrative",),
        scoring_rubric="Identifies party-specific narratives with frame analysis",
    ),

    # ── Intervention ──────────────────────────────────────────────────────
    BenchmarkQuestion(
        id="cd-intv-01",
        text="What type of intervention is most appropriate at this stage of the conflict?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.INTERVENTION,
        difficulty=Difficulty.EXPERT,
        answer_type=AnswerType.NARRATIVE,
        theory="glasl",
        scoring_rubric="Intervention matches Glasl stage-appropriate recommendation",
    ),
    BenchmarkQuestion(
        id="cd-intv-02",
        text="Which theoretical framework best explains this conflict and why?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.GENERAL,
        difficulty=Difficulty.EXPERT,
        answer_type=AnswerType.NARRATIVE,
        scoring_rubric="Framework selection reasonableness + justification quality",
    ),

    # ── Forecasting ───────────────────────────────────────────────────────
    BenchmarkQuestion(
        id="cd-fore-01",
        text="What are the most likely scenarios for how this conflict evolves?",
        domain=QuestionDomain.CROSS_DOMAIN,
        mode=AnalysisMode.FORECASTING,
        difficulty=Difficulty.EXPERT,
        answer_type=AnswerType.NARRATIVE,
        scoring_rubric="Scenario plausibility, grounding in evidence, probability calibration",
    ),
)

# ═══════════════════════════════════════════════════════════════════════════════
# HUMAN FRICTION DOMAIN QUESTIONS
# ═══════════════════════════════════════════════════════════════════════════════

HUMAN_FRICTION_QUESTIONS: tuple[BenchmarkQuestion, ...] = (
    BenchmarkQuestion(
        id="hf-int-01",
        text="What are the underlying interests (not positions) of each party?",
        domain=QuestionDomain.HUMAN_FRICTION,
        mode=AnalysisMode.GENERAL,
        difficulty=Difficulty.INTERMEDIATE,
        answer_type=AnswerType.LIST,
        theory="fisher_ury",
        requires_node_types=("Interest", "Actor"),
        requires_edge_types=("HAS_INTEREST",),
        scoring_rubric="Interest identification accuracy (stated vs underlying)",
        tags=("negotiation", "interests"),
    ),
    BenchmarkQuestion(
        id="hf-int-02",
        text="What is each party's BATNA (Best Alternative to Negotiated Agreement)?",
        domain=QuestionDomain.HUMAN_FRICTION,
        mode=AnalysisMode.GENERAL,
        difficulty=Difficulty.ADVANCED,
        answer_type=AnswerType.NARRATIVE,
        theory="fisher_ury",
        requires_node_types=("Interest",),
        scoring_rubric="BATNA identification + strength assessment accuracy",
        tags=("negotiation", "batna"),
    ),
    BenchmarkQuestion(
        id="hf-int-03",
        text="Is there a Zone of Possible Agreement (ZOPA)? Where do interests overlap?",
        domain=QuestionDomain.HUMAN_FRICTION,
        mode=AnalysisMode.GENERAL,
        difficulty=Difficulty.ADVANCED,
        answer_type=AnswerType.BOOLEAN,
        theory="fisher_ury",
        scoring_rubric="ZOPA identification + overlap area description",
        tags=("negotiation", "zopa"),
    ),
    BenchmarkQuestion(
        id="hf-emo-01",
        text="What emotional states are present? How do emotions affect the conflict dynamics?",
        domain=QuestionDomain.HUMAN_FRICTION,
        mode=AnalysisMode.EMOTION,
        difficulty=Difficulty.INTERMEDIATE,
        answer_type=AnswerType.NARRATIVE,
        theory="plutchik",
        requires_node_types=("EmotionalState",),
        scoring_rubric="Emotion identification + impact analysis",
        tags=("emotions", "dynamics"),
    ),
    BenchmarkQuestion(
        id="hf-trust-01",
        text="Has there been a trust breach? Which dimension (ability, benevolence, integrity) was affected?",
        domain=QuestionDomain.HUMAN_FRICTION,
        mode=AnalysisMode.TRUST,
        difficulty=Difficulty.INTERMEDIATE,
        answer_type=AnswerType.NARRATIVE,
        theory="mayer_trust",
        requires_node_types=("TrustState",),
        scoring_rubric="Trust breach detection + dimension identification",
        tags=("trust", "breach"),
    ),
    BenchmarkQuestion(
        id="hf-proc-01",
        text="What dispute resolution process is most appropriate? Facilitation, mediation, or arbitration?",
        domain=QuestionDomain.HUMAN_FRICTION,
        mode=AnalysisMode.INTERVENTION,
        difficulty=Difficulty.ADVANCED,
        answer_type=AnswerType.DETERMINISTIC,
        theory="ury_brett_goldberg",
        requires_node_types=("Process",),
        scoring_rubric="Process selection matches escalation level and party dynamics",
        tags=("process", "resolution"),
    ),
    BenchmarkQuestion(
        id="hf-style-01",
        text="What conflict handling style is each party using? (competing, collaborating, compromising, avoiding, accommodating)",
        domain=QuestionDomain.HUMAN_FRICTION,
        mode=AnalysisMode.GENERAL,
        difficulty=Difficulty.INTERMEDIATE,
        answer_type=AnswerType.LIST,
        theory="thomas_kilmann",
        scoring_rubric="Style identification accuracy per party",
        tags=("style", "thomas_kilmann"),
    ),
    BenchmarkQuestion(
        id="hf-outcome-01",
        text="What value-creating options exist? Can the outcome be integrative rather than distributive?",
        domain=QuestionDomain.HUMAN_FRICTION,
        mode=AnalysisMode.INTERVENTION,
        difficulty=Difficulty.EXPERT,
        answer_type=AnswerType.NARRATIVE,
        theory="fisher_ury",
        scoring_rubric="Creative option generation grounded in interests",
        tags=("options", "value_creation"),
    ),
    BenchmarkQuestion(
        id="hf-needs-01",
        text="What basic human needs (identity, security, recognition) are at stake?",
        domain=QuestionDomain.HUMAN_FRICTION,
        mode=AnalysisMode.GENERAL,
        difficulty=Difficulty.ADVANCED,
        answer_type=AnswerType.LIST,
        theory="burton_basic_needs",
        scoring_rubric="Needs identification beyond surface interests",
        tags=("needs", "identity"),
    ),
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFLICT & WARFARE DOMAIN QUESTIONS
# ═══════════════════════════════════════════════════════════════════════════════

CONFLICT_WARFARE_QUESTIONS: tuple[BenchmarkQuestion, ...] = (
    BenchmarkQuestion(
        id="cw-class-01",
        text="What type of conflict is this? (interstate, intrastate, non-state, internationalized internal)",
        domain=QuestionDomain.CONFLICT_WARFARE,
        mode=AnalysisMode.STRUCTURAL,
        difficulty=Difficulty.BASIC,
        answer_type=AnswerType.DETERMINISTIC,
        requires_node_types=("Conflict", "Actor"),
        scoring_rubric="UCDP conflict type classification accuracy",
        tags=("classification", "ucdp"),
    ),
    BenchmarkQuestion(
        id="cw-class-02",
        text="What is the primary incompatibility? (territory, government, resources, ideology)",
        domain=QuestionDomain.CONFLICT_WARFARE,
        mode=AnalysisMode.STRUCTURAL,
        difficulty=Difficulty.BASIC,
        answer_type=AnswerType.DETERMINISTIC,
        requires_node_types=("Conflict", "Issue"),
        scoring_rubric="UCDP incompatibility type accuracy",
        tags=("classification", "incompatibility"),
    ),
    BenchmarkQuestion(
        id="cw-alliance-01",
        text="Map the alliance structure. Who are allies, opponents, and neutral parties?",
        domain=QuestionDomain.CONFLICT_WARFARE,
        mode=AnalysisMode.NETWORK,
        difficulty=Difficulty.INTERMEDIATE,
        answer_type=AnswerType.NARRATIVE,
        requires_edge_types=("ALLIED_WITH", "OPPOSED_TO"),
        scoring_rubric="Alliance/opposition pair identification precision/recall",
        tags=("alliances", "network"),
    ),
    BenchmarkQuestion(
        id="cw-norm-01",
        text="What international norms or treaties have been violated? By whom?",
        domain=QuestionDomain.CONFLICT_WARFARE,
        mode=AnalysisMode.STRUCTURAL,
        difficulty=Difficulty.INTERMEDIATE,
        answer_type=AnswerType.LIST,
        requires_node_types=("Norm", "Event"),
        requires_edge_types=("VIOLATED",),
        scoring_rubric="Norm violation detection accuracy",
        tags=("norms", "violations"),
    ),
    BenchmarkQuestion(
        id="cw-power-01",
        text="What is the military power balance? Who has escalation dominance?",
        domain=QuestionDomain.CONFLICT_WARFARE,
        mode=AnalysisMode.POWER,
        difficulty=Difficulty.ADVANCED,
        answer_type=AnswerType.NARRATIVE,
        theory="french_raven",
        requires_node_types=("PowerDynamic", "Actor"),
        scoring_rubric="Power balance assessment + escalation dominance identification",
        tags=("power", "military"),
    ),
    BenchmarkQuestion(
        id="cw-ripe-01",
        text="Is there a Mutually Hurting Stalemate (MHS)? What indicators support this?",
        domain=QuestionDomain.CONFLICT_WARFARE,
        mode=AnalysisMode.RIPENESS,
        difficulty=Difficulty.ADVANCED,
        answer_type=AnswerType.BOOLEAN,
        theory="zartman",
        scoring_rubric="MHS detection + indicator enumeration",
        tags=("ripeness", "mhs"),
    ),
    BenchmarkQuestion(
        id="cw-ripe-02",
        text="Is there a Mutually Enticing Opportunity (MEO)? What would make resolution attractive?",
        domain=QuestionDomain.CONFLICT_WARFARE,
        mode=AnalysisMode.RIPENESS,
        difficulty=Difficulty.ADVANCED,
        answer_type=AnswerType.NARRATIVE,
        theory="zartman",
        scoring_rubric="MEO identification + incentive structure analysis",
        tags=("ripeness", "meo"),
    ),
    BenchmarkQuestion(
        id="cw-prot-01",
        text="Is this a protracted social conflict? What communal identity factors are driving it?",
        domain=QuestionDomain.CONFLICT_WARFARE,
        mode=AnalysisMode.GENERAL,
        difficulty=Difficulty.ADVANCED,
        answer_type=AnswerType.BOOLEAN,
        theory="azar_protracted",
        scoring_rubric="PSC classification + identity factor identification",
        tags=("protracted", "identity"),
    ),
    BenchmarkQuestion(
        id="cw-struct-01",
        text="Using Galtung's ABC triangle, what are the Attitudes, Behaviors, and Contradictions?",
        domain=QuestionDomain.CONFLICT_WARFARE,
        mode=AnalysisMode.GENERAL,
        difficulty=Difficulty.ADVANCED,
        answer_type=AnswerType.NARRATIVE,
        theory="galtung",
        scoring_rubric="ABC identification with evidence from graph",
        tags=("structural_violence", "galtung"),
    ),
    BenchmarkQuestion(
        id="cw-proxy-01",
        text="Are there proxy actors? Which external powers are operating through local parties?",
        domain=QuestionDomain.CONFLICT_WARFARE,
        mode=AnalysisMode.NETWORK,
        difficulty=Difficulty.ADVANCED,
        answer_type=AnswerType.LIST,
        requires_edge_types=("HAS_POWER_OVER", "ALLIED_WITH"),
        scoring_rubric="Proxy relationship identification accuracy",
        tags=("proxy", "external_actors"),
    ),
    BenchmarkQuestion(
        id="cw-intv-01",
        text="What intervention approach does Glasl's model recommend at this stage?",
        domain=QuestionDomain.CONFLICT_WARFARE,
        mode=AnalysisMode.INTERVENTION,
        difficulty=Difficulty.INTERMEDIATE,
        answer_type=AnswerType.DETERMINISTIC,
        theory="glasl",
        scoring_rubric="Intervention type matches Glasl stage recommendation",
        tags=("intervention", "glasl"),
    ),
    BenchmarkQuestion(
        id="cw-fore-01",
        text="Based on historical patterns, what is the most likely trajectory? What are the spoiler risks?",
        domain=QuestionDomain.CONFLICT_WARFARE,
        mode=AnalysisMode.FORECASTING,
        difficulty=Difficulty.EXPERT,
        answer_type=AnswerType.NARRATIVE,
        scoring_rubric="Scenario plausibility + spoiler identification",
        tags=("forecasting", "spoilers"),
    ),
    BenchmarkQuestion(
        id="cw-transform-01",
        text="What would a conflict transformation approach look like? (Lederach: personal, relational, structural, cultural)",
        domain=QuestionDomain.CONFLICT_WARFARE,
        mode=AnalysisMode.INTERVENTION,
        difficulty=Difficulty.EXPERT,
        answer_type=AnswerType.NARRATIVE,
        theory="lederach_transformation",
        scoring_rubric="Multi-level transformation strategy grounded in evidence",
        tags=("transformation", "lederach"),
    ),
)


# ═══════════════════════════════════════════════════════════════════════════════
# QUESTION REGISTRY & UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════


ALL_QUESTIONS: tuple[BenchmarkQuestion, ...] = (
    CROSS_DOMAIN_QUESTIONS + HUMAN_FRICTION_QUESTIONS + CONFLICT_WARFARE_QUESTIONS
)

QUESTION_BY_ID: dict[str, BenchmarkQuestion] = {q.id: q for q in ALL_QUESTIONS}


def get_questions_for_domain(domain: str) -> list[BenchmarkQuestion]:
    """Get all questions applicable to a domain (includes cross-domain)."""
    questions = list(CROSS_DOMAIN_QUESTIONS)
    if domain == "human_friction":
        questions.extend(HUMAN_FRICTION_QUESTIONS)
    elif domain == "conflict_warfare":
        questions.extend(CONFLICT_WARFARE_QUESTIONS)
    else:
        questions.extend(HUMAN_FRICTION_QUESTIONS)
        questions.extend(CONFLICT_WARFARE_QUESTIONS)
    return questions


def get_questions_by_mode(mode: str) -> list[BenchmarkQuestion]:
    """Get all questions for a specific analysis mode."""
    return [q for q in ALL_QUESTIONS if q.mode == mode]


def get_questions_by_theory(theory: str) -> list[BenchmarkQuestion]:
    """Get all questions testing a specific theory framework."""
    return [q for q in ALL_QUESTIONS if q.theory == theory]


def get_questions_by_difficulty(difficulty: str) -> list[BenchmarkQuestion]:
    """Get all questions at a specific difficulty level."""
    return [q for q in ALL_QUESTIONS if q.difficulty == difficulty]


def get_minimum_coverage_questions() -> list[BenchmarkQuestion]:
    """Get the minimum set of questions every ConflictCorpus should be able to answer.

    These are the 'quality gate' questions — if a corpus can't answer these,
    the extraction was insufficient.
    """
    minimum_ids = {
        "cd-struct-01",  # Actor count
        "cd-struct-02",  # Core issues
        "cd-esc-01",     # Glasl stage
        "cd-esc-02",     # Escalation direction
        "cd-ripe-01",    # Ripeness
        "cd-trust-01",   # Trust dynamics
        "cd-power-01",   # Power asymmetries
        "cd-causal-01",  # Causal chains
        "cd-intv-01",    # Intervention recommendation
    }
    return [q for q in ALL_QUESTIONS if q.id in minimum_ids]


# Summary stats
TOTAL_QUESTIONS = len(ALL_QUESTIONS)
CROSS_DOMAIN_COUNT = len(CROSS_DOMAIN_QUESTIONS)
HUMAN_FRICTION_COUNT = len(HUMAN_FRICTION_QUESTIONS)
CONFLICT_WARFARE_COUNT = len(CONFLICT_WARFARE_QUESTIONS)
