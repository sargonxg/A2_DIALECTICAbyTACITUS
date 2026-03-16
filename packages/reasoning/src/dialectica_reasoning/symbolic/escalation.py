"""
Escalation Detection — Glasl-stage assessment, signal detection, and trajectory forecasting.

Maps workspace graph data (emotional states, event frequency, violence types,
coalition formation) to Glasl's 9-stage escalation model and produces
forward-looking trajectory forecasts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import mean

from dialectica_graph import GraphClient
from dialectica_ontology.enums import (
    GlaslStage,
    PrimaryEmotion,
    ViolenceType,
)
from dialectica_ontology.primitives import (
    Conflict,
    EmotionalState,
    Event,
)
from dialectica_ontology.relationships import EdgeType


# ---------------------------------------------------------------------------
# Result data classes
# ---------------------------------------------------------------------------

@dataclass
class GlaslAssessment:
    """Result of a Glasl stage computation for a workspace."""

    stage: GlaslStage = GlaslStage.HARDENING
    level: str = "win_win"
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)
    intervention_type: str = "moderation"


@dataclass
class Signal:
    """A single escalation (or de-escalation) signal detected in the graph."""

    signal_type: str = ""
    description: str = ""
    severity: float = 0.0
    timestamp: datetime | None = None
    evidence_ids: list[str] = field(default_factory=list)


@dataclass
class TrajectoryPoint:
    """A predicted future point on the escalation trajectory."""

    timestamp: datetime = field(default_factory=datetime.utcnow)
    predicted_stage: int = 1
    confidence: float = 0.0


@dataclass
class Forecast:
    """Forward-looking escalation trajectory."""

    trajectory: list[TrajectoryPoint] = field(default_factory=list)
    direction: str = "stable"  # "escalating" | "de_escalating" | "stable"
    confidence: float = 0.0


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TOXIC_EMOTIONS: set[str] = {
    PrimaryEmotion.ANGER,
    PrimaryEmotion.DISGUST,
    PrimaryEmotion.FEAR,
}

_CONFLICT_EVENT_TYPES: set[str] = {
    "threaten", "protest", "exhibit_force_posture",
    "reduce_relations", "coerce", "assault",
}

_GLASL_ORDERED: list[GlaslStage] = list(GlaslStage)


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------

class EscalationDetector:
    """Computes Glasl stage, detects escalation signals, and forecasts trajectory."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client

    # -- Glasl stage --------------------------------------------------------

    async def compute_glasl_stage(self, workspace_id: str) -> GlaslAssessment:
        """Derive the current Glasl stage from workspace graph signals."""
        conflicts = await self._gc.get_nodes(workspace_id, label="Conflict")
        events = await self._gc.get_nodes(workspace_id, label="Event")
        emotions = await self._gc.get_nodes(workspace_id, label="EmotionalState")
        edges = await self._gc.get_edges(workspace_id)

        evidence_ids: list[str] = []
        scores: list[float] = []

        # 1. Explicit conflict glasl_stage (highest authority)
        conflict_stages: list[int] = []
        for node in conflicts:
            c: Conflict = node  # type: ignore[assignment]
            stage = getattr(c, "glasl_stage", None)
            if stage is not None:
                conflict_stages.append(int(stage))
                evidence_ids.append(c.id)
        if conflict_stages:
            scores.append(max(conflict_stages))

        # 2. Narrative toxicity: anger/disgust/fear emotional states
        toxic_count = 0
        total_emotions = 0
        for node in emotions:
            es: EmotionalState = node  # type: ignore[assignment]
            total_emotions += 1
            pe = getattr(es, "primary_emotion", None)
            if pe in _TOXIC_EMOTIONS:
                toxic_count += 1
                evidence_ids.append(es.id)
        if total_emotions > 0:
            toxicity_ratio = toxic_count / total_emotions
            # toxicity_ratio 0-1 maps to stages 1-9
            scores.append(1.0 + toxicity_ratio * 8.0)

        # 3. Event severity and conflict-type events
        severities: list[float] = []
        conflict_event_count = 0
        for node in events:
            ev: Event = node  # type: ignore[assignment]
            severities.append(getattr(ev, "severity", 0.0))
            et = getattr(ev, "event_type", "")
            if et in _CONFLICT_EVENT_TYPES:
                conflict_event_count += 1
                evidence_ids.append(ev.id)
        if severities:
            avg_severity = mean(severities)
            scores.append(1.0 + avg_severity * 8.0)

        # 4. Violence type
        for node in conflicts:
            c = node  # type: ignore[assignment]
            vt = getattr(c, "violence_type", None)
            if vt == ViolenceType.DIRECT:
                scores.append(7.0)
                evidence_ids.append(c.id)
            elif vt == ViolenceType.STRUCTURAL:
                scores.append(4.0)
            elif vt == ViolenceType.CULTURAL:
                scores.append(3.0)

        # 5. Coalition formation (ALLIED_WITH edges indicate stage >= 4)
        allied_edges = [e for e in edges if e.type == EdgeType.ALLIED_WITH]
        if len(allied_edges) >= 2:
            scores.append(4.0)

        # Aggregate
        if not scores:
            return GlaslAssessment()

        avg_stage = mean(scores)
        stage_idx = max(0, min(8, round(avg_stage) - 1))
        glasl = _GLASL_ORDERED[stage_idx]
        confidence = min(1.0, len(scores) * 0.15)

        return GlaslAssessment(
            stage=glasl,
            level=glasl.level,
            confidence=round(confidence, 3),
            evidence=list(dict.fromkeys(evidence_ids)),  # dedupe preserving order
            intervention_type=glasl.intervention_type,
        )

    # -- Signal detection ---------------------------------------------------

    async def detect_escalation_signals(
        self, workspace_id: str, window_days: int = 30
    ) -> list[Signal]:
        """Detect escalation / de-escalation signals within a time window."""
        signals: list[Signal] = []
        cutoff = datetime.utcnow() - timedelta(days=window_days)

        events = await self._gc.get_nodes(workspace_id, label="Event")
        emotions = await self._gc.get_nodes(workspace_id, label="EmotionalState")
        edges = await self._gc.get_edges(workspace_id)

        # Recent events with high severity
        recent_events: list[Event] = []
        for node in events:
            ev: Event = node  # type: ignore[assignment]
            occ = getattr(ev, "occurred_at", None)
            if occ is not None and occ >= cutoff:
                recent_events.append(ev)

        high_severity = [e for e in recent_events if getattr(e, "severity", 0) >= 0.7]
        if high_severity:
            signals.append(Signal(
                signal_type="high_severity_events",
                description=f"{len(high_severity)} high-severity events in the last {window_days} days.",
                severity=0.8,
                timestamp=max(getattr(e, "occurred_at", cutoff) for e in high_severity),
                evidence_ids=[e.id for e in high_severity],
            ))

        # Increasing event frequency (compare first half vs second half of window)
        mid = cutoff + timedelta(days=window_days // 2)
        first_half = [e for e in recent_events if getattr(e, "occurred_at", cutoff) < mid]
        second_half = [e for e in recent_events if getattr(e, "occurred_at", cutoff) >= mid]
        if len(first_half) > 0 and len(second_half) > len(first_half) * 1.5:
            signals.append(Signal(
                signal_type="accelerating_event_frequency",
                description=(
                    f"Event frequency accelerating: {len(first_half)} events in first half "
                    f"vs {len(second_half)} in second half of window."
                ),
                severity=0.6,
                timestamp=datetime.utcnow(),
                evidence_ids=[e.id for e in second_half[:5]],
            ))

        # Toxic emotional escalation
        recent_toxic = []
        for node in emotions:
            es: EmotionalState = node  # type: ignore[assignment]
            observed = getattr(es, "observed_at", None)
            if observed is not None and observed >= cutoff:
                pe = getattr(es, "primary_emotion", None)
                if pe in _TOXIC_EMOTIONS:
                    recent_toxic.append(es)
        if len(recent_toxic) >= 3:
            signals.append(Signal(
                signal_type="emotional_toxicity",
                description=f"{len(recent_toxic)} toxic emotional states recorded recently.",
                severity=0.7,
                timestamp=datetime.utcnow(),
                evidence_ids=[es.id for es in recent_toxic[:5]],
            ))

        # Coalition formation signals
        allied = [e for e in edges if e.type == EdgeType.ALLIED_WITH]
        opposed = [e for e in edges if e.type == EdgeType.OPPOSED_TO]
        if len(allied) >= 2 and len(opposed) >= 1:
            signals.append(Signal(
                signal_type="coalition_polarisation",
                description="Multiple alliances with opposition detected — coalition formation underway.",
                severity=0.6,
                timestamp=datetime.utcnow(),
                evidence_ids=[e.id for e in allied[:3]] + [e.id for e in opposed[:2]],
            ))

        return signals

    # -- Trajectory forecast ------------------------------------------------

    async def forecast_trajectory(self, workspace_id: str) -> Forecast:
        """Produce a simple linear trajectory forecast based on current signals."""
        assessment = await self.compute_glasl_stage(workspace_id)
        signals = await self.detect_escalation_signals(workspace_id)

        current_stage_num = assessment.stage.stage_number

        # Compute velocity from signals
        escalation_pressure = sum(s.severity for s in signals if s.signal_type != "de_escalation")
        n_signals = len(signals) if signals else 1

        # positive = escalating, range roughly -2..+2 stages per month
        velocity = (escalation_pressure / n_signals) - 0.3 if signals else 0.0

        if velocity > 0.1:
            direction = "escalating"
        elif velocity < -0.1:
            direction = "de_escalating"
        else:
            direction = "stable"

        # Project 3 months ahead
        now = datetime.utcnow()
        trajectory: list[TrajectoryPoint] = []
        for month_offset in range(1, 4):
            predicted = current_stage_num + velocity * month_offset
            clamped = max(1, min(9, round(predicted)))
            conf = max(0.1, assessment.confidence - 0.15 * month_offset)
            trajectory.append(TrajectoryPoint(
                timestamp=now + timedelta(days=30 * month_offset),
                predicted_stage=clamped,
                confidence=round(conf, 3),
            ))

        return Forecast(
            trajectory=trajectory,
            direction=direction,
            confidence=round(assessment.confidence * 0.8, 3),
        )
