"""
Tests for the Reasoning Persistence Layer.

Covers:
- ReasoningTrace and InferredFact model creation and validation
- write_reasoning_trace with a mocked graph client
- SymbolicFirewall.write_trace_to_graph helper
- EscalationDetector.write_back helper
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from dialectica_ontology.primitives import InferredFact, ReasoningTrace


# ---------------------------------------------------------------------------
# 1. Model creation
# ---------------------------------------------------------------------------


class TestReasoningTraceModel:
    def test_default_creation(self) -> None:
        trace = ReasoningTrace(
            workspace_id="ws-1",
            tenant_id="tenant-1",
        )
        assert trace.node_type == "ReasoningTrace"
        assert trace.label == "ReasoningTrace"
        assert trace.confidence_type == "deterministic"
        assert trace.confidence_score == 1.0
        assert trace.invalidated is False
        assert trace.validated_by is None
        assert trace.rules_fired == []
        assert trace.source_node_ids == []
        assert isinstance(trace.id, str) and len(trace.id) > 0

    def test_with_rules_and_conclusion(self) -> None:
        trace = ReasoningTrace(
            workspace_id="ws-1",
            tenant_id="tenant-1",
            rules_fired=["glasl_stage_derivation", "coalition_detection"],
            conclusion="Glasl stage 6 — WIN_LOSE level",
            confidence_score=0.85,
            source_node_ids=["node-a", "node-b"],
        )
        assert trace.rules_fired == ["glasl_stage_derivation", "coalition_detection"]
        assert trace.conclusion == "Glasl stage 6 — WIN_LOSE level"
        assert trace.confidence_score == 0.85
        assert trace.source_node_ids == ["node-a", "node-b"]

    def test_validated_trace(self) -> None:
        now = datetime.utcnow()
        trace = ReasoningTrace(
            workspace_id="ws-1",
            tenant_id="tenant-1",
            validated_by="analyst-007",
            validated_at=now,
        )
        assert trace.validated_by == "analyst-007"
        assert trace.validated_at == now

    def test_confidence_score_bounds(self) -> None:
        with pytest.raises(Exception):
            ReasoningTrace(
                workspace_id="ws-1",
                tenant_id="tenant-1",
                confidence_score=1.5,  # out of range
            )

    def test_model_dump(self) -> None:
        trace = ReasoningTrace(
            workspace_id="ws-1",
            tenant_id="tenant-1",
            rules_fired=["rule_a"],
            conclusion="Test conclusion",
        )
        data = trace.model_dump()
        assert data["workspace_id"] == "ws-1"
        assert data["node_type"] == "ReasoningTrace"
        assert "rules_fired" in data
        assert data["rules_fired"] == ["rule_a"]


class TestInferredFactModel:
    def test_default_creation(self) -> None:
        fact = InferredFact(
            workspace_id="ws-1",
            tenant_id="tenant-1",
            predicate="ESCALATION_RISK_HIGH",
            subject_node_id="conflict-123",
        )
        assert fact.node_type == "InferredFact"
        assert fact.label == "InferredFact"
        assert fact.predicate == "ESCALATION_RISK_HIGH"
        assert fact.subject_node_id == "conflict-123"
        assert fact.object_node_id is None
        assert fact.value is None
        assert fact.human_validated is False
        assert fact.human_verdict is None
        assert fact.trace_id is None

    def test_with_value_and_trace_link(self) -> None:
        fact = InferredFact(
            workspace_id="ws-1",
            tenant_id="tenant-1",
            predicate="RIPENESS_DETECTED",
            subject_node_id="conflict-456",
            value=0.78,
            trace_id="trace-abc",
            confidence_score=0.9,
        )
        assert fact.value == 0.78
        assert fact.trace_id == "trace-abc"
        assert fact.confidence_score == 0.9

    def test_with_object_node(self) -> None:
        fact = InferredFact(
            workspace_id="ws-1",
            tenant_id="tenant-1",
            predicate="ALLIED_WITH_INFERRED",
            subject_node_id="actor-a",
            object_node_id="actor-b",
        )
        assert fact.object_node_id == "actor-b"

    def test_bool_value(self) -> None:
        fact = InferredFact(
            workspace_id="ws-1",
            tenant_id="tenant-1",
            predicate="TREATY_VIOLATION",
            subject_node_id="norm-xyz",
            value=True,
        )
        assert fact.value is True

    def test_model_dump(self) -> None:
        fact = InferredFact(
            workspace_id="ws-1",
            tenant_id="tenant-1",
            predicate="TEST_PREDICATE",
            subject_node_id="node-1",
        )
        data = fact.model_dump()
        assert data["node_type"] == "InferredFact"
        assert data["predicate"] == "TEST_PREDICATE"

    def test_import_from_dialectica_ontology(self) -> None:
        """Ensure top-level import works as specified."""
        from dialectica_ontology import InferredFact as IF  # noqa: N814
        from dialectica_ontology import ReasoningTrace as RT  # noqa: N814

        assert RT is ReasoningTrace
        assert IF is InferredFact


# ---------------------------------------------------------------------------
# 2. write_reasoning_trace with mocked Neo4j client
# ---------------------------------------------------------------------------


class TestWriteReasoningTrace:
    @pytest.mark.asyncio
    async def test_write_calls_graph_client(self) -> None:
        mock_gc = MagicMock()
        mock_gc.write_reasoning_trace = AsyncMock(return_value="trace-001")

        from dialectica_reasoning.symbolic.firewall import SymbolicFirewall

        trace = ReasoningTrace(
            id="trace-001",
            workspace_id="ws-1",
            tenant_id="t-1",
            rules_fired=["rule_x"],
            conclusion="Treaty violated",
        )
        fact = InferredFact(
            workspace_id="ws-1",
            tenant_id="t-1",
            predicate="TREATY_VIOLATION",
            subject_node_id="norm-1",
            trace_id="trace-001",
        )

        returned_id = await SymbolicFirewall.write_trace_to_graph(
            trace_data=trace.model_dump(),
            graph_client=mock_gc,
            inferred_facts=[fact.model_dump()],
        )

        assert returned_id == "trace-001"
        mock_gc.write_reasoning_trace.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_write_graceful_degradation_no_method(self) -> None:
        """write_trace_to_graph should not raise if graph_client lacks the method."""

        class MinimalMockGC:
            pass

        from dialectica_reasoning.symbolic.firewall import SymbolicFirewall

        trace_data = {
            "id": "trace-noop",
            "workspace_id": "ws-1",
            "tenant_id": "t-1",
        }
        returned_id = await SymbolicFirewall.write_trace_to_graph(
            trace_data=trace_data,
            graph_client=MinimalMockGC(),  # type: ignore[arg-type]
        )
        assert returned_id == "trace-noop"

    @pytest.mark.asyncio
    async def test_write_empty_facts(self) -> None:
        mock_gc = MagicMock()
        mock_gc.write_reasoning_trace = AsyncMock(return_value="trace-002")

        from dialectica_reasoning.symbolic.firewall import SymbolicFirewall

        trace_data = {
            "id": "trace-002",
            "workspace_id": "ws-2",
            "tenant_id": "t-2",
        }
        returned_id = await SymbolicFirewall.write_trace_to_graph(
            trace_data=trace_data,
            graph_client=mock_gc,
            inferred_facts=[],
        )
        assert returned_id == "trace-002"
        # Called with empty list for facts
        call_args = mock_gc.write_reasoning_trace.call_args
        assert call_args.args[1] == [] or call_args.kwargs.get("inferred_facts", []) == []


# ---------------------------------------------------------------------------
# 3. EscalationDetector.write_back
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_escalation_write_back_calls_graph() -> None:
    from dialectica_reasoning.symbolic.escalation import EscalationDetector, GlaslAssessment

    mock_gc = MagicMock()
    mock_gc.get_nodes = AsyncMock(return_value=[])
    mock_gc.get_edges = AsyncMock(return_value=[])
    mock_gc.write_reasoning_trace = AsyncMock(return_value="trace-esc-001")

    detector = EscalationDetector(mock_gc)
    assessment = GlaslAssessment(
        stage=__import__(
            "dialectica_ontology.enums", fromlist=["GlaslStage"]
        ).GlaslStage.HARDENING,
        level="win_win",
        confidence=0.6,
        evidence=["conflict-1"],
        intervention_type="moderation",
    )

    trace_id = await detector.write_back(
        workspace_id="ws-test",
        tenant_id="t-test",
        assessment=assessment,
    )

    assert isinstance(trace_id, str) and len(trace_id) > 0
    mock_gc.write_reasoning_trace.assert_awaited_once()
    # First positional arg is the trace dict; second is the list of facts
    call_args = mock_gc.write_reasoning_trace.call_args
    trace_dict = call_args.args[0]
    facts_list = call_args.args[1]
    assert trace_dict["workspace_id"] == "ws-test"
    assert "glasl_stage_derivation" in trace_dict["rules_fired"]
    assert len(facts_list) == 1
    assert facts_list[0]["predicate"] == "GLASL_STAGE"


@pytest.mark.asyncio
async def test_escalation_write_back_no_method() -> None:
    """write_back should not raise if graph client has no write_reasoning_trace."""

    class LegacyMockGC:
        async def get_nodes(self, *a: Any, **kw: Any) -> list:
            return []

        async def get_edges(self, *a: Any, **kw: Any) -> list:
            return []

    from dialectica_reasoning.symbolic.escalation import EscalationDetector, GlaslAssessment
    from dialectica_ontology.enums import GlaslStage

    detector = EscalationDetector(LegacyMockGC())  # type: ignore[arg-type]
    assessment = GlaslAssessment(
        stage=GlaslStage.HARDENING,
        level="win_win",
        confidence=0.3,
        evidence=[],
        intervention_type="moderation",
    )
    trace_id = await detector.write_back("ws-1", "t-1", assessment)
    # Should return a generated ULID without raising
    assert isinstance(trace_id, str) and len(trace_id) > 0


# ---------------------------------------------------------------------------
# 4. NODE_TYPES registry includes new types
# ---------------------------------------------------------------------------


def test_node_types_registry_includes_new_types() -> None:
    from dialectica_ontology.primitives import NODE_TYPES

    assert "ReasoningTrace" in NODE_TYPES
    assert "InferredFact" in NODE_TYPES
    assert NODE_TYPES["ReasoningTrace"] is ReasoningTrace
    assert NODE_TYPES["InferredFact"] is InferredFact
