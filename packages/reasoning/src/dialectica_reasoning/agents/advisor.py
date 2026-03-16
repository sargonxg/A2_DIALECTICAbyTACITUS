"""
Advisor Agent — Actionable recommendations synthesis.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from dialectica_graph import GraphClient
from dialectica_reasoning.symbolic.escalation import EscalationDetector
from dialectica_reasoning.symbolic.ripeness import RipenessScorer
from dialectica_reasoning.symbolic.pattern_matching import PatternMatcher
from dialectica_reasoning.symbolic.constraint_engine import ConflictGrammarEngine


@dataclass
class Recommendation:
    priority: int  # 1=urgent, 2=high, 3=medium
    category: str  # "de_escalation" | "process" | "trust" | "power" | "structural"
    action: str
    rationale: str
    timeframe: str
    actors_involved: list[str] = field(default_factory=list)


@dataclass
class AdvisoryReport:
    workspace_id: str
    recommendations: list[Recommendation] = field(default_factory=list)
    overall_assessment: str = ""
    urgency_level: str = "medium"


class AdvisorAgent:
    """Synthesises actionable recommendations from all symbolic analyses."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client
        self._escalation = EscalationDetector(graph_client)
        self._ripeness = RipenessScorer(graph_client)
        self._patterns = PatternMatcher(graph_client)
        self._engine = ConflictGrammarEngine(graph_client)

    async def run(self, workspace_id: str) -> AdvisoryReport:
        report = AdvisoryReport(workspace_id=workspace_id)
        recommendations: list[Recommendation] = []

        glasl = await self._escalation.compute_glasl_stage(workspace_id)
        ripe = await self._ripeness.compute_ripeness(workspace_id)
        patterns = await self._patterns.detect_all(workspace_id)
        rule_report = await self._engine.evaluate_all_rules(workspace_id)

        stage_num = glasl.stage.stage_number if glasl.stage else 1

        # Escalation-based recommendations
        if stage_num >= 7:
            report.urgency_level = "critical"
            recommendations.append(Recommendation(
                priority=1,
                category="de_escalation",
                action="Implement immediate de-escalation measures",
                rationale=f"Glasl stage {stage_num} — lose-lose territory. Immediate intervention required.",
                timeframe="Immediate (0-7 days)",
            ))
        elif stage_num >= 5:
            report.urgency_level = "high"
            recommendations.append(Recommendation(
                priority=1,
                category="de_escalation",
                action="Introduce circuit-breaker through neutral third party",
                rationale=f"Glasl stage {stage_num} — conflict losing-face dynamics. Need external help.",
                timeframe="Urgent (7-30 days)",
            ))

        # Ripeness recommendations
        if ripe.is_ripe:
            recommendations.append(Recommendation(
                priority=1,
                category="process",
                action="Initiate formal mediation process now",
                rationale=f"Conflict is ripe: MHS={ripe.mhs_score:.2f}, MEO={ripe.meo_score:.2f}.",
                timeframe="Immediate — window may close",
            ))
        elif ripe.mhs_score > 0.5 and ripe.meo_score < 0.3:
            recommendations.append(Recommendation(
                priority=2,
                category="process",
                action="Create mutually enticing opportunity",
                rationale="Stalemate pressure high but no resolution path visible.",
                timeframe="30-60 days",
            ))

        # Pattern-based recommendations
        for pattern in patterns:
            if pattern.confidence > 0.5:
                recommendations.append(Recommendation(
                    priority=2,
                    category="structural",
                    action=pattern.intervention_recommendation,
                    rationale=f"Pattern detected: {pattern.pattern_name} (confidence={pattern.confidence:.2f})",
                    timeframe="Medium-term (30-90 days)",
                    actors_involved=pattern.evidence_ids[:3],
                ))

        # Rule violation recommendations
        critical_findings = [f for f in rule_report.findings if f.severity == "CRITICAL"]
        for finding in critical_findings[:3]:
            recommendations.append(Recommendation(
                priority=1,
                category="structural",
                action=finding.recommendation,
                rationale=finding.description,
                timeframe="Urgent (7-30 days)",
            ))

        # Sort by priority
        recommendations.sort(key=lambda r: r.priority)
        report.recommendations = recommendations

        report.overall_assessment = (
            f"Urgency: {report.urgency_level.upper()}. "
            f"Glasl stage {stage_num}, ripeness {ripe.overall_score:.2f}. "
            f"{len(critical_findings)} critical issues, {len(patterns)} patterns detected. "
            f"{len(recommendations)} recommendations generated."
        )
        return report
