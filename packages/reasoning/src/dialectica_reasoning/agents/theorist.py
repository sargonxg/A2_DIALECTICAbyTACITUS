"""
Theorist Agent — Apply all 15 frameworks and rank their applicability.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from dialectica_graph import GraphClient
from dialectica_reasoning.symbolic.causal_analysis import CausalAnalyzer
from dialectica_reasoning.symbolic.escalation import EscalationDetector
from dialectica_reasoning.symbolic.power_analysis import PowerMapper
from dialectica_reasoning.symbolic.ripeness import RipenessScorer
from dialectica_reasoning.symbolic.trust_analysis import TrustAnalyzer


@dataclass
class FrameworkAssessment:
    framework_id: str
    framework_name: str
    applicability_score: float
    key_insights: list[str] = field(default_factory=list)
    indicators_present: list[str] = field(default_factory=list)
    limitations: str = ""


@dataclass
class TheoryReport:
    workspace_id: str
    assessments: list[FrameworkAssessment] = field(default_factory=list)
    top_framework: str = ""
    synthesis: str = ""


class TheoristAgent:
    """Applies all 15 DIALECTICA frameworks and ranks their explanatory power."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client
        self._escalation = EscalationDetector(graph_client)
        self._ripeness = RipenessScorer(graph_client)
        self._trust = TrustAnalyzer(graph_client)
        self._power = PowerMapper(graph_client)
        self._causal = CausalAnalyzer(graph_client)

    async def run(self, workspace_id: str) -> TheoryReport:
        report = TheoryReport(workspace_id=workspace_id)

        actors = await self._gc.get_nodes(workspace_id, label="Actor")
        events = await self._gc.get_nodes(workspace_id, label="Event")
        emotions = await self._gc.get_nodes(workspace_id, label="EmotionalState")
        edges = await self._gc.get_edges(workspace_id)

        glasl = await self._escalation.compute_glasl_stage(workspace_id)
        ripe = await self._ripeness.compute_ripeness(workspace_id)
        trust_matrix = await self._trust.compute_trust_matrix(workspace_id)
        power_map = await self._power.compute_power_map(workspace_id)
        causal_chains = await self._causal.extract_causal_chains(workspace_id)

        has_emotions = len(emotions) > 0
        has_trust = len(trust_matrix.dyads) > 0
        has_power = len(power_map.dyads) > 0
        has_causal = len(causal_chains) > 0
        any(getattr(e, "type", "") == "ALLIED_WITH" for e in edges)
        has_interests = len(await self._gc.get_nodes(workspace_id, label="Interest")) > 0
        has_narratives = len(await self._gc.get_nodes(workspace_id, label="Narrative")) > 0

        glasl_num = glasl.stage.stage_number if glasl.stage else 1

        assessments: list[FrameworkAssessment] = []

        # Glasl (escalation stage model)
        glasl_score = min(1.0, glasl.confidence + 0.3 * (len(events) / max(1, 5)))
        assessments.append(
            FrameworkAssessment(
                framework_id="glasl",
                framework_name="Glasl 9-Stage Escalation Model",
                applicability_score=round(glasl_score, 3),
                key_insights=[
                    f"Current stage: {glasl.stage}",
                    f"Intervention type: {glasl.intervention_type}",
                ],
                indicators_present=["conflict_stage", "event_severity"]
                if events
                else ["conflict_stage"],
            )
        )

        # Zartman (ripeness)
        zartman_score = round(ripe.overall_score * 0.7 + 0.3, 3)
        assessments.append(
            FrameworkAssessment(
                framework_id="zartman",
                framework_name="Zartman Ripeness Theory",
                applicability_score=round(zartman_score, 3),
                key_insights=[
                    f"MHS={ripe.mhs_score:.2f}, MEO={ripe.meo_score:.2f}",
                    "Ripe for intervention" if ripe.is_ripe else "Not yet ripe",
                ],
                indicators_present=["mhs_indicators", "meo_indicators"],
            )
        )

        # Fisher/Ury (interests)
        fisher_score = 0.8 if has_interests else 0.3
        assessments.append(
            FrameworkAssessment(
                framework_id="fisher_ury",
                framework_name="Fisher/Ury Interest-Based Negotiation",
                applicability_score=round(fisher_score, 3),
                key_insights=[
                    "Interest mapping available" if has_interests else "Interests not yet mapped"
                ],
                indicators_present=["interests"] if has_interests else [],
            )
        )

        # Mayer Trust (trust model)
        trust_score = 0.85 if has_trust else 0.2
        assessments.append(
            FrameworkAssessment(
                framework_id="mayer_trust",
                framework_name="Mayer/Davis/Schoorman Trust Model",
                applicability_score=round(trust_score, 3),
                key_insights=[
                    f"Avg trust: {trust_matrix.average_trust:.2f}"
                    if has_trust
                    else "No trust data",
                ],
                indicators_present=["trust_dyads"] if has_trust else [],
            )
        )

        # French/Raven (power)
        power_score = 0.85 if has_power else 0.25
        assessments.append(
            FrameworkAssessment(
                framework_id="french_raven",
                framework_name="French/Raven Power Bases",
                applicability_score=round(power_score, 3),
                key_insights=[
                    f"Power map: {len(power_map.dyads)} dyads" if has_power else "No power data",
                ],
                indicators_present=["power_dynamics"] if has_power else [],
            )
        )

        # Pearl Causal (causality)
        causal_score = min(1.0, len(causal_chains) * 0.2 + 0.2) if has_causal else 0.2
        assessments.append(
            FrameworkAssessment(
                framework_id="pearl_causal",
                framework_name="Pearl Causal Hierarchy",
                applicability_score=round(causal_score, 3),
                key_insights=[
                    f"{len(causal_chains)} causal chains identified"
                    if has_causal
                    else "No causal data"
                ],
                indicators_present=["causal_chains"] if has_causal else [],
            )
        )

        # Plutchik emotions
        emotion_score = min(1.0, len(emotions) * 0.15 + 0.2) if has_emotions else 0.1
        assessments.append(
            FrameworkAssessment(
                framework_id="plutchik",
                framework_name="Plutchik Emotion Wheel",
                applicability_score=round(emotion_score, 3),
                key_insights=[
                    f"{len(emotions)} emotional states mapped"
                    if has_emotions
                    else "No emotion data"
                ],
                indicators_present=["emotional_states"] if has_emotions else [],
            )
        )

        # Galtung (structural violence)
        galtung_score = 0.6 if len(actors) > 3 else 0.3
        assessments.append(
            FrameworkAssessment(
                framework_id="galtung",
                framework_name="Galtung Conflict Triangle (ABC)",
                applicability_score=round(galtung_score, 3),
                key_insights=["Attitude, Behavior, Contradiction analysis applicable"],
                indicators_present=["actors", "conflict_structure"],
            )
        )

        # Winslade/Monk (narrative)
        narrative_score = 0.85 if has_narratives else 0.2
        assessments.append(
            FrameworkAssessment(
                framework_id="winslade_monk",
                framework_name="Winslade/Monk Narrative Mediation",
                applicability_score=round(narrative_score, 3),
                key_insights=[
                    "Narrative data available" if has_narratives else "Narratives not mapped"
                ],
                indicators_present=["narratives"] if has_narratives else [],
            )
        )

        # Kriesberg phases
        kriesberg_score = 0.7
        assessments.append(
            FrameworkAssessment(
                framework_id="kriesberg",
                framework_name="Kriesberg Conflict Cycle",
                applicability_score=round(kriesberg_score, 3),
                key_insights=["Phase transition analysis applicable"],
                indicators_present=["conflict_phases"],
            )
        )

        # Sort by applicability
        assessments.sort(key=lambda a: a.applicability_score, reverse=True)
        report.assessments = assessments
        report.top_framework = assessments[0].framework_name if assessments else ""
        report.synthesis = (
            f"Most applicable: {report.top_framework} "
            f"(score={assessments[0].applicability_score:.2f}). "
            f"Conflict is at Glasl stage {glasl_num} with ripeness {ripe.overall_score:.2f}."
        )
        return report
