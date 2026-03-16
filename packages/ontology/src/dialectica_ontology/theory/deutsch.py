"""
Deutsch Theory Framework — DIALECTICA implementation.

Morton Deutsch's theory of cooperation and competition. Conflicts are
shaped by whether parties perceive their goals as positively linked
(cooperative) or negatively linked (competitive).
"""
from __future__ import annotations

from dialectica_ontology.theory.base import (
    DiagnosticQuestion,
    TheoryFramework,
)

INTERACTION_TYPES: dict[str, dict[str, str]] = {
    "cooperative": {
        "description": "Parties perceive their goals as positively linked; one's gain helps the other.",
        "dynamics": "Open communication, trust, mutual aid, shared problem-solving.",
        "outcomes": "Constructive conflict resolution, mutual benefit, stronger relationships.",
    },
    "competitive": {
        "description": "Parties perceive their goals as negatively linked; one's gain is the other's loss.",
        "dynamics": "Suspicion, deception, coercion, win-lose framing.",
        "outcomes": "Destructive conflict, escalation, damaged relationships.",
    },
    "mixed_motive": {
        "description": "Parties have both cooperative and competitive incentives.",
        "dynamics": "Complex dynamics with trust and suspicion coexisting.",
        "outcomes": "Outcome depends on which motive dominates the interaction.",
    },
    "individualistic": {
        "description": "Parties pursue their own goals with indifference to the other.",
        "dynamics": "Low engagement, minimal communication, parallel action.",
        "outcomes": "Missed opportunities for mutual gain; conflict may be latent.",
    },
}


class DeutschFramework(TheoryFramework):
    """Morton Deutsch's cooperation and competition theory.

    Analyses whether conflict parties perceive their goals as cooperatively
    or competitively linked, and predicts dynamics and outcomes accordingly.
    Deutsch's Crude Law of Social Relations: the characteristic processes
    and effects of a given type of social relationship tend to induce that
    type of social relationship.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Deutsch Cooperation-Competition Theory"
        self.author = "Morton Deutsch"
        self.key_concepts = [
            "cooperation",
            "competition",
            "goal_interdependence",
            "crude_law",
            "constructive_controversy",
            "trust",
            "promotive_interaction",
        ]

    def describe(self) -> str:
        return (
            "Deutsch's theory posits that conflict outcomes are determined "
            "by whether parties perceive their goals as cooperatively linked "
            "(positive interdependence) or competitively linked (negative "
            "interdependence). The 'Crude Law of Social Relations' states "
            "that cooperative processes breed further cooperation, while "
            "competitive processes breed further competition."
        )

    def assess_interaction_type(self, context: dict) -> str:
        """Determine the dominant interaction type.

        Args:
            context: Dict with optional keys: 'cooperation_signals' (list[str]),
                'competition_signals' (list[str]), 'trust_level' (float 0-1),
                'communication_quality' (str: 'open'|'guarded'|'hostile'),
                'keywords' (list[str]).

        Returns:
            One of 'cooperative', 'competitive', 'mixed_motive', 'individualistic'.
        """
        coop_signals = len(context.get("cooperation_signals", []))
        comp_signals = len(context.get("competition_signals", []))

        trust = context.get("trust_level", 0.5)
        comm = context.get("communication_quality", "")

        # Keyword-based scoring
        keywords = set(context.get("keywords", []))
        coop_kw = {"collaboration", "mutual", "shared", "trust", "joint", "together", "cooperation"}
        comp_kw = {"rivalry", "zero_sum", "win_lose", "adversarial", "threat", "competition", "hostile"}

        coop_signals += len(keywords & coop_kw)
        comp_signals += len(keywords & comp_kw)

        # Communication quality adjustment
        if comm == "open":
            coop_signals += 1
        elif comm == "hostile":
            comp_signals += 1

        # Trust adjustment
        if trust > 0.7:
            coop_signals += 1
        elif trust < 0.3:
            comp_signals += 1

        if coop_signals > 0 and comp_signals > 0:
            if coop_signals > comp_signals * 2:
                return "cooperative"
            elif comp_signals > coop_signals * 2:
                return "competitive"
            return "mixed_motive"
        elif coop_signals > 0:
            return "cooperative"
        elif comp_signals > 0:
            return "competitive"
        return "individualistic"

    def assess(self, graph_context: dict) -> dict:
        """Assess a conflict using cooperation-competition theory.

        Returns interaction type, dynamics, predicted outcomes, and recommendations.
        """
        context = graph_context.get("indicators", graph_context)
        interaction_type = self.assess_interaction_type(context)
        type_data = INTERACTION_TYPES[interaction_type]

        recommendations = []
        if interaction_type == "competitive":
            recommendations = [
                "Reframe the conflict from zero-sum to positive-sum where possible.",
                "Build trust through small cooperative gestures (tit-for-tat strategy).",
                "Establish norms for constructive controversy.",
            ]
        elif interaction_type == "mixed_motive":
            recommendations = [
                "Strengthen cooperative incentives while managing competitive dynamics.",
                "Use integrative bargaining to expand the pie before dividing it.",
            ]
        elif interaction_type == "individualistic":
            recommendations = [
                "Create awareness of interdependence between parties.",
                "Establish shared goals or common threats to motivate engagement.",
            ]
        else:
            recommendations = [
                "Maintain cooperative dynamics through continued open communication.",
                "Address any emerging competitive pressures early.",
            ]

        return {
            "interaction_type": interaction_type,
            "description": type_data["description"],
            "dynamics": type_data["dynamics"],
            "predicted_outcomes": type_data["outcomes"],
            "recommendations": recommendations,
        }

    def score(self, graph_context: dict) -> float:
        """Score relevance — higher when cooperation/competition data is present."""
        context = graph_context.get("indicators", graph_context)
        signals = 0
        total = 4

        if context.get("cooperation_signals") or context.get("competition_signals"):
            signals += 1
        if "trust_level" in context:
            signals += 1
        if "communication_quality" in context:
            signals += 1
        if context.get("keywords"):
            signals += 1

        return round(signals / total, 2)

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        return [
            DiagnosticQuestion(
                question="Do the parties see their goals as linked (one benefits when the other does)?",
                framework=self.name,
                purpose="Assess goal interdependence type",
                response_type="open",
            ),
            DiagnosticQuestion(
                question="How would you characterise the communication between parties: open, guarded, or hostile?",
                framework=self.name,
                purpose="Assess interaction quality",
                response_type="choice",
            ),
        ]
