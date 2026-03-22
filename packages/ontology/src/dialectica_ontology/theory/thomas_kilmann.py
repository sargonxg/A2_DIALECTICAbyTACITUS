"""
Thomas-Kilmann Theory Framework — DIALECTICA implementation.

Kenneth Thomas and Ralph Kilmann's Conflict Mode Instrument (TKI).
Five conflict-handling modes mapped along two dimensions:
assertiveness (concern for self) and cooperativeness (concern for other).
"""

from __future__ import annotations

from dialectica_ontology.theory.base import (
    DiagnosticQuestion,
    TheoryFramework,
)

# Five conflict handling modes with assertiveness/cooperativeness mapping
MODES: dict[str, dict[str, object]] = {
    "competing": {
        "assertiveness": "high",
        "cooperativeness": "low",
        "description": "Pursuing one's own concerns at the other's expense. Power-oriented.",
        "when_appropriate": (
            "When quick decisive action is vital, on important issues where "
            "unpopular actions must be taken, or against people who take advantage."
        ),
    },
    "collaborating": {
        "assertiveness": "high",
        "cooperativeness": "high",
        "description": "Working together to find a solution that fully satisfies both parties.",
        "when_appropriate": (
            "When both sets of concerns are too important to compromise, "
            "when you want to learn, or to merge insights from different perspectives."
        ),
    },
    "compromising": {
        "assertiveness": "medium",
        "cooperativeness": "medium",
        "description": "Finding an expedient, mutually acceptable solution that partially satisfies both.",  # noqa: E501
        "when_appropriate": (
            "When goals are moderately important, when opponents with equal "
            "power are committed to mutually exclusive goals, or as a temporary settlement."
        ),
    },
    "avoiding": {
        "assertiveness": "low",
        "cooperativeness": "low",
        "description": "Not pursuing own concerns or those of the other; sidestepping the issue.",
        "when_appropriate": (
            "When the issue is trivial, when there is no chance of winning, "
            "when the cost of confrontation outweighs the benefit, or to let people cool down."
        ),
    },
    "accommodating": {
        "assertiveness": "low",
        "cooperativeness": "high",
        "description": "Neglecting own concerns to satisfy the other party's concerns.",
        "when_appropriate": (
            "When you realise you are wrong, when the issue is more important "
            "to the other, to build goodwill, or when continued competition would be damaging."
        ),
    },
}


class ThomasKilmannFramework(TheoryFramework):
    """Thomas-Kilmann Conflict Mode Instrument (TKI).

    Maps five conflict-handling modes along assertiveness (concern for self)
    and cooperativeness (concern for other): competing, collaborating,
    compromising, avoiding, and accommodating.
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Thomas-Kilmann Conflict Mode Instrument"
        self.author = "Kenneth Thomas & Ralph Kilmann"
        self.key_concepts = [
            "competing",
            "collaborating",
            "compromising",
            "avoiding",
            "accommodating",
            "assertiveness",
            "cooperativeness",
        ]

    def describe(self) -> str:
        return (
            "The Thomas-Kilmann model identifies five conflict-handling modes "
            "based on two dimensions: assertiveness (concern for one's own "
            "interests) and cooperativeness (concern for the other's interests). "
            "No single mode is best for all situations — effective conflict "
            "management requires choosing the appropriate mode for each context."
        )

    def recommend_mode(self, context: dict) -> str:
        """Recommend the most appropriate conflict-handling mode.

        Args:
            context: Dict with optional keys:
                'issue_importance' (float 0-1): How important the issue is to the party.
                'relationship_importance' (float 0-1): How important the relationship is.
                'time_pressure' (bool): Whether quick resolution is needed.
                'power_balance' (str: 'equal'|'stronger'|'weaker').
                'keywords' (list[str]).

        Returns:
            Mode name: 'competing', 'collaborating', 'compromising', 'avoiding', 'accommodating'.
        """
        issue_imp = context.get("issue_importance", 0.5)
        rel_imp = context.get("relationship_importance", 0.5)
        time_pressure = context.get("time_pressure", False)
        power = context.get("power_balance", "equal")

        # High issue + high relationship = collaborating
        if issue_imp > 0.7 and rel_imp > 0.7 and not time_pressure:
            return "collaborating"

        # High issue + low relationship = competing
        if issue_imp > 0.7 and rel_imp < 0.3:
            return "competing"

        # Low issue + high relationship = accommodating
        if issue_imp < 0.3 and rel_imp > 0.7:
            return "accommodating"

        # Low issue + low relationship = avoiding
        if issue_imp < 0.3 and rel_imp < 0.3:
            return "avoiding"

        # Time pressure + equal power = compromising
        if time_pressure:
            return "compromising"

        # Power dynamics
        if power == "weaker" and issue_imp < 0.5:
            return "accommodating"
        if power == "stronger" and issue_imp > 0.6:
            return "competing"

        # Default to compromising for moderate situations
        return "compromising"

    def assess(self, graph_context: dict) -> dict:
        """Assess a conflict and recommend appropriate handling mode.

        Returns recommended mode, mode details, and situational analysis.
        """
        context = graph_context.get("indicators", graph_context)
        mode = self.recommend_mode(context)
        mode_data = MODES[mode]

        # Assess all modes' appropriateness
        all_modes = {}
        for mode_name, mdata in MODES.items():
            all_modes[mode_name] = {
                "assertiveness": mdata["assertiveness"],
                "cooperativeness": mdata["cooperativeness"],
                "is_recommended": mode_name == mode,
            }

        return {
            "recommended_mode": mode,
            "mode_description": mode_data["description"],
            "when_appropriate": mode_data["when_appropriate"],
            "assertiveness": mode_data["assertiveness"],
            "cooperativeness": mode_data["cooperativeness"],
            "all_modes": all_modes,
        }

    def score(self, graph_context: dict) -> float:
        """Score relevance — higher when interpersonal conflict data is present."""
        context = graph_context.get("indicators", graph_context)
        signals = 0
        total = 4

        if "issue_importance" in context:
            signals += 1
        if "relationship_importance" in context:
            signals += 1
        if "power_balance" in context:
            signals += 1
        if len(graph_context.get("parties", [])) >= 2:
            signals += 1

        return round(signals / total, 2)

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        return [
            DiagnosticQuestion(
                question="How important is the issue at stake to you (1-10)?",
                framework=self.name,
                purpose="Assess issue importance for mode selection",
                response_type="scale",
            ),
            DiagnosticQuestion(
                question="How important is maintaining the relationship with the other party (1-10)?",  # noqa: E501
                framework=self.name,
                purpose="Assess relationship importance for mode selection",
                response_type="scale",
            ),
            DiagnosticQuestion(
                question="Is there significant time pressure to resolve this conflict?",
                framework=self.name,
                purpose="Determine if compromising is appropriate",
                response_type="boolean",
            ),
        ]
