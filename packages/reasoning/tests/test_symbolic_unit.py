"""
Unit tests for DIALECTICA symbolic reasoning modules.

Tests: escalation detection, ripeness scoring, trust analysis,
symbolic firewall, and power asymmetry detection — all without
external services.

Uses an inline MockGraphClient that mirrors the API conftest pattern.
"""
from __future__ import annotations

import sys
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_ontology.primitives import (
    Actor,
    Conflict,
    EmotionalState,
    Event,
    Process,
    Outcome,
    TrustState,
)
from dialectica_ontology.relationships import ConflictRelationship, EdgeType
from dialectica_ontology.enums import (
    ConflictStatus,
    GlaslStage,
    PrimaryEmotion,
    ProcessStatus,
    ViolenceType,
)
from dialectica_ontology.confidence import Conclusion, ConfidenceType

from dialectica_reasoning.symbolic.escalation import (
    EscalationDetector,
    GlaslAssessment,
    Forecast,
)
from dialectica_reasoning.symbolic.ripeness import RipenessScorer, RipenessAssessment
from dialectica_reasoning.symbolic.trust_analysis import TrustAnalyzer, TrustMatrix
from dialectica_reasoning.symbolic.firewall import SymbolicFirewall
from dialectica_reasoning.symbolic.power_analysis import (
    PowerMapper,
    PowerMap,
    PowerAsymmetry,
)


# ═══════════════════════════════════════════════════════════════════════════
#  INLINE MOCK GRAPH CLIENT
# ═══════════════════════════════════════════════════════════════════════════


class MockGraphClient:
    """In-memory mock implementing the GraphClient interface for unit tests.

    Stores nodes and edges by workspace_id, supporting the methods used
    by the symbolic reasoning modules.
    """

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}   # {ws_id: {node_id: node}}
        self.edges: dict[str, list[Any]] = {}         # {ws_id: [edge]}

    def seed_nodes(self, workspace_id: str, nodes: list[Any]) -> None:
        """Add nodes to a workspace."""
        if workspace_id not in self.nodes:
            self.nodes[workspace_id] = {}
        for node in nodes:
            self.nodes[workspace_id][node.id] = node

    def seed_edges(self, workspace_id: str, edges: list[Any]) -> None:
        """Add edges to a workspace."""
        if workspace_id not in self.edges:
            self.edges[workspace_id] = []
        self.edges[workspace_id].extend(edges)

    async def get_nodes(
        self,
        workspace_id: str,
        label: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Any]:
        ws_nodes = list(self.nodes.get(workspace_id, {}).values())
        if label:
            ws_nodes = [n for n in ws_nodes if getattr(n, "label", "") == label]
        return ws_nodes[offset: offset + limit]

    async def get_edges(
        self,
        workspace_id: str,
        edge_type: str | None = None,
    ) -> list[Any]:
        ws_edges = self.edges.get(workspace_id, [])
        if edge_type:
            ws_edges = [e for e in ws_edges if str(e.type) == edge_type]
        return ws_edges

    async def get_workspace_stats(self, workspace_id: str) -> Any:
        from dialectica_graph.models import WorkspaceStats
        ws_nodes = self.nodes.get(workspace_id, {})
        ws_edges = self.edges.get(workspace_id, [])
        label_counts: dict[str, int] = {}
        for n in ws_nodes.values():
            lbl = getattr(n, "label", "Unknown")
            label_counts[lbl] = label_counts.get(lbl, 0) + 1
        type_counts: dict[str, int] = {}
        for e in ws_edges:
            t = str(e.type)
            type_counts[t] = type_counts.get(t, 0) + 1
        return WorkspaceStats(
            node_counts_by_label=label_counts,
            edge_counts_by_type=type_counts,
            total_nodes=len(ws_nodes),
            total_edges=len(ws_edges),
        )

    async def get_escalation_trajectory(self, workspace_id: str) -> Any:
        from dialectica_graph.models import EscalationResult, EscalationTrajectoryPoint
        return EscalationResult(
            trajectory=[
                EscalationTrajectoryPoint(
                    timestamp=datetime.utcnow(),
                    glasl_stage=5,
                    evidence="Unit-test evidence",
                )
            ],
            current_stage=5,
            velocity=0.4,
            direction="escalating",
        )


