"""
Gemini Extractor — Vertex AI Gemini integration for conflict entity extraction.

Uses structured JSON output mode with tier-appropriate prompts.
Primary model: gemini-2.5-flash-001, complex: gemini-2.5-pro-001.
Supports LiteLLM as an alternative backend for provider-agnostic access.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from dialectica_extraction.prompts.extraction_essential import EXTRACTION_ESSENTIAL_PROMPT
from dialectica_extraction.prompts.extraction_full import EXTRACTION_FULL_PROMPT
from dialectica_extraction.prompts.extraction_standard import EXTRACTION_STANDARD_PROMPT
from dialectica_extraction.prompts.relationship import RELATIONSHIP_PROMPT
from dialectica_extraction.prompts.system import build_system_prompt
from dialectica_ontology.tiers import OntologyTier

logger = logging.getLogger(__name__)

FLASH_MODEL = "gemini-2.5-flash-001"
PRO_MODEL = "gemini-2.5-pro-001"

_TIER_PROMPTS = {
    OntologyTier.ESSENTIAL: EXTRACTION_ESSENTIAL_PROMPT,
    OntologyTier.STANDARD: EXTRACTION_STANDARD_PROMPT,
    OntologyTier.FULL: EXTRACTION_FULL_PROMPT,
}


@dataclass
class ExtractionMetrics:
    """Metrics for a Gemini extraction call."""

    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    model: str = ""
    retries: int = 0


@dataclass
class GeminiExtractionResult:
    """Result of a Gemini extraction call."""

    raw_nodes: list[dict] = field(default_factory=list)
    raw_edges: list[dict] = field(default_factory=list)
    metrics: ExtractionMetrics = field(default_factory=ExtractionMetrics)
    error: str | None = None


class GeminiExtractor:
    """Wraps Vertex AI Gemini for structured conflict entity extraction.

    Args:
        project_id: GCP project ID.
        location: GCP region.
        flash_model: Model ID for fast extraction.
        pro_model: Model ID for complex extraction.
        max_retries: Max retries on transient failures.
    """

    def __init__(
        self,
        project_id: str | None = None,
        location: str = "us-east1",
        flash_model: str = FLASH_MODEL,
        pro_model: str = PRO_MODEL,
        max_retries: int = 3,
    ) -> None:
        self._project_id = project_id
        self._location = location
        self._flash_model_id = flash_model
        self._pro_model_id = pro_model
        self._max_retries = max_retries
        self._model: Any = None

    def _init_model(self, model_id: str | None = None) -> Any:
        """Lazy-init Vertex AI GenerativeModel."""
        mid = model_id or self._flash_model_id
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel

            if self._project_id:
                vertexai.init(project=self._project_id, location=self._location)
            return GenerativeModel(mid)
        except Exception as e:
            logger.error("Failed to initialize Gemini model %s: %s", mid, e)
            return None

    def _call_gemini(
        self,
        prompt: str,
        system_prompt: str,
        model_id: str | None = None,
    ) -> tuple[dict | None, ExtractionMetrics]:
        """Call Gemini with structured JSON output."""
        metrics = ExtractionMetrics(model=model_id or self._flash_model_id)
        model = self._init_model(model_id)
        if model is None:
            return None, metrics

        from vertexai.generative_models import GenerationConfig

        config = GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1,
            max_output_tokens=8192,
        )

        for attempt in range(self._max_retries):
            try:
                start = time.time()
                response = model.generate_content(
                    [system_prompt, prompt],
                    generation_config=config,
                )
                metrics.latency_ms = (time.time() - start) * 1000

                if hasattr(response, "usage_metadata"):
                    um = response.usage_metadata
                    metrics.input_tokens = getattr(um, "prompt_token_count", 0)
                    metrics.output_tokens = getattr(um, "candidates_token_count", 0)

                text = response.text.strip()
                return json.loads(text), metrics

            except json.JSONDecodeError as e:
                logger.warning("Gemini JSON parse error (attempt %d): %s", attempt + 1, e)
                metrics.retries = attempt + 1
            except Exception as e:
                logger.warning("Gemini call error (attempt %d): %s", attempt + 1, e)
                metrics.retries = attempt + 1
                if attempt < self._max_retries - 1:
                    time.sleep(2**attempt)

        return None, metrics

    def extract_entities(
        self,
        text: str,
        tier: OntologyTier,
    ) -> GeminiExtractionResult:
        """Extract entities from text using tier-appropriate prompt.

        Args:
            text: Source text to extract from.
            tier: Ontology tier determining which node types to extract.

        Returns:
            GeminiExtractionResult with raw_nodes and metrics.
        """
        system_prompt = build_system_prompt(tier)
        extraction_prompt = _TIER_PROMPTS[tier] + text

        result_dict, metrics = self._call_gemini(extraction_prompt, system_prompt)

        if result_dict is None:
            return GeminiExtractionResult(
                metrics=metrics,
                error="Gemini extraction failed after retries",
            )

        raw_nodes = result_dict.get("nodes", [])
        return GeminiExtractionResult(raw_nodes=raw_nodes, metrics=metrics)

    def extract_relationships(
        self,
        entities: list[dict],
        text: str,
        tier: OntologyTier,
    ) -> GeminiExtractionResult:
        """Extract relationships given validated entities and source text.

        Args:
            entities: List of validated entity dicts with IDs.
            text: Original source text.
            tier: Ontology tier.

        Returns:
            GeminiExtractionResult with raw_edges and metrics.
        """
        system_prompt = build_system_prompt(tier)
        entities_json = json.dumps(entities, indent=2, default=str)
        prompt = RELATIONSHIP_PROMPT.format(entities_json=entities_json, text=text)

        result_dict, metrics = self._call_gemini(prompt, system_prompt)

        if result_dict is None:
            return GeminiExtractionResult(
                metrics=metrics,
                error="Gemini relationship extraction failed",
            )

        raw_edges = result_dict.get("edges", [])
        return GeminiExtractionResult(raw_edges=raw_edges, metrics=metrics)

    def repair_entities(
        self,
        entities: list[dict],
        errors: list[str],
        tier: OntologyTier,
    ) -> GeminiExtractionResult:
        """Repair invalid entities by sending errors back to Gemini.

        Args:
            entities: Invalid entity dicts.
            errors: Validation error messages.
            tier: Ontology tier.

        Returns:
            GeminiExtractionResult with corrected raw_nodes.
        """
        system_prompt = build_system_prompt(tier)
        repair_prompt = (
            "The following entities failed schema validation. "
            "Please fix them and return valid JSON.\n\n"
            f"Entities:\n{json.dumps(entities, indent=2, default=str)}\n\n"
            f"Errors:\n" + "\n".join(f"- {e}" for e in errors) + "\n\n"
            'Return: {"nodes": [...]}'
        )

        result_dict, metrics = self._call_gemini(repair_prompt, system_prompt)

        if result_dict is None:
            return GeminiExtractionResult(
                metrics=metrics,
                error="Gemini repair failed",
            )

        raw_nodes = result_dict.get("nodes", [])
        return GeminiExtractionResult(raw_nodes=raw_nodes, metrics=metrics)
