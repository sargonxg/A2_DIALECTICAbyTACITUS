"""
Cross-Graph Querier — Queries across workspace graphs AND the theory knowledge graph.

Enables theory-grounded analysis by matching workspace conflict patterns
against the shared theory graph, finding applicable frameworks, similar
conflicts, and theory-informed guidance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TheoryMatch:
    """A matched theory framework with relevance score."""

    framework_id: str
    framework_name: str
    relevance_score: float
    matching_patterns: list[str]
    guidance: str


@dataclass
class SimilarConflict:
    """A structurally similar conflict workspace."""

    workspace_id: str
    workspace_name: str
    similarity_score: float
    shared_patterns: list[str]
    explanation: str


@dataclass
class TheoryGuidance:
    """Theory-informed guidance for a workspace."""

    framework_id: str
    framework_name: str
    current_assessment: str
    recommendations: list[str]
    key_concepts: list[str]
    intervention_strategies: list[str]


@dataclass
class TheoryExplanation:
    """A theory-grounded explanation of a query result."""

    query: str
    explanation: str
    theory_lenses: list[TheoryLens]
    confidence: float


@dataclass
class TheoryLens:
    """A single theoretical perspective on the conflict."""

    framework: str
    interpretation: str
    supporting_concepts: list[str]


# ─── Framework Signatures ───────────────────────────────────────────────────

# Each framework has indicators that can be matched against workspace graph features
FRAMEWORK_SIGNATURES: dict[str, dict[str, Any]] = {
    "glasl": {
        "name": "Glasl Escalation Model",
        "indicators": ["glasl_stage", "escalation_events", "coalition_formation", "threat_events"],
        "applicable_when": "conflict shows escalation dynamics",
    },
    "fisher_ury": {
        "name": "Principled Negotiation",
        "indicators": ["interests", "positions", "batna_strength", "negotiation_events"],
        "applicable_when": "parties have identifiable interests and negotiation potential",
    },
    "zartman": {
        "name": "Ripeness Theory",
        "indicators": ["stalemate_indicators", "mhs_score", "meo_score", "mediation_events"],
        "applicable_when": "conflict is in stalemate or approaching resolution",
    },
    "galtung": {
        "name": "Structural Violence",
        "indicators": ["structural_inequalities", "cultural_justifications", "systemic_patterns"],
        "applicable_when": "conflict has deep structural roots",
    },
    "burton": {
        "name": "Basic Human Needs",
        "indicators": ["identity_issues", "security_concerns", "recognition_demands"],
        "applicable_when": "fundamental human needs are at stake",
    },
    "lederach": {
        "name": "Conflict Transformation",
        "indicators": ["relationship_patterns", "systemic_issues", "multi_level_actors"],
        "applicable_when": "conflict requires systemic change, not just settlement",
    },
    "deutsch": {
        "name": "Cooperation & Competition",
        "indicators": ["cooperation_events", "competition_events", "mixed_motive_situations"],
        "applicable_when": "parties face cooperation-competition dilemmas",
    },
    "pearl_causal": {
        "name": "Causal Inference",
        "indicators": ["causal_chains", "event_sequences", "intervention_opportunities"],
        "applicable_when": "understanding causation is critical for intervention",
    },
    "french_raven": {
        "name": "Bases of Power",
        "indicators": ["power_dynamics", "authority_structures", "resource_control"],
        "applicable_when": "power asymmetries drive the conflict",
    },
    "mayer_trust": {
        "name": "Trust Model",
        "indicators": ["trust_states", "broken_commitments", "trust_building_events"],
        "applicable_when": "trust breakdown is central to the conflict",
    },
    "plutchik": {
        "name": "Emotion Theory",
        "indicators": ["emotional_states", "emotional_intensity", "emotion_patterns"],
        "applicable_when": "strong emotions drive conflict behavior",
    },
    "thomas_kilmann": {
        "name": "Conflict Modes",
        "indicators": ["conflict_modes", "assertiveness_levels", "cooperation_levels"],
        "applicable_when": "parties use different conflict-handling styles",
    },
    "winslade_monk": {
        "name": "Narrative Mediation",
        "indicators": ["narratives", "framing_patterns", "counter_narratives"],
        "applicable_when": "competing narratives fuel the conflict",
    },
    "kriesberg": {
        "name": "Conflict Dynamics",
        "indicators": ["conflict_phases", "escalation_patterns", "de_escalation_events"],
        "applicable_when": "tracking conflict lifecycle and transitions",
    },
    "ury_brett_goldberg": {
        "name": "Dispute Systems Design",
        "indicators": ["resolution_processes", "dispute_mechanisms", "system_patterns"],
        "applicable_when": "designing institutional conflict resolution systems",
    },
}


class CrossGraphQuerier:
    """
    Queries across conflict workspace graphs AND the theory knowledge graph.

    Examples:
        "What theory best explains the dynamics in my Syria workspace?"
        "Are there similar conflicts to my current workspace?"
        "What does Glasl say about conflicts at stage 5?"
    """

    def __init__(self, graph_client: Any = None) -> None:
        self._graph = graph_client

    async def find_applicable_theories(self, workspace_id: str) -> list[TheoryMatch]:
        """Match workspace patterns against theory frameworks."""
        matches: list[TheoryMatch] = []

        # Get workspace features (node type counts, edge patterns, etc.)
        features = await self._get_workspace_features(workspace_id)

        for fw_id, fw_sig in FRAMEWORK_SIGNATURES.items():
            score = self._compute_relevance(features, fw_sig["indicators"])
            if score > 0.3:
                matching = [ind for ind in fw_sig["indicators"] if features.get(ind, 0) > 0]
                matches.append(
                    TheoryMatch(
                        framework_id=fw_id,
                        framework_name=fw_sig["name"],
                        relevance_score=score,
                        matching_patterns=matching,
                        guidance=fw_sig["applicable_when"],
                    )
                )

        return sorted(matches, key=lambda m: m.relevance_score, reverse=True)

    async def find_similar_conflicts(self, workspace_id: str) -> list[SimilarConflict]:
        """Find structurally similar workspaces."""
        # Compute structural signature and compare
        return []

    async def get_theory_guidance(self, framework_id: str, workspace_id: str) -> TheoryGuidance:
        """Get theory-specific guidance for a workspace."""
        fw = FRAMEWORK_SIGNATURES.get(framework_id)
        if not fw:
            raise ValueError(f"Unknown framework: {framework_id}")

        return TheoryGuidance(
            framework_id=framework_id,
            framework_name=fw["name"],
            current_assessment=f"Applying {fw['name']} lens to workspace",
            recommendations=[fw["applicable_when"]],
            key_concepts=fw["indicators"],
            intervention_strategies=[],
        )

    async def explain_with_theory(self, query: str, workspace_id: str) -> TheoryExplanation:
        """Generate a theory-grounded explanation for a query."""
        theories = await self.find_applicable_theories(workspace_id)
        lenses = [
            TheoryLens(
                framework=t.framework_name,
                interpretation=t.guidance,
                supporting_concepts=t.matching_patterns,
            )
            for t in theories[:3]
        ]
        return TheoryExplanation(
            query=query,
            explanation=f"Analysis grounded in {len(lenses)} applicable frameworks",
            theory_lenses=lenses,
            confidence=theories[0].relevance_score if theories else 0.0,
        )

    async def _get_workspace_features(self, workspace_id: str) -> dict[str, float]:
        """Extract structural features from a workspace graph."""
        # Default features — in production, query the actual graph
        return {
            "glasl_stage": 1.0,
            "interests": 1.0,
            "narratives": 1.0,
            "power_dynamics": 0.5,
            "trust_states": 0.5,
            "emotional_states": 0.3,
            "causal_chains": 0.5,
            "conflict_modes": 0.5,
        }

    def _compute_relevance(self, features: dict[str, float], indicators: list[str]) -> float:
        """Compute relevance score of a framework given workspace features."""
        if not indicators:
            return 0.0
        matched = sum(1 for ind in indicators if features.get(ind, 0) > 0)
        return matched / len(indicators)