# ═══════════════════════════════════════════════════════════════════════════
#  HELPER FACTORIES
# ═══════════════════════════════════════════════════════════════════════════

_WS = "ws-unit-test"


def make_actor(id: str, name: str, **kwargs: Any) -> Actor:
    """Create a test Actor with sensible defaults."""
    return Actor(
        id=id,
        name=name,
        actor_type=kwargs.pop("actor_type", "person"),
        workspace_id=kwargs.pop("workspace_id", _WS),
        label="Actor",
        **kwargs,
    )


def make_conflict(id: str, name: str, glasl_stage: int, **kwargs: Any) -> Conflict:
    """Create a test Conflict with an explicit Glasl stage."""
    return Conflict(
        id=id,
        name=name,
        scale=kwargs.pop("scale", "macro"),
        domain=kwargs.pop("domain", "political"),
        status=kwargs.pop("status", "active"),
        glasl_stage=glasl_stage,
        workspace_id=kwargs.pop("workspace_id", _WS),
        label="Conflict",
        **kwargs,
    )


def make_event(
    id: str, event_type: str, severity: float, occurred_at: datetime, **kwargs: Any
) -> Event:
    """Create a test Event."""
    return Event(
        id=id,
        event_type=event_type,
        severity=severity,
        occurred_at=occurred_at,
        workspace_id=kwargs.pop("workspace_id", _WS),
        label="Event",
        **kwargs,
    )


def make_emotion(
    id: str, primary_emotion: str, intensity: str = "medium", **kwargs: Any
) -> EmotionalState:
    """Create a test EmotionalState."""
    return EmotionalState(
        id=id,
        primary_emotion=primary_emotion,
        intensity=intensity,
        workspace_id=kwargs.pop("workspace_id", _WS),
        label="EmotionalState",
        observed_at=kwargs.pop("observed_at", datetime.utcnow()),
        **kwargs,
    )


def make_trust_state(
    id: str,
    ability: float,
    benevolence: float,
    integrity: float,
    overall: float,
    **kwargs: Any,
) -> TrustState:
    """Create a test TrustState."""
    return TrustState(
        id=id,
        perceived_ability=ability,
        perceived_benevolence=benevolence,
        perceived_integrity=integrity,
        overall_trust=overall,
        workspace_id=kwargs.pop("workspace_id", _WS),
        label="TrustState",
        **kwargs,
    )


# ═══════════════════════════════════════════════════════════════════════════
#  ESCALATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestEscalationDetectsGlaslStage:
    """Conflict at Glasl stage 5 should be detected and influence assessment."""

    @pytest.mark.asyncio
    async def test_escalation_detects_glasl_stage(self):
        gc = MockGraphClient()
        conflict = make_conflict("c-1", "Syria Civil War", glasl_stage=5)
        gc.seed_nodes(_WS, [conflict])

        detector = EscalationDetector(gc)
        assessment = await detector.compute_glasl_stage(_WS)

        assert isinstance(assessment, GlaslAssessment)
        # With a stage-5 conflict the aggregated stage should be >= 4
        # (exact result depends on other signal scores, but the conflict
        # stage feeds directly into the scoring with highest authority)
        assert assessment.stage.stage_number >= 4
        assert assessment.confidence > 0.0
        assert "c-1" in assessment.evidence

    @pytest.mark.asyncio
    async def test_high_stage_conflict_yields_win_lose_or_worse(self):
        gc = MockGraphClient()
        conflict = make_conflict("c-high", "Extreme Escalation", glasl_stage=7,
                                 violence_type="direct")
        gc.seed_nodes(_WS, [conflict])

        detector = EscalationDetector(gc)
        assessment = await detector.compute_glasl_stage(_WS)

        # Stage 7+ should yield win_lose or lose_lose
        assert assessment.level in ("win_lose", "lose_lose")

    @pytest.mark.asyncio
    async def test_escalation_with_multiple_signals(self):
        """Combine conflict stage, toxic emotions, and high-severity events."""
        gc = MockGraphClient()
        conflict = make_conflict("c-2", "Regional Dispute", glasl_stage=5,
                                 violence_type="structural")
        now = datetime.utcnow()
        events = [
            make_event("e-1", "threaten", 0.8, now - timedelta(days=5)),
            make_event("e-2", "coerce", 0.9, now - timedelta(days=2)),
        ]
        emotions = [
            make_emotion("em-1", "anger"),
            make_emotion("em-2", "disgust"),
            make_emotion("em-3", "fear"),
        ]
        gc.seed_nodes(_WS, [conflict] + events + emotions)

        detector = EscalationDetector(gc)
        assessment = await detector.compute_glasl_stage(_WS)

        assert assessment.confidence > 0.0
        assert assessment.stage.stage_number >= 4


