"""Link Predictor — Given (Actor, LEVERAGES, ?) predict missing targets."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """A predicted link with score."""
    target_id: str
    target_label: str
    relation: str
    score: float


class LinkPredictor:
    """Predict missing links in the conflict knowledge graph.

    Uses a trained PyKEEN model for (head, relation, ?) prediction.
    """

    def __init__(self, pipeline_result: Any) -> None:
        self._result = pipeline_result

    def predict_tails(
        self,
        head: str,
        relation: str,
        top_k: int = 10,
    ) -> list[PredictionResult]:
        """Predict tail entities for (head, relation, ?).

        Args:
            head: Head entity label/ID.
            relation: Relation type string.
            top_k: Number of predictions to return.

        Returns:
            Ranked list of PredictionResult.
        """
        try:
            model = self._result.model
            factory = self._result.training

            predictions = model.get_tail_prediction_df(
                head_label=head,
                relation_label=relation,
                triples_factory=factory,
            )

            results: list[PredictionResult] = []
            for _, row in predictions.head(top_k).iterrows():
                results.append(PredictionResult(
                    target_id=str(row.get("tail_label", "")),
                    target_label=str(row.get("tail_label", "")),
                    relation=relation,
                    score=float(row.get("score", 0)),
                ))
            return results
        except Exception as e:
            logger.error("Link prediction failed: %s", e)
            return []

    def predict_heads(
        self,
        relation: str,
        tail: str,
        top_k: int = 10,
    ) -> list[PredictionResult]:
        """Predict head entities for (?, relation, tail)."""
        try:
            model = self._result.model
            factory = self._result.training

            predictions = model.get_head_prediction_df(
                tail_label=tail,
                relation_label=relation,
                triples_factory=factory,
            )

            results: list[PredictionResult] = []
            for _, row in predictions.head(top_k).iterrows():
                results.append(PredictionResult(
                    target_id=str(row.get("head_label", "")),
                    target_label=str(row.get("head_label", "")),
                    relation=relation,
                    score=float(row.get("score", 0)),
                ))
            return results
        except Exception as e:
            logger.error("Head prediction failed: %s", e)
            return []
