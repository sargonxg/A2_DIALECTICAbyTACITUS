"""
Instructor Extractors — Pydantic-validated structured extraction using Instructor + LiteLLM.

Replaces raw Gemini API calls with Instructor for automatic validation,
retry on schema errors, and provider-agnostic model access via LiteLLM.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from pydantic import BaseModel, Field

from dialectica_ontology.primitives import ConflictNode, Actor, Conflict, Event
from dialectica_ontology.relationships import ConflictRelationship, EdgeType
from dialectica_ontology.tiers import OntologyTier, TIER_NODES, TIER_EDGES

from dialectica_extraction.prompts.system import build_system_prompt

logger = logging.getLogger(__name__)

# Model configuration
DEFAULT_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini/gemini-2.5-flash-001")
COMPLEX_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini/gemini-2.5-pro-001")
MAX_RETRIES = 3


# ── Response Models ───────────────────────────────────────────────────────


class ExtractedEntity(BaseModel):
    """A single extracted entity from text."""

    label: str = Field(description="Node type: Actor, Conflict, Event, Issue, etc.")
    name: str = Field(default="", description="Entity name")
    description: str = Field(default="", description="Brief description")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    properties: dict[str, Any] = Field(
        default_factory=dict,
        description="Type-specific properties (actor_type, scale, domain, etc.)",
    )


class EntityExtractionResult(BaseModel):
    """Batch result of entity extraction."""

    entities: list[ExtractedEntity] = Field(default_factory=list)


class ExtractedRelationship(BaseModel):
    """A single extracted relationship between entities."""

    type: str = Field(description="Edge type: PARTY_TO, CAUSED, ALLIED_WITH, etc.")
    source_name: str = Field(description="Name of the source entity")
    target_name: str = Field(description="Name of the target entity")
    source_label: str = Field(description="Label of source entity")
    target_label: str = Field(description="Label of target entity")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    properties: dict[str, Any] = Field(default_factory=dict)


class RelationshipExtractionResult(BaseModel):
    """Batch result of relationship extraction."""

    relationships: list[ExtractedRelationship] = Field(default_factory=list)


# ── Extractor Functions ───────────────────────────────────────────────────


def _get_instructor_client() -> Any:
    """Create an Instructor client backed by LiteLLM."""
    try:
        import instructor
        import litellm

        return instructor.from_litellm(litellm.completion)
    except ImportError:
        raise ImportError(
            "instructor and litellm packages required. "
            "Install with: pip install instructor litellm"
        )


def extract_conflict_entities(
    text: str,
    tier: OntologyTier = OntologyTier.ESSENTIAL,
    model: str | None = None,
) -> list[dict]:
    """Extract conflict entities from text using Instructor + LiteLLM.

    Uses Pydantic-validated structured output with automatic retries
    on validation failures.

    Args:
        text: Source text to extract entities from.
        tier: Ontology tier controlling which entity types are allowed.
        model: LiteLLM model string (default: Gemini Flash).

    Returns:
        List of raw entity dicts ready for schema validation.
    """
    client = _get_instructor_client()
    model_id = model or DEFAULT_MODEL

    system_prompt = build_system_prompt(tier)
    available_types = [t.__name__ if not isinstance(t, str) else t for t in TIER_NODES.get(tier, [])]

    user_prompt = (
        f"Extract all conflict-relevant entities from the following text.\n"
        f"Allowed entity types for {tier.value} tier: {', '.join(available_types)}\n\n"
        f"Text:\n{text}"
    )

    try:
        result = client(
            model=model_id,
            response_model=EntityExtractionResult,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_retries=MAX_RETRIES,
        )

        entities: list[dict] = []
        for entity in result.entities:
            raw = {
                "label": entity.label,
                "name": entity.name,
                "description": entity.description,
                "confidence": entity.confidence,
                **entity.properties,
            }
            entities.append(raw)

        logger.info("Extracted %d entities (tier=%s)", len(entities), tier.value)
        return entities

    except Exception as e:
        logger.error("Instructor entity extraction failed: %s", e)
        return []


def extract_conflict_relationships(
    nodes: list[dict],
    text: str,
    tier: OntologyTier = OntologyTier.ESSENTIAL,
    model: str | None = None,
) -> list[dict]:
    """Extract relationships between known entities using Instructor + LiteLLM.

    Args:
        nodes: List of extracted entity dicts (with name, label, id).
        text: Original source text for context.
        tier: Ontology tier controlling allowed edge types.
        model: LiteLLM model string.

    Returns:
        List of raw edge dicts ready for schema validation.
    """
    if not nodes:
        return []

    client = _get_instructor_client()
    model_id = model or DEFAULT_MODEL

    available_edges = [e.value for e in TIER_EDGES.get(tier, [])]
    entity_list = "\n".join(
        f"- {n.get('name', 'unknown')} ({n.get('label', 'unknown')}, id={n.get('id', '')})"
        for n in nodes
    )

    user_prompt = (
        f"Given these entities:\n{entity_list}\n\n"
        f"And this text:\n{text[:3000]}\n\n"
        f"Extract all relationships between entities.\n"
        f"Allowed relationship types: {', '.join(available_edges)}"
    )

    try:
        result = client(
            model=model_id,
            response_model=RelationshipExtractionResult,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            max_retries=MAX_RETRIES,
        )

        # Map names to IDs
        name_to_id: dict[str, str] = {}
        for n in nodes:
            name = n.get("name", "")
            nid = n.get("id", "")
            if name and nid:
                name_to_id[name.lower()] = nid

        edges: list[dict] = []
        for rel in result.relationships:
            src_id = name_to_id.get(rel.source_name.lower(), rel.source_name)
            tgt_id = name_to_id.get(rel.target_name.lower(), rel.target_name)

            raw = {
                "type": rel.type,
                "source_id": src_id,
                "target_id": tgt_id,
                "source_label": rel.source_label,
                "target_label": rel.target_label,
                "confidence": rel.confidence,
                **rel.properties,
            }
            edges.append(raw)

        logger.info("Extracted %d relationships (tier=%s)", len(edges), tier.value)
        return edges

    except Exception as e:
        logger.error("Instructor relationship extraction failed: %s", e)
        return []
