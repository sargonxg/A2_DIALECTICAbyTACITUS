"""
GLiNER Pre-filter — Zero-shot NER for conflict entity-dense passage selection.

Uses GLiNER for entity detection if available; falls back to keyword detection.
Scores chunks by entity density to prioritize entity-rich passages for Gemini.
"""
from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

try:
    import gliner  # noqa: F401

    GLINER_AVAILABLE = True
except ImportError:
    GLINER_AVAILABLE = False
    logger.info(
        "GLiNER not installed — keyword fallback will be used. "
        "Install with: pip install dialectica-extraction[gliner]"
    )

# Conflict-specific entity labels for GLiNER
GLINER_LABELS = [
    "conflict actor",
    "political event",
    "conflict event",
    "stated interest",
    "claim or demand",
    "norm or law",
    "emotional state",
    "narrative frame",
    "power relationship",
    "trust indicator",
    "conflict process",
    "evidence source",
    "geographic location",
    "agreement or outcome",
]

# Keyword fallback — simplified conflict entity detection
CONFLICT_KEYWORDS = [
    # Actors
    r"\b(?:president|minister|government|opposition|rebel|militia|UN|NATO|EU)\b",
    r"\b(?:mediator|arbitrator|negotiator|representative|delegate|ambassador)\b",
    # Events
    r"\b(?:attack|protest|negotiation|ceasefire|election|summit|conference)\b",
    r"\b(?:agreement|treaty|resolution|sanctions|embargo)\b",
    # Conflict terms
    r"\b(?:conflict|dispute|war|crisis|tension|escalation|violence|hostility)\b",
    r"\b(?:mediation|arbitration|reconciliation|settlement|peace)\b",
    # Emotions
    r"\b(?:anger|fear|frustration|trust|distrust|hostility|resentment)\b",
    # Locations
    r"\b(?:border|territory|region|capital|province|district)\b",
]
_KEYWORD_PATTERN = re.compile("|".join(CONFLICT_KEYWORDS), re.IGNORECASE)


@dataclass
class PrefilterEntity:
    """An entity detected during pre-filtering."""

    text: str
    label: str
    start: int
    end: int
    score: float = 0.0


@dataclass
class PrefilterResult:
    """Result of pre-filtering a text chunk."""

    chunk_index: int
    chunk_text: str
    entities: list[PrefilterEntity] = field(default_factory=list)
    entity_density: float = 0.0  # entities per 100 words
    priority_score: float = 0.0

    @property
    def entity_count(self) -> int:
        return len(self.entities)


class GLiNERPreFilter:
    """Pre-filter text chunks using GLiNER zero-shot NER.

    Falls back to keyword detection if GLiNER is not available.
    """

    def __init__(self, model_name: str = "gliner-community/gliner_medium-v2.5") -> None:
        self._model_name = model_name
        self._model: Any = None
        self._gliner_available = self._check_gliner_enabled()

    def _check_gliner_enabled(self) -> bool:
        """Check if GLiNER should be used."""
        if not GLINER_AVAILABLE:
            return False
        if os.environ.get("GLINER_ENABLED", "true").lower() == "false":
            logger.info("GLiNER disabled via GLINER_ENABLED=false")
            return False
        return True

    def _init_model(self) -> bool:
        """Lazy-init GLiNER model."""
        if self._model is not None:
            return True
        if not self._gliner_available:
            return False
        try:
            from gliner import GLiNER

            self._model = GLiNER.from_pretrained(self._model_name)
            logger.info("Loaded GLiNER model: %s", self._model_name)
            return True
        except Exception as e:
            logger.warning("GLiNER not available: %s (using keyword fallback)", e)
            self._gliner_available = False
            return False

    def prefilter(
        self,
        chunks: list[str],
        threshold: float = 0.3,
        min_entities: int = 1,
    ) -> list[PrefilterResult]:
        """Pre-filter chunks by entity density.

        Args:
            chunks: Text chunks to analyze.
            threshold: Minimum entity density score to pass.
            min_entities: Minimum entity count to pass.

        Returns:
            List of PrefilterResult for all chunks (with scores).
        """
        results = []
        for i, chunk in enumerate(chunks):
            if self._init_model():
                result = self._gliner_prefilter(i, chunk)
            else:
                result = self._keyword_prefilter(i, chunk)
            results.append(result)

        # Assign priority scores (normalize to 0-1)
        max_density = max((r.entity_density for r in results), default=1.0) or 1.0
        for r in results:
            r.priority_score = r.entity_density / max_density

        return results

    def _gliner_prefilter(self, index: int, text: str) -> PrefilterResult:
        """Pre-filter using GLiNER model."""
        entities_raw = self._model.predict_entities(text, GLINER_LABELS, threshold=0.3)
        entities = [
            PrefilterEntity(
                text=e["text"],
                label=e["label"],
                start=e["start"],
                end=e["end"],
                score=e.get("score", 0.5),
            )
            for e in entities_raw
        ]
        word_count = max(len(text.split()), 1)
        density = len(entities) / word_count * 100

        return PrefilterResult(
            chunk_index=index,
            chunk_text=text,
            entities=entities,
            entity_density=density,
        )

    def _keyword_prefilter(self, index: int, text: str) -> PrefilterResult:
        """Fallback: pre-filter using keyword matching."""
        entities = []
        for match in _KEYWORD_PATTERN.finditer(text):
            entities.append(PrefilterEntity(
                text=match.group(),
                label="keyword_match",
                start=match.start(),
                end=match.end(),
                score=0.5,
            ))

        word_count = max(len(text.split()), 1)
        density = len(entities) / word_count * 100

        return PrefilterResult(
            chunk_index=index,
            chunk_text=text,
            entities=entities,
            entity_density=density,
        )

    def get_priority_chunks(
        self,
        results: list[PrefilterResult],
        min_score: float = 0.3,
    ) -> list[PrefilterResult]:
        """Return chunks ordered by priority score, filtered by minimum."""
        filtered = [r for r in results if r.priority_score >= min_score]
        return sorted(filtered, key=lambda r: r.priority_score, reverse=True)
