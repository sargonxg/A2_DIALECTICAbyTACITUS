"""
Glasl Theory Framework — DIALECTICA implementation.

Friedrich Glasl's 9-stage model of conflict escalation.
Each stage belongs to one of three levels (win-win, win-lose, lose-lose)
and maps to appropriate intervention strategies.
"""
from __future__ import annotations

from dialectica_ontology.theory.base import (
    DiagnosticQuestion,
    TheoryFramework,
)

# Full 9-stage escalation model
STAGES: dict[int, dict[str, str]] = {
    1: {
        "name": "Hardening",
        "level": "win-win",
        "description": "Positions harden; tension but still belief in resolution through talk.",
        "intervention": "moderation",
    },
    2: {
        "name": "Debate and Polemics",
        "level": "win-win",
        "description": "Polarisation; verbal confrontation and pressure tactics emerge.",
        "intervention": "process_consultation",
    },
    3: {
        "name": "Actions Not Words",
        "level": "win-win",
        "description": "Talk yields to action; empathy declines, fait accompli tactics.",
        "intervention": "process_consultation",
    },
    4: {
        "name": "Images and Coalitions",
        "level": "win-lose",
        "description": "Stereotypes form; parties recruit allies and campaign for support.",
        "intervention": "socio_therapeutic_process",
    },
    5: {
        "name": "Loss of Face",
        "level": "win-lose",
        "description": "Public attacks on opponent's moral credibility; demonisation.",
        "intervention": "mediation",
    },
    6: {
        "name": "Strategies of Threats",
        "level": "win-lose",
        "description": "Threats and counter-threats; ultimatums and demonstrations of power.",
        "intervention": "mediation",
    },
    7: {
        "name": "Limited Destructive Blows",
        "level": "lose-lose",
        "description": "Opponent seen as non-human; limited attacks to inflict damage.",
        "intervention": "arbitration",
    },
    8: {
        "name": "Fragmentation of the Enemy",
        "level": "lose-lose",
        "description": "Goal is to destroy opponent's system; frontal attacks.",
        "intervention": "power_intervention",
    },
    9: {
        "name": "Together into the Abyss",
        "level": "lose-lose",
        "description": "Total confrontation; self-destruction acceptable if enemy is destroyed.",
        "intervention": "power_intervention",
    },
}

# Keywords that suggest each stage
_STAGE_INDICATORS: dict[int, list[str]] = {
    1: ["tension", "disagreement", "hardening", "frustration"],
    2: ["debate", "argument", "polarisation", "verbal_conflict"],
    3: ["action", "fait_accompli", "empathy_loss", "unilateral"],
    4: ["coalition", "stereotype", "allies", "image_campaign"],
    5: ["loss_of_face", "moral_attack", "demonisation", "public_attack"],
    6: ["threat", "ultimatum", "coercion", "demand"],
    7: ["limited_attack", "sabotage", "dehumanisation", "destruction"],
    8: ["fragmentation", "systemic_attack", "annihilation", "total_war"],
    9: ["abyss", "mutual_destruction", "suicide_attack", "no_return"],
}