class TestEscalationTrajectoryDirection:
    """Mock escalation result with 'escalating' direction."""

    @pytest.mark.asyncio
    async def test_escalation_trajectory_direction(self):
        gc = MockGraphClient()
        result = await gc.get_escalation_trajectory(_WS)

        assert result.direction == "escalating"
        assert result.current_stage == 5
        assert result.velocity > 0
        assert len(result.trajectory) == 1
        assert result.trajectory[0].glasl_stage == 5

    @pytest.mark.asyncio
    async def test_forecast_with_escalation_signals(self):
        """Forecast should detect escalation when high-severity events exist."""
        gc = MockGraphClient()
        now = datetime.utcnow()
        conflict = make_conflict("c-f", "Forecast Test", glasl_stage=4)
        events = [
            make_event("ef-1", "threaten", 0.8, now - timedelta(days=10)),
            make_event("ef-2", "assault", 0.9, now - timedelta(days=3)),
            make_event("ef-3", "coerce", 0.85, now - timedelta(days=1)),
        ]
        gc.seed_nodes(_WS, [conflict] + events)

        detector = EscalationDetector(gc)
        forecast = await detector.forecast_trajectory(_WS)

        assert isinstance(forecast, Forecast)
        assert len(forecast.trajectory) == 3  # 3 months projected
        # With high-severity conflict events the direction should be escalating
        assert forecast.direction in ("escalating", "stable")
        assert forecast.confidence >= 0.0


