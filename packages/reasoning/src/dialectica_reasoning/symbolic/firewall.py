"""
Symbolic Firewall — Ensures deterministic conclusions are NEVER overridden
by probabilistic neural predictions.

This is the core architectural invariant of DIALECTICA: treaty violations,
legal constraints, and other rule-derived facts always take priority over
GNN/LLM predictions.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from dialectica_ontology.confidence import Conclusion, ConfidenceType

if TYPE_CHECKING:
    from dialectica_graph.interface import GraphClient

logger = logging.getLogger(__name__)


class SymbolicFirewall:
    """Guards deterministic conclusions against probabilistic overrides.

    Takes a set of deterministic (symbolic) conclusions and filters
    neural predictions that contradict them.

    Args:
        deterministic_conclusions: Pre-computed symbolic conclusions.
    """

    def __init__(self, deterministic_conclusions: Sequence[Conclusion] | None = None) -> None:
        self._deterministic: list[Conclusion] = []
        if deterministic_conclusions:
            for c in deterministic_conclusions:
                if c.conclusion_type != ConfidenceType.DETERMINISTIC:
                    raise ValueError(
                        f"SymbolicFirewall only accepts deterministic conclusions, "
                        f"got {c.conclusion_type} for conclusion {c.conclusion_id}"
                    )
                self._deterministic.append(c)

    def add_deterministic(self, conclusion: Conclusion) -> None:
        """Register a new deterministic conclusion."""
        if conclusion.conclusion_type != ConfidenceType.DETERMINISTIC:
            raise ValueError("Only deterministic conclusions can be added to the firewall")
        self._deterministic.append(conclusion)

    def check_neural_prediction(self, prediction: Conclusion) -> Conclusion | None:
        """Check if a neural prediction contradicts any deterministic conclusion.

        Args:
            prediction: A probabilistic conclusion from a neural model.

        Returns:
            The prediction if it passes, or None if it contradicts a
            deterministic conclusion.
        """
        if prediction.conclusion_type == ConfidenceType.DETERMINISTIC:
            # Deterministic conclusions always pass
            return prediction

        for det in self._deterministic:
            if self._contradicts(det, prediction):
                logger.warning(
                    "FIREWALL BLOCKED: Neural prediction '%s' (from %s, conf=%.2f) "
                    "contradicts deterministic conclusion '%s' (rule=%s). "
                    "Deterministic conclusions are never overridden.",
                    prediction.statement,
                    prediction.source_model or "unknown",
                    prediction.confidence,
                    det.statement,
                    det.source_rule,
                )
                return None

        return prediction

    def merge_conclusions(
        self,
        symbolic: list[Conclusion],
        neural: list[Conclusion],
    ) -> list[Conclusion]:
        """Merge symbolic and neural conclusions with deterministic priority.

        Deterministic conclusions are always included. Neural predictions
        are only included if they don't contradict any deterministic conclusion.

        Args:
            symbolic: Conclusions from symbolic rules (should be deterministic).
            neural: Conclusions from neural models (probabilistic).

        Returns:
            Merged list with deterministic conclusions first.
        """
        # Start with all deterministic conclusions
        merged: list[Conclusion] = []
        for c in symbolic:
            merged.append(c)
            if c.conclusion_type == ConfidenceType.DETERMINISTIC and not any(
                d.conclusion_id == c.conclusion_id for d in self._deterministic
            ):
                self._deterministic.append(c)

        # Filter neural predictions through the firewall
        accepted = 0
        rejected = 0
        for pred in neural:
            result = self.check_neural_prediction(pred)
            if result is not None:
                merged.append(result)
                accepted += 1
            else:
                rejected += 1

        if rejected > 0:
            logger.info(
                "Symbolic firewall: %d neural predictions accepted, %d rejected",
                accepted,
                rejected,
            )

        return merged

    # ── Persistence helpers ────────────────────────────────────────────────

    @staticmethod
    async def write_trace_to_graph(
        trace_data: dict[str, Any],
        graph_client: GraphClient,
        inferred_facts: list[dict[str, Any]] | None = None,
    ) -> str:
        """Write a ReasoningTrace (and optional InferredFacts) to Neo4j.

        This helper bridges the in-memory firewall computation with the
        durable graph store.  It delegates to
        ``Neo4jGraphClient.write_reasoning_trace`` when the method is
        available, falling back to a no-op that returns the trace ID so
        callers never break in test/mock environments.

        Args:
            trace_data: Property dict for the ReasoningTrace node.
                        Must contain at least ``id``, ``workspace_id``,
                        and ``tenant_id``.
            graph_client: Any GraphClient implementation (live or mock).
            inferred_facts: Optional list of InferredFact property dicts.

        Returns:
            The trace node ID.
        """
        facts = inferred_facts or []
        write_fn = getattr(graph_client, "write_reasoning_trace", None)
        if write_fn is not None:
            return await write_fn(trace_data, facts)

        # Graceful degradation: graph client does not support write-back
        logger.warning(
            "Graph client %s does not implement write_reasoning_trace — "
            "ReasoningTrace %s will NOT be persisted.",
            type(graph_client).__name__,
            trace_data.get("id", "<unknown>"),
        )
        return trace_data.get("id", "")

    @staticmethod
    def _contradicts(deterministic: Conclusion, prediction: Conclusion) -> bool:
        """Check if a prediction contradicts a deterministic conclusion.

        Two conclusions contradict if they share the same workspace and
        their statements are about the same subject but reach opposite
        conclusions. Simple heuristic: same workspace + overlapping
        subject keywords + different assertion direction.
        """
        # Must be in the same workspace to contradict
        if (
            deterministic.workspace_id
            and prediction.workspace_id
            and deterministic.workspace_id != prediction.workspace_id
        ):
            return False

        det_lower = deterministic.statement.lower()
        pred_lower = prediction.statement.lower()

        # Direct negation patterns
        negation_pairs = [
            ("violated", "compliant"),
            ("compliant", "violated"),
            ("escalating", "de-escalating"),
            ("de-escalating", "escalating"),
            ("hostile", "cooperative"),
            ("cooperative", "hostile"),
            ("breached", "upheld"),
            ("upheld", "breached"),
            ("failed", "succeeded"),
            ("succeeded", "failed"),
            ("increasing", "decreasing"),
            ("decreasing", "increasing"),
        ]

        for pos, neg in negation_pairs:
            if pos in det_lower and neg in pred_lower:
                return True

        # Check for "not" negation of the same statement
        return bool(
            det_lower.replace("not ", "") == pred_lower
            or pred_lower.replace("not ", "") == det_lower
        )