class GlaslFramework(TheoryFramework):
    """Friedrich Glasl's 9-stage conflict escalation model.

    Provides heuristic detection of escalation stage, level classification,
    and intervention recommendations calibrated to the current stage.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Glasl Escalation Model"
        self.author = "Friedrich Glasl"
        self.key_concepts = [
            "escalation_stages",
            "win_win",
            "win_lose",
            "lose_lose",
            "de_escalation",
            "intervention_threshold",
        ]

    def describe(self) -> str:
        return (
            "Glasl's 9-stage model describes conflict escalation from mild "
            "tension (Stage 1) to mutual destruction (Stage 9). Stages 1-3 "
            "are win-win, 4-6 are win-lose, and 7-9 are lose-lose. Each "
            "threshold shift requires progressively stronger intervention."
        )

    def detect_stage(self, indicators: dict) -> int:
        """Heuristically detect the current escalation stage.

        Args:
            indicators: Dict with keys like 'keywords' (list[str]),
                'intensity' (float 0-1), 'violence_present' (bool),
                'dehumanisation' (bool), 'threats' (bool).

        Returns:
            Integer 1-9 representing the detected stage.
        """
        keywords = set(indicators.get("keywords", []))
        intensity = indicators.get("intensity", 0.0)
        violence = indicators.get("violence_present", False)
        dehumanisation = indicators.get("dehumanisation", False)
        threats = indicators.get("threats", False)

        # Check keyword overlap per stage (highest matching stage wins)
        best_stage = 1
        best_overlap = 0
        for stage, stage_keywords in _STAGE_INDICATORS.items():
            overlap = len(keywords & set(stage_keywords))
            if overlap > best_overlap:
                best_overlap = overlap
                best_stage = stage

        # Adjust based on behavioural indicators
        if violence and best_stage < 7:
            best_stage = 7
        elif dehumanisation and best_stage < 5:
            best_stage = 5
        elif threats and best_stage < 6:
            best_stage = 6

        # Intensity-based floor
        intensity_floor = max(1, int(intensity * 9))
        best_stage = max(best_stage, intensity_floor)

        return min(best_stage, 9)

    def recommend_intervention(self, stage: int) -> str:
        """Return the recommended intervention type for a given stage.

        Args:
            stage: Escalation stage (1-9).

        Returns:
            String describing the recommended intervention approach.
        """
        stage = max(1, min(stage, 9))
        stage_data = STAGES[stage]
        intervention = stage_data["intervention"]

        descriptions = {
            "moderation": (
                "Moderation/facilitation: A light-touch facilitator helps "
                "parties communicate more effectively and find common ground."
            ),
            "process_consultation": (
                "Process consultation: A consultant helps parties examine and "
                "improve their interaction patterns and decision-making processes."
            ),
            "socio_therapeutic_process": (
                "Socio-therapeutic process work: Structured sessions to address "
                "the social and psychological dynamics driving the conflict."
            ),
            "mediation": (
                "Mediation: A neutral third party actively facilitates "
                "negotiation, helping parties reach a mutually acceptable agreement."
            ),
            "arbitration": (
                "Arbitration: An authoritative third party imposes a binding "
                "decision after hearing both sides."
            ),
            "power_intervention": (
                "Power intervention: An authority with coercive power intervenes "
                "to stop the conflict and impose conditions for resolution."
            ),
        }
        return descriptions.get(intervention, intervention)

    def assess(self, graph_context: dict) -> dict:
        """Assess a conflict context using the Glasl escalation model.

        Args:
            graph_context: Dict with optional keys: 'indicators', 'keywords',
                'intensity', 'violence_present', 'dehumanisation', 'threats'.

        Returns:
            Dict with 'stage', 'stage_name', 'level', 'intervention',
            'description', and 'prognosis'.
        """
        indicators = graph_context.get("indicators", graph_context)
        stage = self.detect_stage(indicators)
        stage_data = STAGES[stage]

        prognosis_map = {
            "win-win": "Conflict is still manageable through cooperative means.",
            "win-lose": "Conflict has escalated; third-party intervention recommended.",
            "lose-lose": "Conflict is destructive; urgent power intervention needed.",
        }

        return {
            "stage": stage,
            "stage_name": stage_data["name"],
            "level": stage_data["level"],
            "intervention": self.recommend_intervention(stage),
            "description": stage_data["description"],
            "prognosis": prognosis_map[stage_data["level"]],
        }

    def score(self, graph_context: dict) -> float:
        """Score framework relevance based on presence of escalation indicators.

        Returns higher scores when escalation-related data is present.
        """
        indicators = graph_context.get("indicators", graph_context)
        signals = 0
        total = 5

        if indicators.get("keywords"):
            signals += 1
        if indicators.get("intensity") is not None:
            signals += 1
        if "violence_present" in indicators:
            signals += 1
        if "threats" in indicators:
            signals += 1
        if len(graph_context.get("parties", [])) >= 2:
            signals += 1

        return round(signals / total, 2)

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        return [
            DiagnosticQuestion(
                question="How would you describe the current intensity of the conflict on a scale of 1-10?",
                framework=self.name,
                purpose="Estimate escalation stage",
                response_type="scale",
            ),
            DiagnosticQuestion(
                question="Are parties still willing to talk directly to each other?",
                framework=self.name,
                purpose="Determine if conflict is still in win-win range",
                response_type="boolean",
            ),
            DiagnosticQuestion(
                question="Have there been any threats, ultimatums, or acts of coercion?",
                framework=self.name,
                purpose="Detect escalation beyond stage 5",
                response_type="boolean",
            ),
        ]
