"""
Relationship Strength Scoring — Compute confidence and weight for extracted edges.
"""

from __future__ import annotations

from dialectica_ontology.relationships import ConflictRelationship


def score_relationship(edge: ConflictRelationship) -> float:
    """Compute a combined strength score for a relationship.

    Factors:
    - Base confidence from extraction
    - Source text length (longer = more evidence)
    - Edge type-specific heuristics
    """
    score = edge.confidence

    # Boost for longer source text (more evidence)
    if edge.source_text:
        text_len = len(edge.source_text)
        if text_len > 100:
            score = min(1.0, score + 0.05)
        if text_len > 200:
            score = min(1.0, score + 0.05)

    # High-confidence edge types (explicit relationships)
    explicit_types = {"PARTY_TO", "MEMBER_OF", "WITHIN", "RESOLVED_THROUGH", "PRODUCES"}
    if str(edge.type) in explicit_types:
        score = min(1.0, score + 0.05)

    # Lower confidence for inferred relationships
    inferred_types = {"CAUSED", "HAS_POWER_OVER", "TRUSTS"}
    if str(edge.type) in inferred_types:
        score = max(0.0, score - 0.05)

    return round(score, 3)


def apply_relationship_scoring(edges: list[ConflictRelationship]) -> list[ConflictRelationship]:
    """Apply strength scoring to all edges and update their weight field."""
    for edge in edges:
        edge.weight = score_relationship(edge)
    return edges
