"""
Tests for SymbolicFirewall — deterministic conclusions block contradicting
probabilistic predictions, non-contradicting predictions pass through,
and deterministic conclusions always have confidence=1.0.
"""
from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_ontology.confidence import Conclusion, ConfidenceType
from dialectica_reasoning.symbolic.firewall import SymbolicFirewall


# ═══════════════════════════════════════════════════════════════════════════
#  CONCLUSION MODEL TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestConclusionModel:
    def test_deterministic_requires_source_rule(self):
        with pytest.raises(ValueError, match="source_rule"):
            Conclusion(
                conclusion_type=ConfidenceType.DETERMINISTIC,
                statement="Treaty violated",
                confidence=0.9,
                workspace_id="ws-1",
            )

    def test_deterministic_forces_confidence_1(self):
        c = Conclusion(
            conclusion_type=ConfidenceType.DETERMINISTIC,
            statement="Treaty violated",
            confidence=0.5,  # Will be overridden to 1.0
            source_rule="treaty_article_7",
            workspace_id="ws-1",
        )
        assert c.confidence == 1.0

    def test_probabilistic_keeps_confidence(self):
        c = Conclusion(
            conclusion_type=ConfidenceType.PROBABILISTIC,
            statement="Likely escalating",
            confidence=0.72,
            source_model="compgcn-v1.2",
            workspace_id="ws-1",
        )
        assert c.confidence == 0.72

    def test_conclusion_has_id(self):
        c = Conclusion(
            conclusion_type=ConfidenceType.PROBABILISTIC,
            statement="Test",
            confidence=0.5,
        )
        assert c.conclusion_id  # Auto-generated ULID


# ═══════════════════════════════════════════════════════════════════════════
#  FIREWALL BLOCKING TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestFirewallBlocking:
    def test_blocks_contradicting_prediction(self):
        """Deterministic 'violated' blocks probabilistic 'compliant'."""
        det = Conclusion(
            conclusion_type=ConfidenceType.DETERMINISTIC,
            statement="Treaty Article 7 violated by State A",
            confidence=1.0,
            source_rule="treaty_article_7_check",
            workspace_id="ws-1",
        )
        firewall = SymbolicFirewall([det])

        pred = Conclusion(
            conclusion_type=ConfidenceType.PROBABILISTIC,
            statement="State A is compliant with Treaty Article 7",
            confidence=0.85,
            source_model="gnn-v2",
            workspace_id="ws-1",
        )

        result = firewall.check_neural_prediction(pred)
        assert result is None  # Blocked

    def test_blocks_escalation_contradiction(self):
        """Deterministic 'escalating' blocks probabilistic 'de-escalating'."""
        det = Conclusion(
            conclusion_type=ConfidenceType.DETERMINISTIC,
            statement="Conflict is escalating per Glasl stage assessment",
            confidence=1.0,
            source_rule="glasl_escalation_stage_6_to_7",
            workspace_id="ws-1",
        )
        firewall = SymbolicFirewall([det])

        pred = Conclusion(
            conclusion_type=ConfidenceType.PROBABILISTIC,
            statement="Conflict is de-escalating based on sentiment trends",
            confidence=0.65,
            source_model="sentiment-lstm",
            workspace_id="ws-1",
        )

        assert firewall.check_neural_prediction(pred) is None

    def test_passes_non_contradicting_prediction(self):
        """Non-contradicting probabilistic predictions pass through."""
        det = Conclusion(
            conclusion_type=ConfidenceType.DETERMINISTIC,
            statement="Treaty Article 7 violated",
            confidence=1.0,
            source_rule="treaty_article_7_check",
            workspace_id="ws-1",
        )
        firewall = SymbolicFirewall([det])

        pred = Conclusion(
            conclusion_type=ConfidenceType.PROBABILISTIC,
            statement="Actor B likely to seek mediation",
            confidence=0.75,
            source_model="forecaster-v3",
            workspace_id="ws-1",
        )

        result = firewall.check_neural_prediction(pred)
        assert result is not None
        assert result.statement == "Actor B likely to seek mediation"

    def test_passes_different_workspace(self):
        """Predictions in different workspaces don't contradict."""
        det = Conclusion(
            conclusion_type=ConfidenceType.DETERMINISTIC,
            statement="Treaty violated",
            confidence=1.0,
            source_rule="rule-1",
            workspace_id="ws-1",
        )
        firewall = SymbolicFirewall([det])

        pred = Conclusion(
            conclusion_type=ConfidenceType.PROBABILISTIC,
            statement="Treaty is compliant",
            confidence=0.9,
            source_model="model-1",
            workspace_id="ws-2",  # Different workspace
        )

        result = firewall.check_neural_prediction(pred)
        assert result is not None  # Passes because different workspace

    def test_deterministic_always_passes(self):
        """Deterministic conclusions always pass the firewall."""
        det = Conclusion(
            conclusion_type=ConfidenceType.DETERMINISTIC,
            statement="Treaty violated",
            confidence=1.0,
            source_rule="rule-1",
            workspace_id="ws-1",
        )
        firewall = SymbolicFirewall([det])

        another_det = Conclusion(
            conclusion_type=ConfidenceType.DETERMINISTIC,
            statement="Another deterministic fact",
            confidence=1.0,
            source_rule="rule-2",
            workspace_id="ws-1",
        )

        result = firewall.check_neural_prediction(another_det)
        assert result is not None