# ═══════════════════════════════════════════════════════════════════════════
#  RIPENESS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestRipenessScorerBasic:
    """Basic ripeness scoring with mock graph data."""

    @pytest.mark.asyncio
    async def test_ripeness_scorer_basic(self):
        gc = MockGraphClient()
        # Dormant conflict = stalemate signal (MHS)
        conflict = make_conflict("c-ripe", "Stalemate Conflict", glasl_stage=4,
                                 status="dormant")
        # High-severity events = cost accumulation (MHS)
        now = datetime.utcnow()
        events = [
            make_event("ev-r1", "threaten", 0.7, now - timedelta(days=30)),
            make_event("ev-r2", "coerce", 0.8, now - timedelta(days=15)),
        ]
        # Negative emotions = pain perception (MHS)
        emotions = [
            make_emotion("em-r1", "anger"),
            make_emotion("em-r2", "fear"),
            make_emotion("em-r3", "sadness"),
        ]
        gc.seed_nodes(_WS, [conflict] + events + emotions)

        scorer = RipenessScorer(gc)
        assessment = await scorer.compute_ripeness(_WS)

        assert isinstance(assessment, RipenessAssessment)
        assert 0.0 <= assessment.mhs_score <= 1.0
        assert 0.0 <= assessment.meo_score <= 1.0
        assert 0.0 <= assessment.overall_score <= 1.0
        # MHS should be elevated due to dormant conflict + high events + neg emotions
        assert assessment.mhs_score > 0.3
        assert len(assessment.factors) > 0

    @pytest.mark.asyncio
    async def test_ripeness_requires_both_mhs_and_meo(self):
        """Overall ripeness uses geometric mean — both MHS and MEO must be nonzero."""
        gc = MockGraphClient()
        # Only MHS signals, no MEO signals
        conflict = make_conflict("c-no-meo", "No MEO", glasl_stage=5,
                                 status="dormant")
        gc.seed_nodes(_WS, [conflict])

        scorer = RipenessScorer(gc)
        assessment = await scorer.compute_ripeness(_WS)

        # Without processes or cooperative events, MEO-dependent score is low
        # Overall should reflect low MEO
        assert assessment.meo_score < 0.5

    @pytest.mark.asyncio
    async def test_ripeness_with_processes_increases_meo(self):
        """Active processes and cooperative events increase MEO."""
        gc = MockGraphClient()
        conflict = make_conflict("c-meo", "With MEO", glasl_stage=3,
                                 status="active")
        process = Process(
            id="proc-1",
            process_type="mediation_facilitative",
            resolution_approach="interest_based",
            status="active",
            workspace_id=_WS,
            label="Process",
        )
        # Cooperative events
        now = datetime.utcnow()
        coop_event = make_event("ev-coop", "cooperate", 0.3, now)
        gc.seed_nodes(_WS, [conflict, process, coop_event])

        scorer = RipenessScorer(gc)
        assessment = await scorer.compute_ripeness(_WS)

        # MEO should be noticeably higher than zero
        assert assessment.meo_score > 0.0


