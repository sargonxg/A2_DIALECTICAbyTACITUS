"""
Standard Tier Extraction Prompt — 12 node types (Essential + Interest, Norm, Narrative, Evidence, Role).
"""
from __future__ import annotations

EXTRACTION_STANDARD_PROMPT = """\
Extract conflict entities from the following text. Return a JSON object with a "nodes" array.

For the STANDARD tier, extract all Essential types PLUS:
- Actor, Conflict, Event, Issue, Process, Outcome, Location (same as Essential)

- Interest: Underlying need, desire, or fear behind a position.
  Required: description, interest_type (substantive/procedural/relational/identity/value)
  Optional: priority (1-5), stated (bool), stated_position, satisfaction (0-1), batna_description

- Norm: Rule, standard, or shared expectation.
  Required: name, norm_type (legal_statute/regulation/contract_clause/custom/organizational_policy/international_law/ethical_principle)
  Optional: jurisdiction, enforceability (binding/persuasive/aspirational)

- Narrative: Dominant story or frame shaping conflict understanding.
  Required: content, narrative_type (dominant/counter/hidden/emerging)
  Optional: perspective, frame_type (diagnostic/prognostic/motivational/identity/loss/gain)

- Evidence: Supporting material for claims or assertions.
  Required: evidence_type (document/testimony/statistical/physical/digital/expert_opinion), description
  Optional: source_name, reliability (0-1)

- Role: Contextual role played by an actor.
  Required: role_type (mediator/arbitrator/facilitator/witness/advocate/respondent/complainant/neutral/observer/guarantor)

For each entity include: label, source_text (exact quote), confidence (0-1).

Return: {"nodes": [{"label": "Actor", "name": "...", ...}, ...]}

Text to analyze:
"""
