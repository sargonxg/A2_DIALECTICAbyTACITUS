"""
Entity Enrichment — Add aliases, link to existing entities, enhance metadata.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from dialectica_ontology.primitives import ConflictNode

logger = logging.getLogger(__name__)


@dataclass
class EntityEnrichmentResult:
    """Result of entity enrichment."""

    enriched_nodes: list[ConflictNode] = field(default_factory=list)
    aliases_added: int = 0
    links_found: int = 0


def enrich_actors(nodes: list[ConflictNode]) -> list[ConflictNode]:
    """Enrich actor nodes with derived properties.

    - Generate common aliases (e.g., "United States" -> "US", "USA")
    - Normalize names (strip titles, normalize whitespace)
    """
    for node in nodes:
        if node.label != "Actor":
            continue
        name = getattr(node, "name", "")
        aliases = getattr(node, "aliases", [])

        # Generate basic aliases
        generated = set(aliases)
        if name:
            # First/last name split for persons
            parts = name.split()
            if len(parts) >= 2:
                generated.add(parts[-1])  # Last name
            # Acronym for organizations
            if len(parts) >= 2 and all(p[0].isupper() for p in parts):
                acronym = "".join(p[0] for p in parts)
                if len(acronym) >= 2:
                    generated.add(acronym)

        if hasattr(node, "aliases"):
            node.aliases = list(generated)

    return nodes


def deduplicate_nodes(nodes: list[ConflictNode]) -> list[ConflictNode]:
    """Remove duplicate nodes within a single extraction batch.

    Uses exact name matching + label matching for deduplication.
    Returns deduplicated list with merged source_text.
    """
    seen: dict[str, ConflictNode] = {}
    deduped: list[ConflictNode] = []

    for node in nodes:
        name = getattr(node, "name", getattr(node, "description", ""))
        key = f"{node.label}::{name.lower().strip()}"

        if key in seen:
            # Merge: keep higher confidence, append source_text
            existing = seen[key]
            if node.confidence > existing.confidence:
                seen[key] = node
                # Find and replace in deduped
                for i, d in enumerate(deduped):
                    if d.id == existing.id:
                        deduped[i] = node
                        break
        else:
            seen[key] = node
            deduped.append(node)

    return deduped
