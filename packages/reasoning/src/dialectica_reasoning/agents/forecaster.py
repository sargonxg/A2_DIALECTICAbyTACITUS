"""
Forecaster Agent — Escalation prediction and scenario generation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from dialectica_graph import GraphClient
from dialectica_reasoning.symbolic.escalation import EscalationDetector, Forecast
from dialectica_reasoning.symbolic.pattern_matching import PatternMatcher, PatternMatch


@dataclass
class Scenario:
    name: str
    probability: float
    description: str
    trigger_conditions: list[str] = field(default_factory=list)
    intervention_window: str = ""


@dataclass
class ForecastReport:
    workspace_id: str
    trajectory: Forecast | None = None
    scenarios: list[Scenario] = field(default_factory=list)
    patterns: list[PatternMatch] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)


class ForecasterAgent:
    """Produces escalation forecasts and multi-scenario analysis."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._escalation = EscalationDetector(graph_client)
        self._patterns = PatternMatcher(graph_client)

    async def run(self, workspace_id: str) -> ForecastReport:
        report = ForecastReport(workspace_id=workspace_id)

        report.trajectory = await self._escalation.forecast_trajectory(workspace_id)
        report.patterns = await self._patterns.detect_all(workspace_id)

        # Generate scenarios based on trajectory direction
        direction = report.trajectory.direction if report.trajectory else "stable"
        if direction == "escalating":
            report.scenarios = [
                Scenario(
                    name="Continued Escalation",
                    probability=0.55,
                    description="Conflict continues to escalate without intervention.",
                    trigger_conditions=["New violent incident", "Leadership hardliner gains power"],
                    intervention_window="Next 30-60 days critical",
                ),
                Scenario(
                    name="External Intervention",
                    probability=0.25,
                    description="Third-party actor intervenes to de-escalate.",
                    trigger_conditions=["International pressure mounts", "Economic costs become prohibitive"],
                    intervention_window="60-90 days",
                ),
                Scenario(
                    name="Negotiated Settlement",
                    probability=0.20,
                    description="Parties reach informal ceasefire or negotiated pause.",
                    trigger_conditions=["Back-channel contact established", "Mutual exhaustion"],
                    intervention_window="90-180 days",
                ),
            ]
        elif direction == "de_escalating":
            report.scenarios = [
                Scenario(
                    name="Negotiated Settlement",
                    probability=0.45,
                    description="Parties reach formal agreement.",
                    trigger_conditions=["Process momentum maintained", "Spoilers contained"],
                    intervention_window="Immediate — seize the moment",
                ),
                Scenario(
                    name="Frozen Conflict",
                    probability=0.35,
                    description="De-escalation stalls into prolonged stalemate.",
                    trigger_conditions=["Process fatigue", "Unresolved core issues"],
                    intervention_window="Engage within 30 days",
                ),
                Scenario(
                    name="Re-escalation",
                    probability=0.20,
                    description="Spoilers or external actors reignite conflict.",
                    trigger_conditions=["Process breakdown", "Unaddressed grievances"],
                    intervention_window="Monitor closely",
                ),
            ]
        else:  # stable
            report.scenarios = [
                Scenario(
                    name="Status Quo Maintenance",
                    probability=0.50,
                    description="Conflict remains stable but unresolved.",
                    trigger_conditions=["No major changes in power balance"],
                    intervention_window="Medium-term engagement recommended",
                ),
                Scenario(
                    name="Gradual Escalation",
                    probability=0.30,
                    description="Slow escalation driven by accumulated grievances.",
                    trigger_conditions=["Economic deterioration", "Spoiler activity"],
                    intervention_window="Preventive action within 90 days",
                ),
                Scenario(
                    name="Unexpected Breakthrough",
                    probability=0.20,
                    description="Leadership change or external pressure creates opening.",
                    trigger_conditions=["Election outcome", "Economic shock", "Regional shift"],
                    intervention_window="Be ready to capitalise on opportunities",
                ),
            ]
        return report