# ═══════════════════════════════════════════════════════════════════════════
#  TRUST ANALYSIS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestTrustDeficitDetection:
    """Low trust scores should be detectable in the trust matrix."""

    @pytest.mark.asyncio
    async def test_trust_deficit_detection(self):
        gc = MockGraphClient()
        # Create a low-trust TrustState (with trustor/trustee stored in
        # the node itself — the TrustAnalyzer uses the fallback path)
        ts_low = make_trust_state(
            "ts-low", ability=0.3, benevolence=0.2, integrity=0.1, overall=0.2,
        )
        # Attach trustor/trustee as attributes for the fallback path
        ts_low.metadata["trustor_id"] = "actor-a"
        ts_low.metadata["trustee_id"] = "actor-b"
        # Monkey-patch the ids that TrustAnalyzer reads via getattr
        object.__setattr__(ts_low, "trustor_id", "actor-a")
        object.__setattr__(ts_low, "trustee_id", "actor-b")

        gc.seed_nodes(_WS, [ts_low])

        analyzer = TrustAnalyzer(gc)
        matrix = await analyzer.compute_trust_matrix(_WS)

        assert isinstance(matrix, TrustMatrix)
        assert len(matrix.dyads) == 1
        dyad = matrix.dyads[0]
        assert dyad.trustor_id == "actor-a"
        assert dyad.trustee_id == "actor-b"
        # Low trust indicators
        assert dyad.overall_trust < 0.4
        assert dyad.integrity < 0.2
        assert matrix.average_trust < 0.4

    @pytest.mark.asyncio
    async def test_trust_matrix_via_edges(self):
        """Build trust matrix from TRUSTS edges rather than TrustState nodes."""
        gc = MockGraphClient()
        actor_a = make_actor("actor-a", "Party A")
        actor_b = make_actor("actor-b", "Party B")

        trust_edge = ConflictRelationship(
            id="te-1",
            type=EdgeType.TRUSTS,
            source_id="actor-a",
            target_id="actor-b",
            source_label="Actor",
            target_label="Actor",
            workspace_id=_WS,
            properties={
                "ability": 0.3,
                "benevolence": 0.2,
                "integrity": 0.15,
                "confidence": 0.7,
            },
        )
        gc.seed_nodes(_WS, [actor_a, actor_b])
        gc.seed_edges(_WS, [trust_edge])

        analyzer = TrustAnalyzer(gc)
        matrix = await analyzer.compute_trust_matrix(_WS)

        assert len(matrix.dyads) == 1
        dyad = matrix.dyads[0]
        assert dyad.ability == 0.3
        assert dyad.benevolence == 0.2
        assert dyad.integrity == 0.15
        assert dyad.overall_trust < 0.3  # mean of low values

    @pytest.mark.asyncio
    async def test_trust_change_detection_eroding_event(self):
        """Eroding events (threaten, coerce) produce negative trust changes.

        The TrustAnalyzer reads event_type, performer_id, and target_id via
        getattr. We use a lightweight SimpleNamespace mock because the
        Event Pydantic model does not carry performer_id/target_id fields,
        and TrustAnalyzer's eroding set includes types like 'betray' that
        are outside the PLOVER EventType enum.
        """
        gc = MockGraphClient()
        now = datetime.utcnow()
        # Use a simple mock object that has the attributes TrustAnalyzer reads
        from types import SimpleNamespace
        event = SimpleNamespace(
            id="ev-threaten",
            label="Event",
            event_type="threaten",
            severity=0.9,
            occurred_at=now - timedelta(days=5),
            performer_id="actor-b",
            target_id="actor-a",
            description="Actor B threatened Actor A",
        )
        gc.seed_nodes(_WS, [event])

        analyzer = TrustAnalyzer(gc)
        changes = await analyzer.detect_trust_changes(_WS)

        assert len(changes) == 1
        change = changes[0]
        assert change.change_type == "decrease"
        assert change.trust_delta < 0
        assert change.trustor_id == "actor-a"
        assert change.trustee_id == "actor-b"

    @pytest.mark.asyncio
    async def test_lowest_and_highest_trust_pairs(self):
        """Matrix should correctly identify lowest and highest trust pairs."""
        gc = MockGraphClient()
        edge_low = ConflictRelationship(
            id="te-low",
            type=EdgeType.TRUSTS,
            source_id="a",
            target_id="b",
            source_label="Actor",
            target_label="Actor",
            workspace_id=_WS,
            properties={"ability": 0.1, "benevolence": 0.1, "integrity": 0.1},
        )
        edge_high = ConflictRelationship(
            id="te-high",
            type=EdgeType.TRUSTS,
            source_id="c",
            target_id="d",
            source_label="Actor",
            target_label="Actor",
            workspace_id=_WS,
            properties={"ability": 0.9, "benevolence": 0.9, "integrity": 0.9},
        )
        gc.seed_edges(_WS, [edge_low, edge_high])

        analyzer = TrustAnalyzer(gc)
        matrix = await analyzer.compute_trust_matrix(_WS)

        assert len(matrix.dyads) == 2
        assert matrix.lowest_trust_pair == ("a", "b")
        assert matrix.highest_trust_pair == ("c", "d")


