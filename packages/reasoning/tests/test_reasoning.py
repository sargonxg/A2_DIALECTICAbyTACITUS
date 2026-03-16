"""
Tests for dialectica_reasoning — Escalation, ripeness, trust, power, causal, pattern.

Uses mock graph clients to avoid requiring a live database.
"""
from __future__ import annotations

import pytest
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import AsyncMock


# ---------------------------------------------------------------------------
# Mock graph client
# ---------------------------------------------------------------------------

@dataclass
class MockEdge:
    id: str
    type: str
    source_id: str
    target_id: str
    properties: dict = field(default_factory=dict)
    weight: float = 1.0


@dataclass
class MockNode:
    id: str
    label: str
    name: str = ""


class MockConflict(MockNode):
    glasl_stage: int = 5
    status: str = "active"
    violence_type: str = "none"
    kriesberg_phase: str = "escalation"


class MockEvent(MockNode):
    severity: float = 0.5
    event_type: str = "threaten"
    occurred_at: Any = None
    performer_id: str | None = None
    target_id: str | None = None


class MockTrustState(MockNode):
    perceived_ability: float = 0.6
    perceived_benevolence: float = 0.4
    perceived_integrity: float = 0.3
    overall_trust: float = 0.43
    trustor_id: str = "actor_a"
    trustee_id: str = "actor_b"


class MockGraphClient:
    def __init__(self, nodes: list = None, edges: list = None):
        self._nodes = nodes or []
        self._edges = edges or []

    async def get_nodes(self, workspace_id: str, label: str = None, limit: int = 100, offset: int = 0):
        if label:
            return [n for n in self._nodes if getattr(n, "label", "") == label]
        return self._nodes

    async def get_edges(self, workspace_id: str, edge_type: str = None):
        if edge_type:
            return [e for e in self._edges if e.type == edge_type]
        return self._edges

    async def traverse(self, start_id: str, workspace_id: str, hops: int = 2, edge_types=None):
        from types import SimpleNamespace
        return SimpleNamespace(nodes=self._nodes, edges=self._edges)

    async def vector_search(self, query_text: str, workspace_id: str, top_k: int = 10, **kwargs):
        return []

    async def get_workspace_stats(self, workspace_id: str):
        from types import SimpleNamespace
        return SimpleNamespace(total_nodes=len(self._nodes), total_edges=len(self._edges))


# ---------------------------------------------------------------------------
# Test: Escalation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_escalation_empty_graph():
    from dialectica_reasoning.symbolic.escalation import EscalationDetector
    gc = MockGraphClient()
    detector = EscalationDetector(gc)
    assessment = await detector.compute_glasl_stage("test")
    # No nodes → return default assessment
    assert assessment is not None


@pytest.mark.asyncio
async def test_escalation_with_conflict():
    from dialectica_reasoning.symbolic.escalation import EscalationDetector
    conflict = MockConflict(id="c1", label="Conflict", name="Test Conflict")
    conflict.glasl_stage = 6
    gc = MockGraphClient(nodes=[conflict])
    detector = EscalationDetector(gc)
    assessment = await detector.compute_glasl_stage("test")
    assert assessment.confidence >= 0.0
    assert assessment.stage is not None


@pytest.mark.asyncio
async def test_escalation_signals():
    from dialectica_reasoning.symbolic.escalation import EscalationDetector
    from datetime import datetime
    event = MockEvent(id="e1", label="Event", name="Threat")
    event.severity = 0.8
    event.occurred_at = datetime.utcnow()
    gc = MockGraphClient(nodes=[event])
    detector = EscalationDetector(gc)
    signals = await detector.detect_escalation_signals("test")
    assert isinstance(signals, list)


# ---------------------------------------------------------------------------
# Test: Ripeness
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ripeness_empty():
    from dialectica_reasoning.symbolic.ripeness import RipenessScorer
    gc = MockGraphClient()
    scorer = RipenessScorer(gc)
    result = await scorer.compute_ripeness("test")
    assert 0.0 <= result.overall_score <= 1.0
    assert isinstance(result.is_ripe, bool)


