"""
Kriesberg Theory Framework — DIALECTICA implementation.

Louis Kriesberg's conflict lifecycle model with 7 phases from
latent conflict through post-conflict transformation.
"""
from __future__ import annotations

from dialectica_ontology.theory.base import (
    DiagnosticQuestion,
    TheoryFramework,
)

# 7-phase conflict lifecycle
PHASES: dict[str, dict[str, str]] = {
    "latent": {
        "name": "Latent Conflict",
        "description": "Underlying conditions exist but conflict has not yet emerged.",
        "indicators": "structural_inequality,unmet_needs,grievance_accumulation",
        "intervention": "Early prevention through addressing root causes.",
    },
    "emergence": {
        "name": "Conflict Emergence",
        "description": "Parties become aware of incompatible goals and begin mobilising.",
        "indicators": "awareness,mobilisation,grievance_expression,identity_formation",
        "intervention": "Dialogue and problem-solving before positions harden.",
    },
    "escalation": {
        "name": "Escalation",
        "description": "Conflict intensifies through hostile actions and rhetoric.",
        "indicators": "hostility,polarisation,violence,threat,coalition_building",
        "intervention": "De-escalation efforts, mediation, confidence-building measures.",
    },
    "stalemate": {
        "name": "Stalemate",
        "description": "Neither party can prevail; costs of continuing rise.",
        "indicators": "exhaustion,mutual_damage,impasse,hurting_stalemate",
        "intervention": "Ripeness assessment and exploration of negotiated settlement.",
    },
    "de_escalation": {
        "name": "De-escalation",
        "description": "Parties begin to reduce hostilities and explore settlement.",
        "indicators": "ceasefire,negotiation,concession,trust_building",
        "intervention": "Support negotiation process, build trust, address spoilers.",
    },
    "settlement": {
        "name": "Settlement / Resolution",
        "description": "Parties reach an agreement to end the conflict.",
        "indicators": "agreement,compromise,treaty,accord,resolution",
        "intervention": "Ensure agreement addresses root causes; implementation support.",
    },
    "post_conflict": {
        "name": "Post-Conflict Transformation",
        "description": "Rebuilding relationships and structures after settlement.",
        "indicators": "reconciliation,reconstruction,justice,healing,institution_building",
        "intervention": "Transitional justice, reconciliation processes, structural reform.",
    },
}

_PHASE_ORDER = [
    "latent", "emergence", "escalation", "stalemate",
    "de_escalation", "settlement", "post_conflict",
]


class KriesbergFramework(TheoryFramework):
    """Louis Kriesberg's conflict lifecycle model.

    Tracks conflicts through 7 phases: latent, emergence, escalation,
    stalemate, de-escalation, settlement, and post-conflict transformation.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Kriesberg Conflict Lifecycle"
        self.author = "Louis Kriesberg"
        self.key_concepts = [
            "conflict_lifecycle",
            "latent_conflict",
            "emergence",
            "escalation",
            "stalemate",
            "de_escalation",
            "settlement",
            "post_conflict_transformation",
        ]

    def describe(self) -> str:
        return (
            "Kriesberg's conflict lifecycle model traces conflicts through "
            "seven phases: latent conditions, emergence, escalation, stalemate, "
            "de-escalation, settlement, and post-conflict transformation. "
            "Understanding the current phase guides appropriate intervention strategy."
        )

    def detect_phase(self, indicators: dict) -> str:
        """Detect the current conflict lifecycle phase from indicators.

        Args:
            indicators: Dict with optional keys: 'keywords' (list[str]),
                'violence_level' (float 0-1), 'negotiation_active' (bool),
                'agreement_reached' (bool), 'post_conflict' (bool).

        Returns:
            Phase identifier string (e.g. 'escalation', 'stalemate').
        """
        keywords = set(indicators.get("keywords", []))

        # Check explicit flags first
        if indicators.get("post_conflict"):
            return "post_conflict"
        if indicators.get("agreement_reached"):
            return "settlement"
        if indicators.get("negotiation_active") and indicators.get("violence_level", 0) < 0.3:
            return "de_escalation"

        # Keyword matching — score each phase
        best_phase = "latent"
        best_score = 0
        for phase_id, phase_data in PHASES.items():
            phase_keywords = set(phase_data["indicators"].split(","))
            overlap = len(keywords & phase_keywords)
            if overlap > best_score:
                best_score = overlap
                best_phase = phase_id

        # Violence level heuristic
        violence = indicators.get("violence_level", 0.0)
        if violence > 0.7 and best_phase in ("latent", "emergence"):
            best_phase = "escalation"
        elif violence > 0.3 and best_phase == "latent":
            best_phase = "emergence"

        return best_phase

    def assess(self, graph_context: dict) -> dict:
        """Assess a conflict using the Kriesberg lifecycle model.

        Returns dict with phase, phase_name, description, intervention,
        phase_index, and trajectory.
        """
        indicators = graph_context.get("indicators", graph_context)
        phase = self.detect_phase(indicators)
        phase_data = PHASES[phase]
        phase_index = _PHASE_ORDER.index(phase)

        trajectory = "unknown"
        if phase_index <= 2:
            trajectory = "escalating"
        elif phase_index == 3:
            trajectory = "stalled"
        elif phase_index >= 4:
            trajectory = "de-escalating"

        return {
            "phase": phase,
            "phase_name": phase_data["name"],
            "description": phase_data["description"],
            "intervention": phase_data["intervention"],
            "phase_index": phase_index,
            "total_phases": len(_PHASE_ORDER),
            "trajectory": trajectory,
        }

    def score(self, graph_context: dict) -> float:
        """Score relevance — higher when lifecycle indicators are present."""
        indicators = graph_context.get("indicators", graph_context)
        signals = 0
        total = 4

        if indicators.get("keywords"):
            signals += 1
        if "violence_level" in indicators:
            signals += 1
        if "negotiation_active" in indicators:
            signals += 1
        if graph_context.get("history"):
            signals += 1

        return round(signals / total, 2)

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        return [
            DiagnosticQuestion(
                question="How long has this conflict been ongoing, and how has it changed over time?",
                framework=self.name,
                purpose="Determine lifecycle phase and trajectory",
                response_type="open",
            ),
            DiagnosticQuestion(
                question="Are the parties currently engaged in any form of negotiation or dialogue?",
                framework=self.name,
                purpose="Detect de-escalation or settlement phase",
                response_type="boolean",
            ),
        ]