# ═══════════════════════════════════════════════════════════════════════════
#  MERGE TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestMergeConclusions:
    def test_merge_with_no_contradictions(self):
        symbolic = [
            Conclusion(
                conclusion_type=ConfidenceType.DETERMINISTIC,
                statement="Treaty violated",
                confidence=1.0,
                source_rule="rule-1",
                workspace_id="ws-1",
            ),
        ]
        neural = [
            Conclusion(
                conclusion_type=ConfidenceType.PROBABILISTIC,
                statement="Actor B likely to seek mediation",
                confidence=0.75,
                source_model="model-1",
                workspace_id="ws-1",
            ),
        ]

        firewall = SymbolicFirewall(symbolic)
        merged = firewall.merge_conclusions(symbolic, neural)
        assert len(merged) == 2

    def test_merge_filters_contradictions(self):
        symbolic = [
            Conclusion(
                conclusion_type=ConfidenceType.DETERMINISTIC,
                statement="Treaty violated",
                confidence=1.0,
                source_rule="rule-1",
                workspace_id="ws-1",
            ),
        ]
        neural = [
            Conclusion(
                conclusion_type=ConfidenceType.PROBABILISTIC,
                statement="Treaty is compliant",
                confidence=0.85,
                source_model="model-1",
                workspace_id="ws-1",
            ),
            Conclusion(
                conclusion_type=ConfidenceType.PROBABILISTIC,
                statement="Mediation likely",
                confidence=0.6,
                source_model="model-2",
                workspace_id="ws-1",
            ),
        ]

        firewall = SymbolicFirewall(symbolic)
        merged = firewall.merge_conclusions(symbolic, neural)
        # 1 symbolic + 1 non-contradicting neural = 2
        assert len(merged) == 2
        statements = [c.statement for c in merged]
        assert "Treaty violated" in statements
        assert "Mediation likely" in statements
        assert "Treaty is compliant" not in statements

    def test_merge_deterministic_first(self):
        symbolic = [
            Conclusion(
                conclusion_type=ConfidenceType.DETERMINISTIC,
                statement="Rule-based fact",
                confidence=1.0,
                source_rule="rule-1",
                workspace_id="ws-1",
            ),
        ]
        neural = [
            Conclusion(
                conclusion_type=ConfidenceType.PROBABILISTIC,
                statement="Neural prediction",
                confidence=0.7,
                source_model="model-1",
                workspace_id="ws-1",
            ),
        ]

        firewall = SymbolicFirewall()
        merged = firewall.merge_conclusions(symbolic, neural)
        assert merged[0].conclusion_type == ConfidenceType.DETERMINISTIC

    def test_merge_empty_inputs(self):
        firewall = SymbolicFirewall()
        merged = firewall.merge_conclusions([], [])
        assert merged == []


# ═══════════════════════════════════════════════════════════════════════════
#  FIREWALL CONSTRUCTION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestFirewallConstruction:
    def test_rejects_probabilistic_in_constructor(self):
        prob = Conclusion(
            conclusion_type=ConfidenceType.PROBABILISTIC,
            statement="Test",
            confidence=0.5,
            source_model="model",
        )
        with pytest.raises(ValueError, match="deterministic"):
            SymbolicFirewall([prob])

    def test_add_deterministic(self):
        firewall = SymbolicFirewall()
        det = Conclusion(
            conclusion_type=ConfidenceType.DETERMINISTIC,
            statement="Fact",
            confidence=1.0,
            source_rule="rule-1",
        )
        firewall.add_deterministic(det)
        assert len(firewall._deterministic) == 1

    def test_add_probabilistic_raises(self):
        firewall = SymbolicFirewall()
        prob = Conclusion(
            conclusion_type=ConfidenceType.PROBABILISTIC,
            statement="Guess",
            confidence=0.5,
            source_model="model",
        )
        with pytest.raises(ValueError, match="deterministic"):
            firewall.add_deterministic(prob)
