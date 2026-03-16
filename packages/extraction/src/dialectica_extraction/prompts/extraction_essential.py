"""
Essential Tier Extraction Prompt — 7 node types.
"""
from __future__ import annotations

EXTRACTION_ESSENTIAL_PROMPT = """\
Extract conflict entities from the following text. Return a JSON object with a "nodes" array.

For the ESSENTIAL tier, extract these entity types:
- Actor: Any person, organization, state, coalition, or group involved.
  Required: name, actor_type (person/organization/state/coalition/informal_group)
  Optional: description, influence_score (0-1), aliases

- Conflict: A sustained dispute or friction between parties.
  Required: name, scale (micro/meso/macro/meta), domain (interpersonal/workplace/commercial/legal/political/armed), status (latent/active/dormant/resolved/transformed)
  Optional: glasl_stage (1-9), summary

- Event: A discrete time-bounded occurrence.
  Required: event_type (agree/consult/support/cooperate/aid/yield/demand/disapprove/reject/threaten/protest/assault/fight/seize/sanction/reduce_relations), severity (0-1), occurred_at (ISO datetime)
  Optional: description, fatalities

- Issue: The subject matter at stake.
  Required: name, issue_type (substantive/procedural/relational/identity/value)
  Optional: salience (0-1), divisibility (0-1)

- Process: Any procedure for addressing the conflict.
  Required: process_type (negotiation/mediation/arbitration/adjudication/facilitation/conciliation/fact_finding/good_offices/hybrid), resolution_approach (interests/rights/power), status (pending/active/paused/completed/failed/abandoned)

- Outcome: The result of a resolution process.
  Required: outcome_type (agreement/verdict/award/settlement/withdrawal/impasse/transformation)
  Optional: description, terms

- Location: Geographic entity.
  Required: name, location_type (point/city/province/country/region/international)
  Optional: latitude, longitude, country_code

For each entity include: label, source_text (exact quote), confidence (0-1).

Return: {"nodes": [{"label": "Actor", "name": "...", ...}, ...]}

Text to analyze:
"""
