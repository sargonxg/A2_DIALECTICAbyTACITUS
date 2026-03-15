"""
Conflict Grammar Engine — Deterministic symbolic rule evaluation.

ConflictGrammarEngine.evaluate_all_rules():
  Runs ALL symbolic rules from symbolic_rules.py on workspace data.
  Returns RuleEvaluationReport with:
    findings: List of rule findings with evidence
    alerts: Urgent items (rapid escalation, trust breaches)
    recommendations: Actionable intervention recommendations

Individual rule methods:
  glasl_stage_check(): Stage-level classification + escalation detection
  trust_breach_check(): Mayer/Davis/Schoorman trust monitoring
  process_recommendation(): Ury/Brett/Goldberg stage-appropriate process
  norm_violation_check(): CLO-based norm violation analysis
  batna_zopa_analysis(): Fisher/Ury BATNA + zone of possible agreement
"""
from __future__ import annotations

# TODO: Implement in Prompt 7
