"""
Relationship Extraction Prompt — Edge extraction given validated entities.
"""

from __future__ import annotations

RELATIONSHIP_PROMPT = """\
Given the extracted entities and source text below, identify all relationships between them.

Return a JSON object with an "edges" array. Each edge:
- type: Relationship type from allowed list
- source_id: ID of source entity
- target_id: ID of target entity
- source_label: Label of source entity
- target_label: Label of target entity
- confidence: Float 0-1
- source_text: Supporting text quote
- properties: Optional dict of edge-specific properties

Allowed types and constraints:
- PARTY_TO: Actor -> Conflict [role, side, joined_at]
- PARTICIPATES_IN: Actor -> Event [role_type, influence]
- HAS_INTEREST: Actor -> Interest [priority, in_conflict, stated]
- PART_OF: Event -> Conflict
- CAUSED: Event -> Event [mechanism, strength, lag, confidence]
- AT_LOCATION: Event -> Location [precision]
- WITHIN: Location -> Location
- ALLIED_WITH: Actor -> Actor [strength, formality, since]
- OPPOSED_TO: Actor -> Actor [intensity, since]
- HAS_POWER_OVER: Actor -> Actor [domain, magnitude]
- MEMBER_OF: Actor -> Actor [role, since, until]
- GOVERNED_BY: Conflict -> Norm [applicability]
- VIOLATES: Event -> Norm [severity, intentional]
- RESOLVED_THROUGH: Conflict -> Process [initiated_at, initiated_by]
- PRODUCES: Process -> Outcome
- EXPERIENCES: Actor -> EmotionalState [context_event_id]
- TRUSTS: Actor -> Actor [trust_state_id, overall_trust]
- PROMOTES: Actor -> Narrative [strength, since]
- ABOUT: Narrative -> Conflict
- EVIDENCED_BY: Event -> Evidence [relevance]

Rules:
1. Only use entities from the provided list.
2. Respect source/target type constraints.
3. Do not invent relationships not in the text.

Entities:
{entities_json}

Source text:
{text}

Return: {{"edges": [{{"type": "PARTY_TO", "source_id": "...", "target_id": "...", ...}}]}}
"""
