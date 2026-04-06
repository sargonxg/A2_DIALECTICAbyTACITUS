"""
Tests for TheoristAgent — Verify all 15 frameworks are assessed.

Uses mock graph client to avoid requiring a live database.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Mock graph client (same pattern as test_reasoning.py)
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

    async def get_nodes(
        self, workspace_id: str, label: str = None, limit: int = 100, offset: int = 0
    ):
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
# All 15 expected framework IDs
# ---------------------------------------------------------------------------

EXPECTED_FRAMEWORKS = {
    "glasl",
    "zartman",
    "fisher_ury",
    "mayer_trust",
    "french_raven",
    "pearl_causal",
    "plutchik",
    "galtung",
    "winslade_monk",
    "kriesberg",
    # New 5:
    "burton_basic_needs",
    "lederach_transformation",
    "azar_protracted",
    "kelman_problem_solving",
    "deutsch_cooperation",
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_theorist_produces_15_frameworks():
    """TheoristAgent.run() should produce exactly 15 framework assessments."""
    from dialectica_reasoning.agents.theorist import TheoristAgent

    conflict = MockConflict(id="c1", label="Conflict", name="Test Conflict")
    actors = [
        MockNode(id="a1", label="Actor", name="Actor A"),
        MockNode(id="a2", label="Actor", name="Actor B"),
        MockNode(id="a3", label="Actor", name="Actor C"),
    ]
    event = MockEvent(id="e1", label="Event", name="Incident")
    trust = MockTrustState(id="ts1", label="TrustState", name="Trust A->B")

    gc = MockGraphClient(nodes=[conflict, *actors, event, trust])
    agent = TheoristAgent(gc)
    report = await agent.run("test")

    assert len(report.assessments) == 15
    framework_ids = {a.framework_id for a in report.assessments}
    assert framework_ids == EXPECTED_FRAMEWORKS


@pytest.mark.asyncio
async def test_theorist_empty_graph():
    """TheoristAgent should still produce 15 assessments on an empty graph."""
    from dialectica_reasoning.agents.theorist import TheoristAgent

    gc = MockGraphClient()
    agent = TheoristAgent(gc)
    report = await agent.run("empty")

    assert len(report.assessments) == 15


@pytest.mark.asyncio
async def test_theorist_top_framework_is_highest_score():
    """The top_framework field should be the highest-scored assessment."""
    from dialectica_reasoning.agents.theorist import TheoristAgent

    gc = MockGraphClient()
    agent = TheoristAgent(gc)
    report = await agent.run("test")

    assert report.top_framework == report.assessments[0].framework_name


@pytest.mark.asyncio
async def test_theorist_scores_in_valid_range():
    """All applicability scores should be between 0 and 1."""
    from dialectica_reasoning.agents.theorist import TheoristAgent

    actors = [MockNode(id=f"a{i}", label="Actor", name=f"Actor {i}") for i in range(6)]
    gc = MockGraphClient(nodes=actors)
    agent = TheoristAgent(gc)
    report = await agent.run("test")

    for assessment in report.assessments:
        assert 0.0 <= assessment.applicability_score <= 1.0, (
            f"{assessment.framework_id}: score={assessment.applicability_score}"
        )


@pytest.mark.asyncio
async def test_burton_needs_high_with_interests():
    """Burton should score high when interest nodes are present."""
    from dialectica_reasoning.agents.theorist import TheoristAgent

    interest = MockNode(id="i1", label="Interest", name="Security")
    gc = MockGraphClient(nodes=[interest])
    agent = TheoristAgent(gc)
    report = await agent.run("test")

    burton = next(a for a in report.assessments if a.framework_id == "burton_basic_needs")
    assert burton.applicability_score >= 0.7


@pytest.mark.asyncio
async def test_kelman_high_with_trust():
    """Kelman should score high when trust data is present."""
    from dialectica_reasoning.agents.theorist import TheoristAgent

    trust = MockTrustState(id="ts1", label="TrustState", name="Trust")
    gc = MockGraphClient(nodes=[trust])
    agent = TheoristAgent(gc)
    report = await agent.run("test")

    kelman = next(a for a in report.assessments if a.framework_id == "kelman_problem_solving")
    assert kelman.applicability_score >= 0.7


@pytest.mark.asyncio
async def test_azar_increases_with_escalation():
    """Azar should increase with higher Glasl stage and more actors."""
    from dialectica_reasoning.agents.theorist import TheoristAgent

    conflict = MockConflict(id="c1", label="Conflict", name="Protracted")
    conflict.glasl_stage = 8
    actors = [MockNode(id=f"a{i}", label="Actor", name=f"Actor {i}") for i in range(10)]
    gc = MockGraphClient(nodes=[conflict, *actors])
    agent = TheoristAgent(gc)
    report = await agent.run("test")

    azar = next(a for a in report.assessments if a.framework_id == "azar_protracted")
    assert azar.applicability_score >= 0.5


@pytest.mark.asyncio
async def test_synthesis_mentions_top_framework():
    """Synthesis text should mention the top framework name."""
    from dialectica_reasoning.agents.theorist import TheoristAgent

    gc = MockGraphClient()
    agent = TheoristAgent(gc)
    report = await agent.run("test")

    assert report.top_framework in report.synthesis
