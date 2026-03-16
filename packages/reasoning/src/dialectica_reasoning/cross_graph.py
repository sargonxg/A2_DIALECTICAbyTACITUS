"""
Cross-Graph Querier — Query across Case, Theory, and Precedent graph layers.

Matches workspace conflict patterns against the theory knowledge graph,
finds structurally similar conflicts, and recommends analytical procedures.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from dialectica_graph import GraphClient
from dialectica_ontology.theory_graph import (
    TheoryMatch,
    TheoryGuidance,
    RecommendedProcedure,
    THEORY_WORKSPACE_ID,
)
from dialectica_reasoning.symbolic.escalation import EscalationDetector
from dialectica_reasoning.symbolic.ripeness import RipenessScorer
from dialectica_reasoning.symbolic.pattern_matching import PatternMatcher


@dataclass
class SimilarConflict:
    workspace_id: str
    similarity_score: float
    shared_patterns: list[str] = field(default_factory=list)
    key_differences: list[str] = field(default_factory=list)
    lessons: str = ""


class CrossGraphQuerier:
    """Query across multiple graph layers: Case, Theory, Precedent."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client
        self._escalation = EscalationDetector(graph_client)
        self._ripeness = RipenessScorer(graph_client)
        self._patterns = PatternMatcher(graph_client)

    async def find_applicable_theories(self, workspace_id: str) -> list[TheoryMatch]:
        """Match workspace patterns against theory graph ConflictPatterns."""
        patterns = await self._patterns.detect_all(workspace_id)
        glasl = await self._escalation.compute_glasl_stage(workspace_id)
        ripe = await self._ripeness.compute_ripeness(workspace_id)

        matches: list[TheoryMatch] = []

        for pattern in patterns:
            if pattern.confidence < 0.3:
                continue

            # Map detected patterns to theory concepts
            concept_map = {
                "escalation_spiral": ["glasl_hardening", "tit_for_tat", "conflict_cycle"],
                "security_dilemma": ["security_dilemma", "arms_race", "misperception"],
                "spoiler_dynamics": ["spoiler_theory", "conflict_economy", "veto_player"],
                "hurting_stalemate": ["mutually_hurting_stalemate", "ripeness", "cost_accumulation"],
                "alliance_cascade": ["alliance_formation", "coalition_dynamics", "polarisation"],
            }
            procedures_map = {
                "escalation_spiral": ["circuit_breaker", "confidence_building"],
                "security_dilemma": ["transparency_measures", "mutual_verification"],
                "spoiler_dynamics": ["spoiler_management", "inclusion_strategy"],
                "hurting_stalemate": ["ripeness_assessment", "meo_creation"],
                "alliance_cascade": ["coalition_mapping", "cross_cutting_engagement"],
            }

            matches.append(TheoryMatch(
                pattern_id=pattern.pattern_name,
                pattern_name=pattern.pattern_name.replace("_", " ").title(),
                confidence=pattern.confidence,
                applicable_concepts=concept_map.get(pattern.pattern_name, []),
                recommended_procedures=procedures_map.get(pattern.pattern_name, []),
            ))

        # Add ripeness-based match
        if ripe.overall_score > 0.3:
            matches.append(TheoryMatch(
                pattern_id="zartman_ripeness",
                pattern_name="Zartman Ripeness Theory",
                confidence=ripe.overall_score,
                applicable_concepts=["mutually_hurting_stalemate", "mutually_enticing_opportunity"],
                recommended_procedures=["ripeness_assessment", "formal_mediation"],
            ))

        return sorted(matches, key=lambda m: m.confidence, reverse=True)

    async def find_similar_conflicts(self, workspace_id: str) -> list[SimilarConflict]:
        """Compare structural signature against other workspaces."""
        # In production: query all workspaces and compare signatures
        # For now: return empty list (requires multi-workspace support)
        return []

    async def get_theory_guidance(
        self, framework_id: str, workspace_id: str
    ) -> TheoryGuidance:
        """Query theory graph for framework-specific guidance."""
        glasl = await self._escalation.compute_glasl_stage(workspace_id)
        ripe = await self._ripeness.compute_ripeness(workspace_id)
        patterns = await self._patterns.detect_all(workspace_id)

        stage_num = glasl.stage.stage_number if glasl.stage else 1

        # Framework-specific synthesis
        synthesis_map = {
            "glasl": (
                f"Glasl stage {stage_num}: {glasl.stage}. "
                f"Intervention type: {glasl.intervention_type}. "
                f"Focus on stage-appropriate de-escalation measures."
            ),
            "zartman": (
                f"Ripeness: MHS={ripe.mhs_score:.2f}, MEO={ripe.meo_score:.2f}. "
                f"{'Conflict is ripe — initiate formal mediation.' if ripe.is_ripe else 'Conflict not yet ripe — build enabling conditions.'}"
            ),
            "fisher_ury": (
                "Apply interest-based negotiation: separate positions from interests, "
                "focus on underlying needs, generate options for mutual gain, use BATNA as leverage."
            ),
            "mayer_trust": (
                "Trust-based intervention: assess ability, benevolence, and integrity perceptions. "
                "Build trust incrementally through low-risk cooperative actions."
            ),
            "french_raven": (
                "Power analysis: leverage expert and legitimate power for process design. "
                "Reduce coercive power asymmetries through external balancing."
            ),
        }

        synthesis = synthesis_map.get(
            framework_id,
            f"Apply {framework_id} framework to the conflict at stage {stage_num}."
        )

        return TheoryGuidance(
            framework_id=framework_id,
            framework_name=framework_id.replace("_", " ").title(),
            workspace_id=workspace_id,
            synthesis=synthesis,
        )

    async def get_analytical_procedures(
        self, workspace_id: str
    ) -> list[RecommendedProcedure]:
        """What analytical steps should be taken next?"""
        from dialectica_ontology.theory_graph import AnalyticalProcedure, ProcedureStep

        glasl = await self._escalation.compute_glasl_stage(workspace_id)
        ripe = await self._ripeness.compute_ripeness(workspace_id)
        stage_num = glasl.stage.stage_number if glasl.stage else 1

        procedures: list[RecommendedProcedure] = []

        # Always recommend stakeholder mapping
        procedures.append(RecommendedProcedure(
            procedure=AnalyticalProcedure(
                id="stakeholder_mapping",
                name="Stakeholder Mapping",
                source="UN DPPA Assessment Framework",
                description="Identify and map all conflict parties, positions, interests, and influence.",
                steps=[
                    ProcedureStep(1, "Identify primary parties", "List all direct conflict parties"),
                    ProcedureStep(2, "Map secondary actors", "Identify spoilers, enablers, third parties"),
                    ProcedureStep(3, "Assess positions vs interests", "Apply Fisher/Ury framework"),
                    ProcedureStep(4, "Evaluate BATNA", "Assess each party's walk-away alternative"),
                ],
                required_data=["Actor", "Interest", "Issue"],
                output_type="stakeholder_map",
            ),
            rationale="Stakeholder mapping is foundational for all subsequent analysis.",
            priority=1,
            estimated_value=0.9,
        ))

        # Escalation assessment if stage >= 4
        if stage_num >= 4:
            procedures.append(RecommendedProcedure(
                procedure=AnalyticalProcedure(
                    id="escalation_assessment",
                    name="Glasl Escalation Assessment",
                    source="Glasl 9-Stage Model",
                    description="Assess current escalation stage and trajectory.",
                    steps=[
                        ProcedureStep(1, "Map events to stages", "Classify recent events by escalation indicators"),
                        ProcedureStep(2, "Assess signals", "Detect escalation/de-escalation signals"),
                        ProcedureStep(3, "Forecast trajectory", "Project 3-month escalation trajectory"),
                    ],
                    required_data=["Event", "Conflict", "EmotionalState"],
                    output_type="escalation_report",
                ),
                rationale=f"Stage {stage_num} requires active escalation monitoring.",
                priority=1,
                estimated_value=0.85,
            ))

        # Ripeness assessment if conflict is active
        procedures.append(RecommendedProcedure(
            procedure=AnalyticalProcedure(
                id="ripeness_assessment",
                name="Zartman Ripeness Assessment",
                source="Zartman Ripeness Theory",
                description="Assess MHS and MEO conditions for intervention timing.",
                steps=[
                    ProcedureStep(1, "Assess MHS", "Measure stalemate pressure and cost accumulation"),
                    ProcedureStep(2, "Assess MEO", "Identify available resolution pathways"),
                    ProcedureStep(3, "Recommend timing", "Advise on intervention window"),
                ],
                required_data=["Conflict", "Process", "Event"],
                output_type="ripeness_report",
            ),
            rationale="Ripeness assessment optimises intervention timing." if not ripe.is_ripe else "Conflict is ripe — verify conditions before formal mediation.",
            priority=2,
            estimated_value=0.8,
        ))

        return procedures
