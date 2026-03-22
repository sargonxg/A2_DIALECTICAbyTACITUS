"""
Pearl Causal Theory Framework — DIALECTICA implementation.

Judea Pearl's causal inference hierarchy (Ladder of Causation):
Level 1 — Association (seeing/observing)
Level 2 — Intervention (doing/acting)
Level 3 — Counterfactual (imagining/reasoning)
"""

from __future__ import annotations

from dialectica_ontology.theory.base import (
    DiagnosticQuestion,
    TheoryFramework,
)

CAUSAL_LEVELS: dict[int, dict[str, str]] = {
    1: {
        "name": "Association",
        "operator": "P(Y|X)",
        "activity": "Seeing / Observing",
        "question": "What if I observe X?",
        "description": (
            "Observational reasoning based on correlations and statistical "
            "associations. Cannot distinguish causation from correlation."
        ),
        "conflict_application": (
            "Identifying patterns and correlations in conflict data. "
            "Recognising that co-occurrence does not imply causation."
        ),
        "indicators": "correlation,pattern,observation,association,co_occurrence,data",
    },
    2: {
        "name": "Intervention",
        "operator": "P(Y|do(X))",
        "activity": "Doing / Acting",
        "question": "What if I do X?",
        "description": (
            "Interventional reasoning about the effects of deliberate actions. "
            "Requires understanding causal mechanisms, not just correlations."
        ),
        "conflict_application": (
            "Predicting the effects of specific interventions on conflict dynamics. "
            "What happens if we impose sanctions, offer mediation, etc.?"
        ),
        "indicators": "intervention,action,do,effect,experiment,cause,mechanism",
    },
    3: {
        "name": "Counterfactual",
        "operator": "P(Y_X|X',Y')",
        "activity": "Imagining / Reasoning",
        "question": "What if X had been different?",
        "description": (
            "Counterfactual reasoning about what would have happened under "
            "different circumstances. Requires a full causal model."
        ),
        "conflict_application": (
            "Reasoning about alternative histories and missed opportunities. "
            "What would have happened if the intervention had occurred earlier?"
        ),
        "indicators": "counterfactual,what_if,alternative,would_have,imagine,retrospective",
    },
}


class PearlCausalFramework(TheoryFramework):
    """Judea Pearl's causal inference hierarchy.

    Classifies reasoning about conflict causes and interventions into
    three levels: association (observing patterns), intervention
    (predicting effects of actions), and counterfactual (imagining
    alternative outcomes).
    """

    def __init__(self) -> None:
        super().__init__()
        self.name = "Pearl Causal Hierarchy"
        self.author = "Judea Pearl"
        self.key_concepts = [
            "association",
            "intervention",
            "counterfactual",
            "causal_model",
            "do_calculus",
            "confounding",
            "ladder_of_causation",
        ]

    def describe(self) -> str:
        return (
            "Pearl's Ladder of Causation defines three levels of causal "
            "reasoning: (1) Association — observing correlations, (2) "
            "Intervention — predicting effects of actions via do(X), and (3) "
            "Counterfactual — imagining what would have happened differently. "
            "Higher levels require deeper causal understanding and enable "
            "more sophisticated conflict analysis."
        )

    def classify_reasoning_level(self, query: str) -> str:
        """Classify a reasoning query into one of the three causal levels.

        Args:
            query: A question or statement about conflict causes/effects.

        Returns:
            One of 'association', 'intervention', 'counterfactual'.
        """
        q = query.lower()

        # Counterfactual indicators (check first — most specific)
        counterfactual_kw = [
            "would have",
            "could have",
            "should have",
            "had been",
            "what if",
            "if only",
            "alternatively",
            "imagine",
            "hypothetical",
            "counterfactual",
            "different outcome",
        ]
        if any(kw in q for kw in counterfactual_kw):
            return "counterfactual"

        # Intervention indicators
        intervention_kw = [
            "what happens if we",
            "if we do",
            "effect of",
            "impact of",
            "intervene",
            "impose",
            "introduce",
            "change",
            "action",
            "implement",
            "cause",
            "result of doing",
        ]
        if any(kw in q for kw in intervention_kw):
            return "intervention"

        # Default to association
        return "association"

    def assess(self, graph_context: dict) -> dict:
        """Assess the causal reasoning level in a conflict analysis.

        Args:
            graph_context: Dict with optional keys:
                'queries' (list[str]): Questions being asked about the conflict.
                'reasoning_type' (str): Explicit reasoning type.
                'causal_claims' (list[str]): Causal claims being made.

        Returns:
            Dict with reasoning level analysis and recommendations.
        """
        context = graph_context.get("indicators", graph_context)
        queries = context.get("queries", [])
        causal_claims = context.get("causal_claims", [])

        # Classify each query
        query_levels = {}
        for q in queries:
            level = self.classify_reasoning_level(q)
            query_levels[q] = level

        # Classify causal claims
        claim_levels = {}
        for c in causal_claims:
            level = self.classify_reasoning_level(c)
            claim_levels[c] = level

        # Determine dominant level
        all_levels = list(query_levels.values()) + list(claim_levels.values())
        if not all_levels:
            dominant = context.get("reasoning_type", "association")
        else:
            level_counts = {lvl: all_levels.count(lvl) for lvl in set(all_levels)}
            dominant = max(level_counts, key=level_counts.get)  # type: ignore[arg-type]

        level_num = {"association": 1, "intervention": 2, "counterfactual": 3}[dominant]
        level_data = CAUSAL_LEVELS[level_num]

        recommendations = []
        if dominant == "association":
            recommendations.append(
                "Currently at association level. To deepen analysis, ask "
                "interventional questions: 'What would happen if we did X?'"
            )
        elif dominant == "intervention":
            recommendations.append(
                "Good interventional reasoning. To deepen further, consider "
                "counterfactuals: 'What would have happened if X had been different?'"
            )
        else:
            recommendations.append(
                "Sophisticated counterfactual reasoning present. Ensure causal "
                "models are well-specified to support these inferences."
            )

        return {
            "dominant_level": dominant,
            "level_number": level_num,
            "level_name": level_data["name"],
            "level_description": level_data["description"],
            "conflict_application": level_data["conflict_application"],
            "query_classifications": query_levels,
            "claim_classifications": claim_levels,
            "recommendations": recommendations,
        }

    def score(self, graph_context: dict) -> float:
        """Score relevance — higher when causal reasoning data is present."""
        context = graph_context.get("indicators", graph_context)
        signals = 0
        total = 3

        if context.get("queries"):
            signals += 1
        if context.get("causal_claims"):
            signals += 1
        if context.get("reasoning_type"):
            signals += 1

        return round(signals / total, 2)

    def get_diagnostic_questions(self) -> list[DiagnosticQuestion]:
        return [
            DiagnosticQuestion(
                question="What causal claims are being made about this conflict (X causes Y)?",
                framework=self.name,
                purpose="Identify causal reasoning level",
                response_type="open",
            ),
            DiagnosticQuestion(
                question="What would have happened if the conflict had been handled differently at an earlier stage?",  # noqa: E501
                framework=self.name,
                purpose="Encourage counterfactual reasoning",
                response_type="open",
            ),
        ]