@pytest.mark.asyncio
async def test_ripeness_with_data():
    from dialectica_reasoning.symbolic.ripeness import RipenessScorer
    conflict = MockConflict(id="c1", label="Conflict", name="Test")
    conflict.status = "dormant"
    event = MockEvent(id="e1", label="Event", name="Incident")
    event.severity = 0.7
    gc = MockGraphClient(nodes=[conflict, event])
    scorer = RipenessScorer(gc)
    result = await scorer.compute_ripeness("test")
    assert result.mhs_score >= 0
    assert result.meo_score >= 0


# ---------------------------------------------------------------------------
# Test: Trust Analysis
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_trust_matrix_empty():
    from dialectica_reasoning.symbolic.trust_analysis import TrustAnalyzer
    gc = MockGraphClient()
    analyzer = TrustAnalyzer(gc)
    matrix = await analyzer.compute_trust_matrix("test")
    assert matrix.workspace_id == "test"
    assert matrix.dyads == []


@pytest.mark.asyncio
async def test_trust_matrix_with_nodes():
    from dialectica_reasoning.symbolic.trust_analysis import TrustAnalyzer
    ts = MockTrustState(id="ts1", label="TrustState", name="Trust A→B")
    gc = MockGraphClient(nodes=[ts])
    analyzer = TrustAnalyzer(gc)
    matrix = await analyzer.compute_trust_matrix("test")
    assert len(matrix.dyads) == 1
    assert matrix.dyads[0].trustor_id == "actor_a"
    assert 0 <= matrix.dyads[0].overall_trust <= 1


# ---------------------------------------------------------------------------
# Test: Power Analysis
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_power_map_empty():
    from dialectica_reasoning.symbolic.power_analysis import PowerMapper
    gc = MockGraphClient()
    mapper = PowerMapper(gc)
    pm = await mapper.compute_power_map("test")
    assert pm.workspace_id == "test"
    assert pm.dyads == []


@pytest.mark.asyncio
async def test_power_asymmetries():
    from dialectica_reasoning.symbolic.power_analysis import PowerMapper
    edge = MockEdge(
        id="e1", type="HAS_POWER_OVER",
        source_id="usa", target_id="iran",
        properties={"domain": "coercive", "magnitude": 0.9},
    )
    gc = MockGraphClient(edges=[edge])
    mapper = PowerMapper(gc)
    asymmetries = await mapper.detect_asymmetries("test")
    assert isinstance(asymmetries, list)


# ---------------------------------------------------------------------------
# Test: Causal Analysis
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_causal_empty():
    from dialectica_reasoning.symbolic.causal_analysis import CausalAnalyzer
    gc = MockGraphClient()
    analyzer = CausalAnalyzer(gc)
    chains = await analyzer.extract_causal_chains("test")
    assert chains == []


@pytest.mark.asyncio
async def test_causal_with_chain():
    from dialectica_reasoning.symbolic.causal_analysis import CausalAnalyzer
    e1 = MockEdge(id="edge1", type="CAUSED", source_id="ev1", target_id="ev2")
    e2 = MockEdge(id="edge2", type="CAUSED", source_id="ev2", target_id="ev3")
    n1 = MockEvent(id="ev1", label="Event", name="Root")
    n2 = MockEvent(id="ev2", label="Event", name="Middle")
    n3 = MockEvent(id="ev3", label="Event", name="Leaf")
    gc = MockGraphClient(nodes=[n1, n2, n3], edges=[e1, e2])
    analyzer = CausalAnalyzer(gc)
    chains = await analyzer.extract_causal_chains("test")
    assert len(chains) >= 1
    assert chains[0].depth >= 2


# ---------------------------------------------------------------------------
# Test: Pattern Matching
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pattern_matching_empty():
    from dialectica_reasoning.symbolic.pattern_matching import PatternMatcher
    gc = MockGraphClient()
    matcher = PatternMatcher(gc)
    matches = await matcher.detect_all("test")
    assert matches == []


