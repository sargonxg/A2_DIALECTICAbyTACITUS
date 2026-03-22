"""
Theory Classification Prompt — Classify conflict using theoretical frameworks.
"""

from __future__ import annotations

THEORY_CLASSIFY_PROMPT = """\
Analyze the following conflict graph and classify it using relevant theoretical frameworks.

For each applicable framework, provide:
1. Framework name and assessment
2. Current stage/phase/mode
3. Supporting evidence from the graph
4. Recommended interventions

Frameworks to consider:
- Glasl Escalation Model (9 stages)
- Kriesberg Conflict Lifecycle (7 phases)
- Galtung Violence Triangle (direct/structural/cultural)
- Fisher/Ury Principled Negotiation (positions vs interests, BATNA)
- Thomas-Kilmann Conflict Modes
- Lederach Nested Model (personal/relational/structural/cultural)
- Zartman Ripeness Theory (mutually hurting stalemate)
- French & Raven Power Bases

Graph data:
{graph_json}

Return:
{{
  "assessments": [
    {{
      "framework": "glasl",
      "stage": 4,
      "stage_name": "images_and_coalitions",
      "evidence": ["quote 1", "quote 2"],
      "confidence": 0.8,
      "recommended_intervention": "process consultation"
    }}
  ]
}}
"""
