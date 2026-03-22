"""
Coreference Resolution — Cross-document and cross-chunk entity merging.

Uses fuzzy string matching to identify when the same entity appears
with different names/references across chunks or documents.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from dialectica_ontology.primitives import ConflictNode

logger = logging.getLogger(__name__)

# Threshold for fuzzy matching (0-1 scale)
FUZZY_THRESHOLD = 0.85


def _normalize_name(name: str) -> str:
    """Normalize a name for comparison."""
    return " ".join(name.lower().strip().split())


def _simple_token_sort_ratio(a: str, b: str) -> float:
    """Simple token-based similarity without external dependencies.

    Sorts tokens alphabetically and computes character-level similarity.
    Falls back when rapidfuzz is not available.
    """
    tokens_a = sorted(a.lower().split())
    tokens_b = sorted(b.lower().split())
    str_a = " ".join(tokens_a)
    str_b = " ".join(tokens_b)

    if str_a == str_b:
        return 1.0
    if not str_a or not str_b:
        return 0.0

    # Simple Jaccard on tokens
    set_a = set(tokens_a)
    set_b = set(tokens_b)
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0


def token_sort_ratio(a: str, b: str) -> float:
    """Compute token sort ratio between two strings.

    Uses rapidfuzz if available, falls back to simple implementation.
    """
    try:
        from rapidfuzz.fuzz import token_sort_ratio as _rfuzz_ratio

        return _rfuzz_ratio(a, b) / 100.0
    except ImportError:
        return _simple_token_sort_ratio(a, b)


@dataclass
class CoreferenceMatch:
    """A pair of nodes identified as likely the same entity."""

    node_a_id: str
    node_b_id: str
    similarity: float
    match_type: str  # "exact", "fuzzy", "alias"


def find_coreferences(
    nodes: list[ConflictNode],
    threshold: float = FUZZY_THRESHOLD,
) -> list[CoreferenceMatch]:
    """Find potential coreferences among a list of nodes.

    Compares nodes of the same label using name similarity.

    Args:
        nodes: List of extracted nodes.
        threshold: Minimum similarity for a match.

    Returns:
        List of CoreferenceMatch pairs.
    """
    matches: list[CoreferenceMatch] = []

    # Group by label
    by_label: dict[str, list[ConflictNode]] = {}
    for node in nodes:
        by_label.setdefault(node.label, []).append(node)

    for _label, group in by_label.items():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a = group[i]
                b = group[j]

                name_a = getattr(a, "name", getattr(a, "description", ""))
                name_b = getattr(b, "name", getattr(b, "description", ""))

                if not name_a or not name_b:
                    continue

                # Exact match
                if _normalize_name(name_a) == _normalize_name(name_b):
                    matches.append(
                        CoreferenceMatch(
                            node_a_id=a.id,
                            node_b_id=b.id,
                            similarity=1.0,
                            match_type="exact",
                        )
                    )
                    continue

                # Alias match
                aliases_a = set(getattr(a, "aliases", []))
                aliases_b = set(getattr(b, "aliases", []))
                if name_a.lower() in {al.lower() for al in aliases_b} or name_b.lower() in {
                    al.lower() for al in aliases_a
                }:
                    matches.append(
                        CoreferenceMatch(
                            node_a_id=a.id,
                            node_b_id=b.id,
                            similarity=0.95,
                            match_type="alias",
                        )
                    )
                    continue

                # Fuzzy match
                sim = token_sort_ratio(name_a, name_b)
                if sim >= threshold:
                    matches.append(
                        CoreferenceMatch(
                            node_a_id=a.id,
                            node_b_id=b.id,
                            similarity=sim,
                            match_type="fuzzy",
                        )
                    )

    return matches


def merge_coreferent_nodes(
    nodes: list[ConflictNode],
    matches: list[CoreferenceMatch],
) -> list[ConflictNode]:
    """Merge coreferent nodes, keeping the one with higher confidence.

    Updates IDs in remaining references. Returns deduplicated node list.
    """
    # Build merge map: node_to_remove -> node_to_keep
    merge_map: dict[str, str] = {}
    node_map = {n.id: n for n in nodes}

    for match in matches:
        a = node_map.get(match.node_a_id)
        b = node_map.get(match.node_b_id)
        if a is None or b is None:
            continue

        # Keep higher confidence node
        if a.confidence >= b.confidence:
            merge_map[b.id] = a.id
        else:
            merge_map[a.id] = b.id

    # Filter out merged nodes
    removed_ids = set(merge_map.keys())
    return [n for n in nodes if n.id not in removed_ids], merge_map
