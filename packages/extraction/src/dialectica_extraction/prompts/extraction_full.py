"""
Full Tier Extraction Prompt — All 15 node types.
"""
from __future__ import annotations

EXTRACTION_FULL_PROMPT = """\
Extract ALL conflict entities from the following text. Return a JSON object with a "nodes" array.

For the FULL tier, extract all 15 entity types (Essential + Standard + these):
- All Essential types: Actor, Conflict, Event, Issue, Process, Outcome, Location
- All Standard types: Interest, Norm, Narrative, Evidence, Role
- Plus these Full-tier types:

- EmotionalState: An actor's emotional condition at a point in time.
  Required: primary_emotion (joy/trust/fear/surprise/sadness/disgust/anger/anticipation), intensity (low/medium/high/extreme)
  Optional: secondary_emotion, valence (-1 to 1), arousal (0-1), is_group_emotion

- TrustState: Trust level between two actors (Mayer/Davis/Schoorman model).
  Required: perceived_ability (0-1), perceived_benevolence (0-1), perceived_integrity (0-1), overall_trust (0-1)
  Optional: propensity_to_trust (0-1), trust_basis (calculus/knowledge/identification/deterrence/institution)

- PowerDynamic: Power relationship between actors.
  Required: power_domain (coercive/reward/legitimate/expert/referent/informational), magnitude (0-1), direction (unilateral/bilateral/multilateral)
  Optional: legitimacy (0-1), exercised (bool), reversible (bool)

For each entity include: label, source_text (exact quote), confidence (0-1).

Return: {"nodes": [{"label": "Actor", "name": "...", ...}, ...]}

Text to analyze:
"""