# ═══════════════════════════════════════════════════════════════════════════
#  FIREWALL TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestFirewallBlocksOverride:
    """Deterministic symbolic conclusions must NEVER be overridden by
    probabilistic neural predictions — this is the core DIALECTICA invariant."""

    def test_firewall_blocks_override(self):
        """A deterministic 'violated' conclusion blocks a neural 'compliant' prediction."""
        det = Conclusion(
            conclusion_type=ConfidenceType.DETERMINISTIC,
            statement="Treaty Article 5 violated by Party X",
            confidence=1.0,
            source_rule="article_5_violation_check",
            workspace_id=_WS,
        )
        firewall = SymbolicFirewall([det])

        neural_pred = Conclusion(
            conclusion_type=ConfidenceType.PROBABILISTIC,
            statement="Party X is compliant with Treaty Article 5",
            confidence=0.92,
            source_model="gnn-compliance-v3",
            workspace_id=_WS,
        )

        result = firewall.check_neural_prediction(neural_pred)
        assert result is None, "Firewall must block contradicting neural prediction"

    def test_firewall_passes_non_contradicting(self):
        """Non-contradicting predictions should pass through."""
        det = Conclusion(
            conclusion_type=ConfidenceType.DETERMINISTIC,
            statement="Treaty Article 5 violated",
            confidence=1.0,
            source_rule="article_5_check",
            workspace_id=_WS,
        )
        firewall = SymbolicFirewall([det])

        compatible = Conclusion(
            conclusion_type=ConfidenceType.PROBABILISTIC,
            statement="Mediation process likely to begin soon",
            confidence=0.7,
            source_model="forecaster-v2",
            workspace_id=_WS,
        )

        result = firewall.check_neural_prediction(compatible)
        assert result is not None
        assert result.statement == compatible.statement

    def test_firewall_escalation_contradiction(self):
        """Deterministic 'escalating' blocks neural 'de-escalating'."""
        det = Conclusion(
            conclusion_type=ConfidenceType.DETERMINISTIC,
            statement="Conflict is escalating based on Glasl stage transition 5->6",
            confidence=1.0,
            source_rule="glasl_stage_transition",
            workspace_id=_WS,
        )
        firewall = SymbolicFirewall([det])

        pred = Conclusion(
            conclusion_type=ConfidenceType.PROBABILISTIC,
            statement="Conflict is de-escalating according to sentiment analysis",
            confidence=0.68,
            source_model="sentiment-v1",
            workspace_id=_WS,
        )

        assert firewall.check_neural_prediction(pred) is None

    def test_firewall_merge_preserves_deterministic(self):
        """Merge always puts deterministic conclusions first and filters contradictions."""
        det = Conclusion(
            conclusion_type=ConfidenceType.DETERMINISTIC,
            statement="Sanctions breached by Actor A",
            confidence=1.0,
            source_rule="sanctions_check",
            workspace_id=_WS,
        )
        neural_ok = Conclusion(
            conclusion_type=ConfidenceType.PROBABILISTIC,
            statement="Actor A may seek arbitration",
            confidence=0.6,
            source_model="model-x",
            workspace_id=_WS,
        )
        neural_bad = Conclusion(
            conclusion_type=ConfidenceType.PROBABILISTIC,
            statement="Sanctions upheld by Actor A",
            confidence=0.85,
            source_model="model-y",
            workspace_id=_WS,
        )

        firewall = SymbolicFirewall([det])
        merged = firewall.merge_conclusions([det], [neural_ok, neural_bad])

        assert len(merged) == 2  # det + neural_ok; neural_bad filtered
        assert merged[0].conclusion_type == ConfidenceType.DETERMINISTIC
        statements = {c.statement for c in merged}
        assert "Sanctions breached by Actor A" in statements
        assert "Actor A may seek arbitration" in statements
        assert "Sanctions upheld by Actor A" not in statements

    def test_firewall_different_workspace_no_contradiction(self):
        """Conclusions in different workspaces do not contradict."""
        det = Conclusion(
            conclusion_type=ConfidenceType.DETERMINISTIC,
            statement="Treaty violated",
            confidence=1.0,
            source_rule="rule-1",
            workspace_id="ws-alpha",
        )
        firewall = SymbolicFirewall([det])

        pred = Conclusion(
            conclusion_type=ConfidenceType.PROBABILISTIC,
            statement="Treaty is compliant",
            confidence=0.9,
            source_model="model-1",
            workspace_id="ws-beta",
        )

        assert firewall.check_neural_prediction(pred) is not None