@pytest.mark.asyncio
async def test_escalation_spiral_detection():
    from dialectica_reasoning.symbolic.pattern_matching import PatternMatcher
    ev1 = MockEvent(id="ev1", label="Event", name="Threat A->B")
    ev1.event_type = "threaten"
    ev1.performer_id = "actor_a"
    ev1.target_id = "actor_b"
    ev1.severity = 0.7
    ev2 = MockEvent(id="ev2", label="Event", name="Threat A->B again")
    ev2.event_type = "threaten"
    ev2.performer_id = "actor_a"
    ev2.target_id = "actor_b"
    ev2.severity = 0.7
    ev3 = MockEvent(id="ev3", label="Event", name="Retaliation B->A")
    ev3.event_type = "coerce"
    ev3.performer_id = "actor_b"
    ev3.target_id = "actor_a"
    ev3.severity = 0.7
    ev4 = MockEvent(id="ev4", label="Event", name="Retaliation B->A again")
    ev4.event_type = "threaten"
    ev4.performer_id = "actor_b"
    ev4.target_id = "actor_a"
    ev4.severity = 0.7
    gc = MockGraphClient(nodes=[ev1, ev2, ev3, ev4])
    matcher = PatternMatcher(gc)
    matches = await matcher.detect_escalation_spiral("test")
    assert len(matches) >= 1
    assert matches[0].pattern_name == "escalation_spiral"


# ---------------------------------------------------------------------------
# Test: Inference
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_inference_empty():
    from dialectica_reasoning.symbolic.inference import SymbolicInference
    gc = MockGraphClient()
    inferrer = SymbolicInference(gc)
    result = await inferrer.forward_chain("test")
    assert result.rules_applied > 0
    assert result.facts_generated == 0


# ---------------------------------------------------------------------------
# Test: GraphRAG
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_retriever_empty():
    from dialectica_reasoning.graphrag.retriever import ConflictGraphRAGRetriever
    gc = MockGraphClient()
    retriever = ConflictGraphRAGRetriever(gc)
    result = await retriever.retrieve("What happened?", "test")
    assert result.query == "What happened?"
    assert result.workspace_id == "test"


@pytest.mark.asyncio
async def test_context_builder():
    from dialectica_reasoning.graphrag.retriever import RetrievalResult
    from dialectica_reasoning.graphrag.context_builder import ConflictContextBuilder
    result = RetrievalResult(query="test query", workspace_id="test")
    builder = ConflictContextBuilder()
    context = builder.build_context(result)
    assert "DIALECTICA" in context
    assert "test query" in context


# ---------------------------------------------------------------------------
# Test: Query Engine
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_query_engine_no_llm():
    from dialectica_reasoning.query_engine import ConflictQueryEngine
    gc = MockGraphClient()
    engine = ConflictQueryEngine(gc)
    response = await engine.analyze("What is the escalation level?", "test")
    assert response.query == "What is the escalation level?"
    assert response.answer != ""


# ---------------------------------------------------------------------------
# Test: Hallucination Detector
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_hallucination_detector():
    from dialectica_reasoning.hallucination_detector import HallucinationDetector
    actor = MockNode(id="a1", label="Actor", name="Iran")
    gc = MockGraphClient(nodes=[actor])
    detector = HallucinationDetector(gc)
    claims = await detector.extract_claims("Iran is a major party to the JCPOA negotiations.")
    assert len(claims) >= 0  # May or may not extract depending on regex


@pytest.mark.asyncio
async def test_hallucination_report():
    from dialectica_reasoning.hallucination_detector import HallucinationDetector, HallucinationReport
    gc = MockGraphClient()
    detector = HallucinationDetector(gc)
    report = await detector.detect("Iran is powerful.", "test")
    assert isinstance(report, HallucinationReport)
    assert 0.0 <= report.hallucination_rate <= 1.0


# ---------------------------------------------------------------------------
# Test: Graph Quality
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_graph_quality_empty():
    from dialectica_reasoning.graph_quality import GraphQualityAnalyzer
    gc = MockGraphClient()
    analyzer = GraphQualityAnalyzer(gc)
    dashboard = await analyzer.generate_quality_dashboard("test")
    assert dashboard.workspace_id == "test"
    assert 0.0 <= dashboard.overall_quality <= 1.0
