"""
ConfliBERT Event Classifier — Fine-tuned BERT for conflict event classification.

Uses snowood1/ConfliBERT-scr-uncased for:
  - Event type classification → ACO EventType enum
  - Conflict actor NER extraction
  - Batch processing for efficiency
"""
from __future__ import annotations

import logging
from typing import Any

from dialectica_ontology.enums import EventType

logger = logging.getLogger(__name__)

MODEL_NAME = "snowood1/ConfliBERT-scr-uncased"

# ConfliBERT label → ACO EventType mapping
_CONFLIBERT_TO_ACO: dict[str, EventType] = {
    "protest": EventType.PROTEST,
    "assault": EventType.ASSAULT,
    "fight": EventType.ASSAULT,
    "agreement": EventType.AGREE,
    "cooperation": EventType.COOPERATE,
    "threat": EventType.THREATEN,
    "demand": EventType.DEMAND,
    "sanction": EventType.REDUCE_RELATIONS,
    "aid": EventType.AID,
    "consult": EventType.CONSULT,
    "disapprove": EventType.DISAPPROVE,
    "reject": EventType.REJECT,
    "coerce": EventType.COERCE,
    "yield": EventType.YIELD,
    "investigate": EventType.INVESTIGATE,
    "military": EventType.EXHIBIT_FORCE_POSTURE,
}


class ConfliBERTClassifier:
    """ConfliBERT-based event type and actor classifier.

    Lazy-loads the model on first use to avoid startup overhead.
    """

    def __init__(self, model_name: str = MODEL_NAME) -> None:
        self._model_name = model_name
        self._pipeline: Any = None
        self._ner_pipeline: Any = None

    def _init_classifier(self) -> None:
        if self._pipeline is not None:
            return
        try:
            from transformers import pipeline as hf_pipeline
            self._pipeline = hf_pipeline(
                "text-classification",
                model=self._model_name,
                top_k=3,
            )
            logger.info("Loaded ConfliBERT classifier: %s", self._model_name)
        except ImportError:
            raise ImportError("transformers not installed. pip install transformers torch")
        except Exception as e:
            logger.warning("ConfliBERT load failed: %s — using fallback", e)
            self._pipeline = None

    def _init_ner(self) -> None:
        if self._ner_pipeline is not None:
            return
        try:
            from transformers import pipeline as hf_pipeline
            self._ner_pipeline = hf_pipeline(
                "ner",
                model=self._model_name,
                aggregation_strategy="simple",
            )
        except Exception as e:
            logger.warning("ConfliBERT NER load failed: %s", e)
            self._ner_pipeline = None

    def classify_event_type(self, text: str) -> EventType:
        """Classify text into an ACO EventType.

        Args:
            text: Event description text.

        Returns:
            Most likely EventType.
        """
        self._init_classifier()
        if self._pipeline is None:
            return EventType.COERCE  # Fallback

        try:
            results = self._pipeline(text[:512])
            if results and len(results) > 0:
                top = results[0] if isinstance(results[0], dict) else results[0][0]
                label = top.get("label", "").lower()
                return _CONFLIBERT_TO_ACO.get(label, EventType.COERCE)
        except Exception as e:
            logger.warning("Classification failed: %s", e)

        return EventType.COERCE

    def classify_batch(self, texts: list[str]) -> list[EventType]:
        """Classify a batch of texts into EventTypes."""
        self._init_classifier()
        if self._pipeline is None:
            return [EventType.COERCE] * len(texts)

        try:
            truncated = [t[:512] for t in texts]
            all_results = self._pipeline(truncated)
            event_types: list[EventType] = []
            for results in all_results:
                if results:
                    top = results[0] if isinstance(results[0], dict) else results[0][0]
                    label = top.get("label", "").lower()
                    event_types.append(_CONFLIBERT_TO_ACO.get(label, EventType.COERCE))
                else:
                    event_types.append(EventType.COERCE)
            return event_types
        except Exception as e:
            logger.warning("Batch classification failed: %s", e)
            return [EventType.COERCE] * len(texts)

    def extract_conflict_actors(self, text: str) -> list[tuple[str, str]]:
        """Extract conflict-relevant actor mentions via NER.

        Returns:
            List of (entity_text, entity_type) tuples.
        """
        self._init_ner()
        if self._ner_pipeline is None:
            return []

        try:
            results = self._ner_pipeline(text[:512])
            actors: list[tuple[str, str]] = []
            for entity in results:
                label = entity.get("entity_group", "")
                word = entity.get("word", "").strip()
                if word and label in ("PER", "ORG", "GPE", "LOC", "NORP"):
                    actor_type = {
                        "PER": "person",
                        "ORG": "organization",
                        "GPE": "state",
                        "LOC": "other",
                        "NORP": "group",
                    }.get(label, "other")
                    actors.append((word, actor_type))
            return actors
        except Exception as e:
            logger.warning("NER extraction failed: %s", e)
            return []