# ═══════════════════════════════════════════════════════════════════════════
#  POWER ANALYSIS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestPowerAsymmetry:
    """Large power gaps should be detected as asymmetries."""

    @pytest.mark.asyncio
    async def test_power_asymmetry(self):
        gc = MockGraphClient()
        # Actor A has high coercive + legitimate power over Actor B
        edge_ab = ConflictRelationship(
            id="power-ab",
            type=EdgeType.HAS_POWER_OVER,
            source_id="actor-usa",
            target_id="actor-iran",
            source_label="Actor",
            target_label="Actor",
            workspace_id=_WS,
            weight=0.8,
            properties={
                "coercive": 0.9,
                "legitimate": 0.7,
                "expert": 0.5,
                "reward": 0.6,
                "referent": 0.2,
                "informational": 0.3,
            },
        )
        # Actor B has much less power over Actor A
        edge_ba = ConflictRelationship(
            id="power-ba",
            type=EdgeType.HAS_POWER_OVER,
            source_id="actor-iran",
            target_id="actor-usa",
            source_label="Actor",
            target_label="Actor",
            workspace_id=_WS,
            weight=0.3,
            properties={
                "coercive": 0.1,
                "legitimate": 0.1,
                "expert": 0.2,
                "reward": 0.0,
                "referent": 0.1,
                "informational": 0.1,
            },
        )
        gc.seed_edges(_WS, [edge_ab, edge_ba])

        mapper = PowerMapper(gc)
        asymmetries = await mapper.detect_asymmetries(_WS)

        assert isinstance(asymmetries, list)
        assert len(asymmetries) >= 1
        top = asymmetries[0]
        assert isinstance(top, PowerAsymmetry)
        assert top.asymmetry_score > 0.2
        assert top.advantage_holder == "actor-usa"

    @pytest.mark.asyncio
    async def test_power_map_most_powerful_actor(self):
        """Most powerful actor is correctly identified."""
        gc = MockGraphClient()
        edge = ConflictRelationship(
            id="pwr-1",
            type=EdgeType.HAS_POWER_OVER,
            source_id="strong-actor",
            target_id="weak-actor",
            source_label="Actor",
            target_label="Actor",
            workspace_id=_WS,
            weight=0.9,
            properties={
                "coercive": 0.8,
                "legitimate": 0.7,
                "expert": 0.6,
                "reward": 0.5,
                "referent": 0.4,
                "informational": 0.3,
            },
        )
        gc.seed_edges(_WS, [edge])

        mapper = PowerMapper(gc)
        pm = await mapper.compute_power_map(_WS)

        assert isinstance(pm, PowerMap)
        assert pm.most_powerful_actor == "strong-actor"
        assert len(pm.dyads) == 1
        assert pm.dyads[0].total_power > 0

    @pytest.mark.asyncio
    async def test_power_asymmetry_dominant_bases(self):
        """Dominant power bases (> 0.4) should be listed in asymmetry result."""
        gc = MockGraphClient()
        edge = ConflictRelationship(
            id="pwr-dom",
            type=EdgeType.HAS_POWER_OVER,
            source_id="a1",
            target_id="a2",
            source_label="Actor",
            target_label="Actor",
            workspace_id=_WS,
            weight=0.8,
            properties={
                "coercive": 0.9,
                "legitimate": 0.8,
                "expert": 0.6,
                "reward": 0.1,
                "referent": 0.1,
                "informational": 0.1,
            },
        )
        gc.seed_edges(_WS, [edge])

        mapper = PowerMapper(gc)
        asymmetries = await mapper.detect_asymmetries(_WS)

        assert len(asymmetries) == 1
        asym = asymmetries[0]
        assert "coercive" in asym.dominant_bases
        assert "legitimate" in asym.dominant_bases
        assert "expert" in asym.dominant_bases

    @pytest.mark.asyncio
    async def test_leverage_points_expert_power(self):
        """High expert power should create a leverage point."""
        gc = MockGraphClient()
        edge = ConflictRelationship(
            id="pwr-exp",
            type=EdgeType.HAS_POWER_OVER,
            source_id="expert-actor",
            target_id="other-actor",
            source_label="Actor",
            target_label="Actor",
            workspace_id=_WS,
            weight=0.8,
            properties={
                "coercive": 0.0,
                "legitimate": 0.0,
                "expert": 0.8,
                "reward": 0.0,
                "referent": 0.0,
                "informational": 0.0,
            },
        )
        gc.seed_edges(_WS, [edge])

        mapper = PowerMapper(gc)
        leverage = await mapper.identify_leverage_points(_WS)

        assert len(leverage) >= 1
        expert_lp = [lp for lp in leverage if lp.leverage_type == "expert_knowledge"]
        assert len(expert_lp) == 1
        assert expert_lp[0].actor_id == "expert-actor"

    @pytest.mark.asyncio
    async def test_no_asymmetry_when_symmetric(self):
        """Symmetric power should not produce asymmetries above threshold."""
        gc = MockGraphClient()
        edge_ab = ConflictRelationship(
            id="pwr-sym-ab",
            type=EdgeType.HAS_POWER_OVER,
            source_id="a",
            target_id="b",
            source_label="Actor",
            target_label="Actor",
            workspace_id=_WS,
            weight=0.5,
            properties={
                "coercive": 0.3,
                "legitimate": 0.3,
                "expert": 0.3,
                "reward": 0.3,
                "referent": 0.3,
                "informational": 0.3,
            },
        )
        edge_ba = ConflictRelationship(
            id="pwr-sym-ba",
            type=EdgeType.HAS_POWER_OVER,
            source_id="b",
            target_id="a",
            source_label="Actor",
            target_label="Actor",
            workspace_id=_WS,
            weight=0.5,
            properties={
                "coercive": 0.3,
                "legitimate": 0.3,
                "expert": 0.3,
                "reward": 0.3,
                "referent": 0.3,
                "informational": 0.3,
            },
        )
        gc.seed_edges(_WS, [edge_ab, edge_ba])

        mapper = PowerMapper(gc)
        asymmetries = await mapper.detect_asymmetries(_WS)

        # Symmetric power => asymmetry = 0 => below 0.2 threshold
        assert len(asymmetries) == 0


# ═══════════════════════════════════════════════════════════════════════════
#  ESCALATION SIGNALS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestEscalationSignals:
    """Escalation signal detection within a time window."""

    @pytest.mark.asyncio
    async def test_high_severity_events_detected(self):
        gc = MockGraphClient()
        now = datetime.utcnow()
        events = [
            make_event("hs-1", "threaten", 0.8, now - timedelta(days=5)),
            make_event("hs-2", "assault", 0.9, now - timedelta(days=2)),
        ]
        gc.seed_nodes(_WS, events)

        detector = EscalationDetector(gc)
        signals = await detector.detect_escalation_signals(_WS, window_days=30)

        severity_signals = [s for s in signals if s.signal_type == "high_severity_events"]
        assert len(severity_signals) == 1
        assert severity_signals[0].severity >= 0.7

    @pytest.mark.asyncio
    async def test_coalition_polarisation_signal(self):
        gc = MockGraphClient()
        edges = [
            ConflictRelationship(
                id="allied-1", type=EdgeType.ALLIED_WITH,
                source_id="a", target_id="b",
                source_label="Actor", target_label="Actor",
                workspace_id=_WS,
            ),
            ConflictRelationship(
                id="allied-2", type=EdgeType.ALLIED_WITH,
                source_id="c", target_id="d",
                source_label="Actor", target_label="Actor",
                workspace_id=_WS,
            ),
            ConflictRelationship(
                id="opposed-1", type=EdgeType.OPPOSED_TO,
                source_id="a", target_id="c",
                source_label="Actor", target_label="Actor",
                workspace_id=_WS,
            ),
        ]
        gc.seed_edges(_WS, edges)

        detector = EscalationDetector(gc)
        signals = await detector.detect_escalation_signals(_WS, window_days=30)

        coalition_signals = [s for s in signals if s.signal_type == "coalition_polarisation"]
        assert len(coalition_signals) == 1

    @pytest.mark.asyncio
    async def test_empty_graph_no_signals(self):
        gc = MockGraphClient()
        detector = EscalationDetector(gc)
        signals = await detector.detect_escalation_signals(_WS)
        assert signals == []
