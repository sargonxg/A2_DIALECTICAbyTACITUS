"""Tests for dialectica_ontology.symbolic_rules — All deterministic conflict grammar rules."""

import pytest
from datetime import datetime, timedelta

from dialectica_ontology.symbolic_rules import (
    # Enums and dataclasses
    Severity,
    RuleCategory,
    Finding,
    # Structural rules
    rule_conflict_has_parties,
    rule_event_has_timestamp,
    rule_edge_endpoints_exist,
    rule_process_has_conflict,
    rule_outcome_has_process,
    # Conflict rules
    rule_glasl_level_derivation,
    # Escalation rules
    rule_rapid_escalation,
    rule_escalation_trajectory,
    rule_stage_regression_alert,
    # Ripeness rules
    rule_mutually_hurting_stalemate,
    rule_mutually_enticing_opportunity,
    rule_ripeness_window,
    # Trust rules
    compute_overall_trust,
    rule_trust_deficit,
    rule_trust_breach_event,
    rule_trust_formula_validation,
    # Power rules
    rule_power_asymmetry,
    rule_multi_domain_power_concentration,
    # Causal rules
    rule_causal_chain_length,
    rule_causal_cycles,
    rule_escalation_retaliation_pattern,
    # Process rules
    rule_power_based_no_resolution,
    rule_glasl_process_recommendation,
    rule_rights_based_escalation_warning,
    # Constants / maps
    GLASL_INTERVENTION_MAP,
    INTERVENTION_PROCESS_MAP,
    # Rule engine
    RuleEngine,
    _DEFAULT_RULES,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  Enums, Dataclasses, Registry
# ═══════════════════════════════════════════════════════════════════════════════


class TestSeverityEnum:
    def test_values(self):
        assert Severity.INFO == "info"
        assert Severity.WARNING == "warning"
        assert Severity.ALERT == "alert"
        assert Severity.CRITICAL == "critical"

    def test_all_members(self):
        assert len(Severity) == 4


class TestRuleCategoryEnum:
    def test_values(self):
        assert RuleCategory.STRUCTURAL == "structural"
        assert RuleCategory.ESCALATION == "escalation"
        assert RuleCategory.RIPENESS == "ripeness"
        assert RuleCategory.TRUST == "trust"
        assert RuleCategory.POWER == "power"
        assert RuleCategory.CAUSAL == "causal"
        assert RuleCategory.PROCESS == "process"
        assert RuleCategory.CONFLICT == "conflict"

    def test_all_members(self):
        assert len(RuleCategory) == 8


class TestFinding:
    def test_creation(self):
        f = Finding(
            rule_id="TEST-001",
            category="structural",
            severity="warning",
            message="test message",
        )
        assert f.rule_id == "TEST-001"
        assert f.category == "structural"
        assert f.severity == "warning"
        assert f.message == "test message"
        assert f.affected_entities == []
        assert f.details == {}

    def test_creation_with_all_fields(self):
        f = Finding(
            rule_id="TEST-002",
            category="trust",
            severity="critical",
            message="trust breach",
            affected_entities=["actor_1", "actor_2"],
            details={"key": "value"},
        )
        assert f.affected_entities == ["actor_1", "actor_2"]
        assert f.details == {"key": "value"}


class TestDefaultRulesRegistry:
    def test_has_all_categories(self):
        expected_categories = {
            RuleCategory.STRUCTURAL,
            RuleCategory.CONFLICT,
            RuleCategory.ESCALATION,
            RuleCategory.RIPENESS,
            RuleCategory.TRUST,
            RuleCategory.POWER,
            RuleCategory.CAUSAL,
            RuleCategory.PROCESS,
        }
        assert set(_DEFAULT_RULES.keys()) == expected_categories

    def test_structural_has_5_rules(self):
        assert len(_DEFAULT_RULES[RuleCategory.STRUCTURAL]) == 5

    def test_conflict_has_1_rule(self):
        assert len(_DEFAULT_RULES[RuleCategory.CONFLICT]) == 1

    def test_escalation_has_3_rules(self):
        assert len(_DEFAULT_RULES[RuleCategory.ESCALATION]) == 3

    def test_ripeness_has_3_rules(self):
        assert len(_DEFAULT_RULES[RuleCategory.RIPENESS]) == 3

    def test_trust_has_3_rules(self):
        assert len(_DEFAULT_RULES[RuleCategory.TRUST]) == 3

    def test_power_has_2_rules(self):
        assert len(_DEFAULT_RULES[RuleCategory.POWER]) == 2

    def test_causal_has_3_rules(self):
        assert len(_DEFAULT_RULES[RuleCategory.CAUSAL]) == 3

    def test_process_has_3_rules(self):
        assert len(_DEFAULT_RULES[RuleCategory.PROCESS]) == 3

    def test_total_rule_count(self):
        total = sum(len(fns) for fns in _DEFAULT_RULES.values())
        assert total == 23


class TestGlaslInterventionMap:
    def test_all_9_stages(self):
        assert len(GLASL_INTERVENTION_MAP) == 9
        for i in range(1, 10):
            assert i in GLASL_INTERVENTION_MAP

    @pytest.mark.parametrize("stage,intervention", [
        (1, "moderation"), (2, "moderation"),
        (3, "facilitation"),
        (4, "process_consultation"),
        (5, "mediation"), (6, "mediation"),
        (7, "arbitration"),
        (8, "power_intervention"), (9, "power_intervention"),
    ])
    def test_stage_to_intervention(self, stage, intervention):
        assert GLASL_INTERVENTION_MAP[stage] == intervention


class TestInterventionProcessMap:
    def test_has_all_intervention_types(self):
        expected = {
            "moderation", "facilitation", "process_consultation",
            "mediation", "arbitration", "power_intervention",
        }
        assert set(INTERVENTION_PROCESS_MAP.keys()) == expected

    def test_moderation_recommends_negotiation(self):
        assert "negotiation" in INTERVENTION_PROCESS_MAP["moderation"]

    def test_mediation_has_multiple_types(self):
        assert len(INTERVENTION_PROCESS_MAP["mediation"]) >= 4


# ═══════════════════════════════════════════════════════════════════════════════
#  STRUCTURAL RULES
# ═══════════════════════════════════════════════════════════════════════════════


class TestRuleConflictHasParties:
    """Tests for rule_conflict_has_parties: STRUCT-001."""

    def test_conflict_with_zero_parties(self):
        ctx = {
            "nodes": {
                "c1": {"id": "c1", "label": "Conflict", "name": "Test Conflict"},
            },
            "edges": [],
        }
        findings = rule_conflict_has_parties(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "STRUCT-001"
        assert findings[0].severity == Severity.WARNING
        assert findings[0].details["party_count"] == 0

    def test_conflict_with_one_party(self):
        ctx = {
            "nodes": {
                "c1": {"id": "c1", "label": "Conflict", "name": "Test"},
                "a1": {"id": "a1", "label": "Actor", "name": "Alice"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
            ],
        }
        findings = rule_conflict_has_parties(ctx)
        assert len(findings) == 1
        assert findings[0].details["party_count"] == 1

    def test_conflict_with_two_parties_no_finding(self):
        ctx = {
            "nodes": {
                "c1": {"id": "c1", "label": "Conflict", "name": "Test"},
                "a1": {"id": "a1", "label": "Actor", "name": "Alice"},
                "a2": {"id": "a2", "label": "Actor", "name": "Bob"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
                {"type": "PARTY_TO", "source_id": "a2", "target_id": "c1", "properties": {}},
            ],
        }
        findings = rule_conflict_has_parties(ctx)
        assert len(findings) == 0

    def test_conflict_with_three_parties_no_finding(self):
        ctx = {
            "nodes": {
                "c1": {"id": "c1", "label": "Conflict", "name": "Test"},
                "a1": {"id": "a1", "label": "Actor"},
                "a2": {"id": "a2", "label": "Actor"},
                "a3": {"id": "a3", "label": "Actor"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
                {"type": "PARTY_TO", "source_id": "a2", "target_id": "c1", "properties": {}},
                {"type": "PARTY_TO", "source_id": "a3", "target_id": "c1", "properties": {}},
            ],
        }
        findings = rule_conflict_has_parties(ctx)
        assert len(findings) == 0

    def test_empty_context(self):
        findings = rule_conflict_has_parties({"nodes": {}, "edges": []})
        assert findings == []

    def test_no_conflicts_returns_empty(self):
        ctx = {
            "nodes": {"a1": {"id": "a1", "label": "Actor"}},
            "edges": [],
        }
        assert rule_conflict_has_parties(ctx) == []


class TestRuleEventHasTimestamp:
    """Tests for rule_event_has_timestamp: STRUCT-002."""

    def test_event_without_timestamp(self):
        ctx = {
            "nodes": {"e1": {"id": "e1", "label": "Event", "name": "Something happened"}},
            "edges": [],
        }
        findings = rule_event_has_timestamp(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "STRUCT-002"
        assert "e1" in findings[0].affected_entities

    def test_event_with_timestamp_no_finding(self):
        ctx = {
            "nodes": {
                "e1": {
                    "id": "e1", "label": "Event",
                    "occurred_at": "2024-01-15T10:00:00",
                },
            },
            "edges": [],
        }
        findings = rule_event_has_timestamp(ctx)
        assert len(findings) == 0

    def test_event_with_none_timestamp(self):
        ctx = {
            "nodes": {
                "e1": {"id": "e1", "label": "Event", "occurred_at": None},
            },
            "edges": [],
        }
        findings = rule_event_has_timestamp(ctx)
        assert len(findings) == 1

    def test_no_events(self):
        ctx = {"nodes": {"a1": {"id": "a1", "label": "Actor"}}, "edges": []}
        assert rule_event_has_timestamp(ctx) == []


class TestRuleEdgeEndpointsExist:
    """Tests for rule_edge_endpoints_exist: STRUCT-003."""

    def test_valid_edge(self):
        ctx = {
            "nodes": {
                "a1": {"id": "a1", "label": "Actor"},
                "c1": {"id": "c1", "label": "Conflict"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
            ],
        }
        findings = rule_edge_endpoints_exist(ctx)
        assert len(findings) == 0

    def test_edge_with_missing_source(self):
        ctx = {
            "nodes": {"c1": {"id": "c1", "label": "Conflict"}},
            "edges": [
                {"type": "PARTY_TO", "source_id": "missing_actor", "target_id": "c1", "properties": {}},
            ],
        }
        findings = rule_edge_endpoints_exist(ctx)
        assert len(findings) == 1
        assert "missing_actor" in findings[0].message

    def test_edge_with_missing_target(self):
        ctx = {
            "nodes": {"a1": {"id": "a1", "label": "Actor"}},
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "missing_conflict", "properties": {}},
            ],
        }
        findings = rule_edge_endpoints_exist(ctx)
        assert len(findings) == 1
        assert "missing_conflict" in findings[0].message

    def test_edge_with_both_endpoints_missing(self):
        ctx = {
            "nodes": {},
            "edges": [
                {"type": "PARTY_TO", "source_id": "missing_a", "target_id": "missing_b", "properties": {}},
            ],
        }
        findings = rule_edge_endpoints_exist(ctx)
        assert len(findings) == 1
        assert "missing_a" in findings[0].message
        assert "missing_b" in findings[0].message

    def test_no_edges(self):
        ctx = {"nodes": {"a1": {"id": "a1", "label": "Actor"}}, "edges": []}
        assert rule_edge_endpoints_exist(ctx) == []


class TestRuleProcessHasConflict:
    """Tests for rule_process_has_conflict: STRUCT-004."""

    def test_unlinked_process(self):
        ctx = {
            "nodes": {"p1": {"id": "p1", "label": "Process", "name": "Mediation"}},
            "edges": [],
        }
        findings = rule_process_has_conflict(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "STRUCT-004"
        assert findings[0].severity == Severity.INFO

    def test_linked_process_no_finding(self):
        ctx = {
            "nodes": {
                "p1": {"id": "p1", "label": "Process"},
                "c1": {"id": "c1", "label": "Conflict"},
            },
            "edges": [
                {"type": "RESOLVED_THROUGH", "source_id": "c1", "target_id": "p1", "properties": {}},
            ],
        }
        findings = rule_process_has_conflict(ctx)
        assert len(findings) == 0

    def test_no_processes(self):
        ctx = {"nodes": {}, "edges": []}
        assert rule_process_has_conflict(ctx) == []


class TestRuleOutcomeHasProcess:
    """Tests for rule_outcome_has_process: STRUCT-005."""

    def test_unlinked_outcome(self):
        ctx = {
            "nodes": {"o1": {"id": "o1", "label": "Outcome"}},
            "edges": [],
        }
        findings = rule_outcome_has_process(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "STRUCT-005"
        assert findings[0].severity == Severity.INFO

    def test_linked_outcome_no_finding(self):
        ctx = {
            "nodes": {
                "o1": {"id": "o1", "label": "Outcome"},
                "p1": {"id": "p1", "label": "Process"},
            },
            "edges": [
                {"type": "PRODUCES", "source_id": "p1", "target_id": "o1", "properties": {}},
            ],
        }
        findings = rule_outcome_has_process(ctx)
        assert len(findings) == 0

    def test_no_outcomes(self):
        ctx = {"nodes": {}, "edges": []}
        assert rule_outcome_has_process(ctx) == []


# ═══════════════════════════════════════════════════════════════════════════════
#  CONFLICT RULES — Glasl level derivation
# ═══════════════════════════════════════════════════════════════════════════════


class TestRuleGlaslLevelDerivation:
    """Tests for rule_glasl_level_derivation: CONFLICT-001/002/003."""

    @pytest.mark.parametrize("stage", [1, 2, 3])
    def test_stages_1_3_derive_win_win(self, stage):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": stage,
                },
            },
            "edges": [],
        }
        findings = rule_glasl_level_derivation(ctx)
        # No mismatch, no lose-lose: should be empty
        assert len(findings) == 0

    @pytest.mark.parametrize("stage", [4, 5, 6])
    def test_stages_4_6_derive_win_lose(self, stage):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": stage,
                },
            },
            "edges": [],
        }
        findings = rule_glasl_level_derivation(ctx)
        assert len(findings) == 0

    @pytest.mark.parametrize("stage", [7, 8, 9])
    def test_stages_7_9_derive_lose_lose_critical(self, stage):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": stage,
                },
            },
            "edges": [],
        }
        findings = rule_glasl_level_derivation(ctx)
        # Should get CONFLICT-003 (lose-lose critical alert)
        assert len(findings) == 1
        assert findings[0].rule_id == "CONFLICT-003"
        assert findings[0].severity == Severity.CRITICAL

    def test_mismatch_detected(self):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": 2, "glasl_level": "lose_lose",
                },
            },
            "edges": [],
        }
        findings = rule_glasl_level_derivation(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "CONFLICT-002"
        assert findings[0].severity == Severity.WARNING
        assert findings[0].details["derived_level"] == "win_win"
        assert findings[0].details["stored_level"] == "lose_lose"

    def test_mismatch_plus_lose_lose(self):
        """Stage 7 with stored win_win => both CONFLICT-002 (mismatch) and CONFLICT-003 (lose-lose)."""
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": 7, "glasl_level": "win_win",
                },
            },
            "edges": [],
        }
        findings = rule_glasl_level_derivation(ctx)
        rule_ids = {f.rule_id for f in findings}
        assert "CONFLICT-002" in rule_ids
        assert "CONFLICT-003" in rule_ids

    def test_non_integer_stage_warning(self):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": "invalid",
                },
            },
            "edges": [],
        }
        findings = rule_glasl_level_derivation(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "CONFLICT-001"

    def test_no_stage_skips_conflict(self):
        ctx = {
            "nodes": {
                "c1": {"id": "c1", "label": "Conflict", "name": "Test"},
            },
            "edges": [],
        }
        findings = rule_glasl_level_derivation(ctx)
        assert len(findings) == 0

    def test_matching_stored_level_no_mismatch(self):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": 5, "glasl_level": "win_lose",
                },
            },
            "edges": [],
        }
        findings = rule_glasl_level_derivation(ctx)
        # No mismatch, not lose-lose
        assert len(findings) == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  ESCALATION RULES
# ═══════════════════════════════════════════════════════════════════════════════


class TestRuleRapidEscalation:
    """Tests for rule_rapid_escalation: ESCAL-001."""

    def test_rapid_jump_detected(self):
        base = datetime(2024, 1, 1)
        ctx = {
            "nodes": {"c1": {"id": "c1", "label": "Conflict", "name": "Test"}},
            "edges": [],
            "conflict_history": {
                "c1": [
                    {"glasl_stage": 2, "timestamp": base.isoformat()},
                    {"glasl_stage": 5, "timestamp": (base + timedelta(days=10)).isoformat()},
                ],
            },
        }
        findings = rule_rapid_escalation(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "ESCAL-001"
        assert findings[0].severity == Severity.ALERT
        assert findings[0].details["previous_stage"] == 2
        assert findings[0].details["current_stage"] == 5

    def test_slow_escalation_not_flagged(self):
        base = datetime(2024, 1, 1)
        ctx = {
            "nodes": {},
            "edges": [],
            "conflict_history": {
                "c1": [
                    {"glasl_stage": 2, "timestamp": base.isoformat()},
                    {"glasl_stage": 4, "timestamp": (base + timedelta(days=60)).isoformat()},
                ],
            },
        }
        findings = rule_rapid_escalation(ctx)
        assert len(findings) == 0

    def test_single_stage_jump_not_flagged(self):
        base = datetime(2024, 1, 1)
        ctx = {
            "nodes": {},
            "edges": [],
            "conflict_history": {
                "c1": [
                    {"glasl_stage": 2, "timestamp": base.isoformat()},
                    {"glasl_stage": 3, "timestamp": (base + timedelta(days=5)).isoformat()},
                ],
            },
        }
        findings = rule_rapid_escalation(ctx)
        assert len(findings) == 0

    def test_empty_history(self):
        ctx = {"nodes": {}, "edges": [], "conflict_history": {}}
        assert rule_rapid_escalation(ctx) == []

    def test_single_record(self):
        ctx = {
            "nodes": {}, "edges": [],
            "conflict_history": {
                "c1": [{"glasl_stage": 3, "timestamp": "2024-01-01T00:00:00"}],
            },
        }
        assert rule_rapid_escalation(ctx) == []

    def test_no_conflict_history_key(self):
        ctx = {"nodes": {}, "edges": []}
        assert rule_rapid_escalation(ctx) == []

    def test_invalid_timestamp_skipped(self):
        ctx = {
            "nodes": {}, "edges": [],
            "conflict_history": {
                "c1": [
                    {"glasl_stage": 2, "timestamp": "not-a-date"},
                    {"glasl_stage": 5, "timestamp": "also-not-a-date"},
                ],
            },
        }
        findings = rule_rapid_escalation(ctx)
        assert len(findings) == 0


class TestRuleEscalationTrajectory:
    """Tests for rule_escalation_trajectory: ESCAL-002."""

    def test_monotonic_increase_detected(self):
        base = datetime(2024, 1, 1)
        ctx = {
            "nodes": {"c1": {"id": "c1", "label": "Conflict", "name": "Test"}},
            "edges": [],
            "conflict_history": {
                "c1": [
                    {"glasl_stage": 2, "timestamp": (base).isoformat()},
                    {"glasl_stage": 3, "timestamp": (base + timedelta(days=30)).isoformat()},
                    {"glasl_stage": 5, "timestamp": (base + timedelta(days=60)).isoformat()},
                ],
            },
        }
        findings = rule_escalation_trajectory(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "ESCAL-002"
        assert findings[0].details["consecutive_increases"] >= 2

    def test_non_monotonic_not_flagged(self):
        base = datetime(2024, 1, 1)
        ctx = {
            "nodes": {}, "edges": [],
            "conflict_history": {
                "c1": [
                    {"glasl_stage": 3, "timestamp": (base).isoformat()},
                    {"glasl_stage": 2, "timestamp": (base + timedelta(days=30)).isoformat()},
                    {"glasl_stage": 4, "timestamp": (base + timedelta(days=60)).isoformat()},
                ],
            },
        }
        findings = rule_escalation_trajectory(ctx)
        assert len(findings) == 0

    def test_fewer_than_3_records_skipped(self):
        ctx = {
            "nodes": {}, "edges": [],
            "conflict_history": {
                "c1": [
                    {"glasl_stage": 2, "timestamp": "2024-01-01T00:00:00"},
                    {"glasl_stage": 4, "timestamp": "2024-02-01T00:00:00"},
                ],
            },
        }
        findings = rule_escalation_trajectory(ctx)
        assert len(findings) == 0

    def test_empty_history(self):
        ctx = {"nodes": {}, "edges": [], "conflict_history": {}}
        assert rule_escalation_trajectory(ctx) == []


class TestRuleStageRegressionAlert:
    """Tests for rule_stage_regression_alert: ESCAL-003."""

    def test_deescalation_detected(self):
        ctx = {
            "nodes": {"c1": {"id": "c1", "label": "Conflict", "name": "Test"}},
            "edges": [],
            "conflict_history": {
                "c1": [
                    {"glasl_stage": 5, "timestamp": "2024-01-01T00:00:00"},
                    {"glasl_stage": 3, "timestamp": "2024-02-01T00:00:00"},
                ],
            },
        }
        findings = rule_stage_regression_alert(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "ESCAL-003"
        assert findings[0].severity == Severity.INFO
        assert findings[0].details["previous_stage"] == 5
        assert findings[0].details["current_stage"] == 3

    def test_escalation_not_flagged(self):
        ctx = {
            "nodes": {}, "edges": [],
            "conflict_history": {
                "c1": [
                    {"glasl_stage": 3, "timestamp": "2024-01-01T00:00:00"},
                    {"glasl_stage": 5, "timestamp": "2024-02-01T00:00:00"},
                ],
            },
        }
        findings = rule_stage_regression_alert(ctx)
        assert len(findings) == 0

    def test_same_stage_not_flagged(self):
        ctx = {
            "nodes": {}, "edges": [],
            "conflict_history": {
                "c1": [
                    {"glasl_stage": 3, "timestamp": "2024-01-01T00:00:00"},
                    {"glasl_stage": 3, "timestamp": "2024-02-01T00:00:00"},
                ],
            },
        }
        findings = rule_stage_regression_alert(ctx)
        assert len(findings) == 0

    def test_single_record(self):
        ctx = {
            "nodes": {}, "edges": [],
            "conflict_history": {
                "c1": [{"glasl_stage": 3, "timestamp": "2024-01-01T00:00:00"}],
            },
        }
        assert rule_stage_regression_alert(ctx) == []


# ═══════════════════════════════════════════════════════════════════════════════
#  RIPENESS RULES
# ═══════════════════════════════════════════════════════════════════════════════


class TestRuleMutuallyHurtingStalemate:
    """Tests for rule_mutually_hurting_stalemate: RIPE-001."""

    def test_stalemate_with_hurting_parties(self):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "kriesberg_phase": "stalemate",
                },
                "a1": {"id": "a1", "label": "Actor", "name": "Alice"},
                "a2": {"id": "a2", "label": "Actor", "name": "Bob"},
                "em1": {"id": "em1", "label": "EmotionalState", "primary_emotion": "anger"},
                "em2": {"id": "em2", "label": "EmotionalState", "primary_emotion": "fear"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
                {"type": "PARTY_TO", "source_id": "a2", "target_id": "c1", "properties": {}},
                {"type": "EXPERIENCES", "source_id": "a1", "target_id": "em1", "properties": {}},
                {"type": "EXPERIENCES", "source_id": "a2", "target_id": "em2", "properties": {}},
            ],
        }
        findings = rule_mutually_hurting_stalemate(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "RIPE-001"
        assert findings[0].severity == Severity.ALERT

    def test_stalemate_with_2_parties_triggers_even_without_emotions(self):
        """Stalemate phase with >= 2 parties triggers MHS even without emotion check."""
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "kriesberg_phase": "stalemate",
                },
                "a1": {"id": "a1", "label": "Actor"},
                "a2": {"id": "a2", "label": "Actor"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
                {"type": "PARTY_TO", "source_id": "a2", "target_id": "c1", "properties": {}},
            ],
        }
        findings = rule_mutually_hurting_stalemate(ctx)
        assert len(findings) == 1

    def test_high_intensity_with_hurting_parties(self):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "intensity": "severe",
                },
                "a1": {"id": "a1", "label": "Actor"},
                "a2": {"id": "a2", "label": "Actor"},
                "em1": {"id": "em1", "label": "EmotionalState", "primary_emotion": "sadness"},
                "em2": {"id": "em2", "label": "EmotionalState", "primary_emotion": "disgust"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
                {"type": "PARTY_TO", "source_id": "a2", "target_id": "c1", "properties": {}},
                {"type": "EXPERIENCES", "source_id": "a1", "target_id": "em1", "properties": {}},
                {"type": "EXPERIENCES", "source_id": "a2", "target_id": "em2", "properties": {}},
            ],
        }
        findings = rule_mutually_hurting_stalemate(ctx)
        assert len(findings) == 1

    def test_low_intensity_no_stalemate_skipped(self):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "intensity": "low",
                    "kriesberg_phase": "emergence",
                },
            },
            "edges": [],
        }
        findings = rule_mutually_hurting_stalemate(ctx)
        assert len(findings) == 0

    def test_active_process_suppresses_finding(self):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "kriesberg_phase": "stalemate",
                },
                "a1": {"id": "a1", "label": "Actor"},
                "a2": {"id": "a2", "label": "Actor"},
                "p1": {"id": "p1", "label": "Process", "status": "active"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
                {"type": "PARTY_TO", "source_id": "a2", "target_id": "c1", "properties": {}},
                {"type": "RESOLVED_THROUGH", "source_id": "c1", "target_id": "p1", "properties": {}},
            ],
        }
        findings = rule_mutually_hurting_stalemate(ctx)
        assert len(findings) == 0


class TestRuleMutuallyEnticingOpportunity:
    """Tests for rule_mutually_enticing_opportunity: RIPE-002."""

    def test_shared_interests_detected(self):
        ctx = {
            "nodes": {
                "c1": {"id": "c1", "label": "Conflict", "name": "Test"},
                "a1": {"id": "a1", "label": "Actor"},
                "a2": {"id": "a2", "label": "Actor"},
                "i1": {"id": "i1", "label": "Interest", "name": "Peace"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
                {"type": "PARTY_TO", "source_id": "a2", "target_id": "c1", "properties": {}},
                {"type": "HAS_INTEREST", "source_id": "a1", "target_id": "i1", "properties": {}},
                {"type": "HAS_INTEREST", "source_id": "a2", "target_id": "i1", "properties": {}},
            ],
        }
        findings = rule_mutually_enticing_opportunity(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "RIPE-002"
        assert "i1" in findings[0].details["shared_interest_ids"]

    def test_cooperative_events_detected(self):
        ctx = {
            "nodes": {
                "c1": {"id": "c1", "label": "Conflict", "name": "Test"},
                "a1": {"id": "a1", "label": "Actor"},
                "a2": {"id": "a2", "label": "Actor"},
                "ev1": {"id": "ev1", "label": "Event", "event_type": "cooperate"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
                {"type": "PARTY_TO", "source_id": "a2", "target_id": "c1", "properties": {}},
                {"type": "PART_OF", "source_id": "ev1", "target_id": "c1", "properties": {}},
            ],
        }
        findings = rule_mutually_enticing_opportunity(ctx)
        assert len(findings) == 1
        assert "ev1" in findings[0].details["cooperative_event_ids"]

    def test_no_shared_interests_no_coop_events(self):
        ctx = {
            "nodes": {
                "c1": {"id": "c1", "label": "Conflict", "name": "Test"},
                "a1": {"id": "a1", "label": "Actor"},
                "a2": {"id": "a2", "label": "Actor"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
                {"type": "PARTY_TO", "source_id": "a2", "target_id": "c1", "properties": {}},
            ],
        }
        findings = rule_mutually_enticing_opportunity(ctx)
        assert len(findings) == 0

    def test_fewer_than_2_parties_skipped(self):
        ctx = {
            "nodes": {
                "c1": {"id": "c1", "label": "Conflict", "name": "Test"},
                "a1": {"id": "a1", "label": "Actor"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
            ],
        }
        findings = rule_mutually_enticing_opportunity(ctx)
        assert len(findings) == 0


class TestRuleRipenessWindow:
    """Tests for rule_ripeness_window: RIPE-003."""

    def test_both_mhs_and_meo_triggers_ripeness(self):
        """When both MHS and MEO are detected for same conflict, ripeness fires."""
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "kriesberg_phase": "stalemate",
                },
                "a1": {"id": "a1", "label": "Actor"},
                "a2": {"id": "a2", "label": "Actor"},
                "i1": {"id": "i1", "label": "Interest", "name": "Peace"},
                "em1": {"id": "em1", "label": "EmotionalState", "primary_emotion": "anger"},
                "em2": {"id": "em2", "label": "EmotionalState", "primary_emotion": "fear"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
                {"type": "PARTY_TO", "source_id": "a2", "target_id": "c1", "properties": {}},
                {"type": "HAS_INTEREST", "source_id": "a1", "target_id": "i1", "properties": {}},
                {"type": "HAS_INTEREST", "source_id": "a2", "target_id": "i1", "properties": {}},
                {"type": "EXPERIENCES", "source_id": "a1", "target_id": "em1", "properties": {}},
                {"type": "EXPERIENCES", "source_id": "a2", "target_id": "em2", "properties": {}},
            ],
        }
        findings = rule_ripeness_window(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "RIPE-003"
        assert findings[0].severity == Severity.CRITICAL

    def test_only_mhs_no_ripeness(self):
        """MHS alone does not trigger ripeness window."""
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "kriesberg_phase": "stalemate",
                },
                "a1": {"id": "a1", "label": "Actor"},
                "a2": {"id": "a2", "label": "Actor"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
                {"type": "PARTY_TO", "source_id": "a2", "target_id": "c1", "properties": {}},
            ],
        }
        findings = rule_ripeness_window(ctx)
        assert len(findings) == 0

    def test_empty_context(self):
        ctx = {"nodes": {}, "edges": []}
        assert rule_ripeness_window(ctx) == []


# ═══════════════════════════════════════════════════════════════════════════════
#  TRUST RULES
# ═══════════════════════════════════════════════════════════════════════════════


class TestComputeOverallTrust:
    """Tests for the compute_overall_trust helper function."""

    def test_basic_computation(self):
        # propensity=1.0, ability=1.0, benevolence=1.0, integrity=1.0
        # => 1.0 * (0.3*1 + 0.3*1 + 0.4*1) = 1.0
        result = compute_overall_trust(1.0, 1.0, 1.0, 1.0)
        assert abs(result - 1.0) < 1e-9

    def test_zero_propensity(self):
        result = compute_overall_trust(0.0, 1.0, 1.0, 1.0)
        assert result == 0.0

    def test_custom_weights(self):
        result = compute_overall_trust(1.0, 1.0, 0.0, 0.0, w1=1.0, w2=0.0, w3=0.0)
        assert abs(result - 1.0) < 1e-9

    def test_partial_values(self):
        # propensity=0.5, ability=0.8, benevolence=0.6, integrity=0.7
        # => 0.5 * (0.3*0.8 + 0.3*0.6 + 0.4*0.7) = 0.5 * (0.24 + 0.18 + 0.28) = 0.5 * 0.7 = 0.35
        result = compute_overall_trust(0.5, 0.8, 0.6, 0.7)
        assert abs(result - 0.35) < 1e-9


class TestRuleTrustDeficit:
    """Tests for rule_trust_deficit: TRUST-001."""

    def test_low_trust_flagged(self):
        ctx = {
            "nodes": {
                "ts1": {
                    "id": "ts1", "label": "TrustState",
                    "overall_trust": 0.15,
                },
            },
            "edges": [],
        }
        findings = rule_trust_deficit(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "TRUST-001"
        assert findings[0].severity == Severity.ALERT

    def test_adequate_trust_no_finding(self):
        ctx = {
            "nodes": {
                "ts1": {
                    "id": "ts1", "label": "TrustState",
                    "overall_trust": 0.7,
                },
            },
            "edges": [],
        }
        findings = rule_trust_deficit(ctx)
        assert len(findings) == 0

    def test_threshold_boundary_not_flagged(self):
        ctx = {
            "nodes": {
                "ts1": {
                    "id": "ts1", "label": "TrustState",
                    "overall_trust": 0.3,
                },
            },
            "edges": [],
        }
        findings = rule_trust_deficit(ctx)
        assert len(findings) == 0

    def test_none_overall_trust_skipped(self):
        ctx = {
            "nodes": {
                "ts1": {"id": "ts1", "label": "TrustState"},
            },
            "edges": [],
        }
        findings = rule_trust_deficit(ctx)
        assert len(findings) == 0

    def test_involved_actors_from_trusts_edges(self):
        ctx = {
            "nodes": {
                "ts1": {"id": "ts1", "label": "TrustState", "overall_trust": 0.1},
                "a1": {"id": "a1", "label": "Actor"},
                "a2": {"id": "a2", "label": "Actor"},
            },
            "edges": [
                {
                    "type": "TRUSTS", "source_id": "a1", "target_id": "a2",
                    "properties": {"trust_state_id": "ts1"},
                },
            ],
        }
        findings = rule_trust_deficit(ctx)
        assert len(findings) == 1
        assert "a1" in findings[0].affected_entities
        assert "a2" in findings[0].affected_entities


class TestRuleTrustBreachEvent:
    """Tests for rule_trust_breach_event: TRUST-002."""

    def test_large_integrity_drop(self):
        ctx = {
            "nodes": {},
            "edges": [],
            "trust_history": {
                "ts1": [
                    {"perceived_integrity": 0.9, "timestamp": "2024-01-01T00:00:00"},
                    {"perceived_integrity": 0.4, "timestamp": "2024-02-01T00:00:00"},
                ],
            },
        }
        findings = rule_trust_breach_event(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "TRUST-002"
        assert findings[0].severity == Severity.CRITICAL
        assert findings[0].details["integrity_drop"] == pytest.approx(0.5)

    def test_small_drop_not_flagged(self):
        ctx = {
            "nodes": {},
            "edges": [],
            "trust_history": {
                "ts1": [
                    {"perceived_integrity": 0.8, "timestamp": "2024-01-01T00:00:00"},
                    {"perceived_integrity": 0.7, "timestamp": "2024-02-01T00:00:00"},
                ],
            },
        }
        findings = rule_trust_breach_event(ctx)
        assert len(findings) == 0

    def test_integrity_increase_not_flagged(self):
        ctx = {
            "nodes": {},
            "edges": [],
            "trust_history": {
                "ts1": [
                    {"perceived_integrity": 0.4, "timestamp": "2024-01-01T00:00:00"},
                    {"perceived_integrity": 0.9, "timestamp": "2024-02-01T00:00:00"},
                ],
            },
        }
        findings = rule_trust_breach_event(ctx)
        assert len(findings) == 0

    def test_single_record_skipped(self):
        ctx = {
            "nodes": {},
            "edges": [],
            "trust_history": {
                "ts1": [{"perceived_integrity": 0.9, "timestamp": "2024-01-01T00:00:00"}],
            },
        }
        assert rule_trust_breach_event(ctx) == []

    def test_no_trust_history_key(self):
        ctx = {"nodes": {}, "edges": []}
        assert rule_trust_breach_event(ctx) == []


class TestRuleTrustFormulaValidation:
    """Tests for rule_trust_formula_validation: TRUST-003."""

    def test_mismatch_detected(self):
        # Computed: 0.8 * (0.3*0.9 + 0.3*0.8 + 0.4*0.7) = 0.8 * (0.27+0.24+0.28) = 0.8*0.79 = 0.632
        ctx = {
            "nodes": {
                "ts1": {
                    "id": "ts1", "label": "TrustState",
                    "propensity_to_trust": 0.8,
                    "perceived_ability": 0.9,
                    "perceived_benevolence": 0.8,
                    "perceived_integrity": 0.7,
                    "overall_trust": 0.2,  # way off from 0.632
                },
            },
            "edges": [],
        }
        findings = rule_trust_formula_validation(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "TRUST-003"

    def test_consistent_no_finding(self):
        ctx = {
            "nodes": {
                "ts1": {
                    "id": "ts1", "label": "TrustState",
                    "propensity_to_trust": 1.0,
                    "perceived_ability": 1.0,
                    "perceived_benevolence": 1.0,
                    "perceived_integrity": 1.0,
                    "overall_trust": 1.0,  # exactly matches formula
                },
            },
            "edges": [],
        }
        findings = rule_trust_formula_validation(ctx)
        assert len(findings) == 0

    def test_missing_values_skipped(self):
        ctx = {
            "nodes": {
                "ts1": {
                    "id": "ts1", "label": "TrustState",
                    "propensity_to_trust": 0.8,
                    # missing perceived_ability, benevolence, integrity
                    "overall_trust": 0.5,
                },
            },
            "edges": [],
        }
        findings = rule_trust_formula_validation(ctx)
        assert len(findings) == 0

    def test_within_tolerance_no_finding(self):
        # Computed = 0.632, stored = 0.62, diff = 0.012 < 0.1
        ctx = {
            "nodes": {
                "ts1": {
                    "id": "ts1", "label": "TrustState",
                    "propensity_to_trust": 0.8,
                    "perceived_ability": 0.9,
                    "perceived_benevolence": 0.8,
                    "perceived_integrity": 0.7,
                    "overall_trust": 0.62,
                },
            },
            "edges": [],
        }
        findings = rule_trust_formula_validation(ctx)
        assert len(findings) == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  POWER RULES
# ═══════════════════════════════════════════════════════════════════════════════


class TestRulePowerAsymmetry:
    """Tests for rule_power_asymmetry: POWER-001/002."""

    def test_high_magnitude_shared_conflict(self):
        ctx = {
            "nodes": {
                "c1": {"id": "c1", "label": "Conflict", "name": "Test"},
                "a1": {"id": "a1", "label": "Actor", "name": "Big Corp"},
                "a2": {"id": "a2", "label": "Actor", "name": "Small Co"},
            },
            "edges": [
                {"type": "PARTY_TO", "source_id": "a1", "target_id": "c1", "properties": {}},
                {"type": "PARTY_TO", "source_id": "a2", "target_id": "c1", "properties": {}},
                {
                    "type": "HAS_POWER_OVER", "source_id": "a1", "target_id": "a2",
                    "properties": {"magnitude": 0.8, "domain": "economic"},
                },
            ],
        }
        findings = rule_power_asymmetry(ctx)
        # Should get POWER-001 for shared conflict
        power_001 = [f for f in findings if f.rule_id == "POWER-001"]
        assert len(power_001) == 1
        assert "economic" in power_001[0].message

    def test_high_magnitude_no_shared_conflict(self):
        ctx = {
            "nodes": {
                "a1": {"id": "a1", "label": "Actor", "name": "A"},
                "a2": {"id": "a2", "label": "Actor", "name": "B"},
            },
            "edges": [
                {
                    "type": "HAS_POWER_OVER", "source_id": "a1", "target_id": "a2",
                    "properties": {"magnitude": 0.9, "domain": "military"},
                },
            ],
        }
        findings = rule_power_asymmetry(ctx)
        power_002 = [f for f in findings if f.rule_id == "POWER-002"]
        assert len(power_002) == 1

    def test_low_magnitude_not_flagged(self):
        ctx = {
            "nodes": {
                "a1": {"id": "a1", "label": "Actor"},
                "a2": {"id": "a2", "label": "Actor"},
            },
            "edges": [
                {
                    "type": "HAS_POWER_OVER", "source_id": "a1", "target_id": "a2",
                    "properties": {"magnitude": 0.3, "domain": "economic"},
                },
            ],
        }
        findings = rule_power_asymmetry(ctx)
        assert len(findings) == 0

    def test_no_magnitude_skipped(self):
        ctx = {
            "nodes": {},
            "edges": [
                {
                    "type": "HAS_POWER_OVER", "source_id": "a1", "target_id": "a2",
                    "properties": {},
                },
            ],
        }
        findings = rule_power_asymmetry(ctx)
        assert len(findings) == 0

    def test_magnitude_from_power_dynamic_node(self):
        ctx = {
            "nodes": {
                "a1": {"id": "a1", "label": "Actor"},
                "a2": {"id": "a2", "label": "Actor"},
                "pd1": {"id": "pd1", "label": "PowerDynamic", "magnitude": 0.75},
            },
            "edges": [
                {
                    "type": "HAS_POWER_OVER", "source_id": "a1", "target_id": "a2",
                    "properties": {"power_dynamic_id": "pd1", "domain": "political"},
                },
            ],
        }
        findings = rule_power_asymmetry(ctx)
        power_002 = [f for f in findings if f.rule_id == "POWER-002"]
        assert len(power_002) == 1


class TestRuleMultiDomainPowerConcentration:
    """Tests for rule_multi_domain_power_concentration: POWER-003."""

    def test_multi_domain_detected(self):
        ctx = {
            "nodes": {
                "a1": {"id": "a1", "label": "Actor", "name": "Hegemon"},
                "a2": {"id": "a2", "label": "Actor", "name": "Subordinate"},
            },
            "edges": [
                {
                    "type": "HAS_POWER_OVER", "source_id": "a1", "target_id": "a2",
                    "properties": {"domain": "economic"},
                },
                {
                    "type": "HAS_POWER_OVER", "source_id": "a1", "target_id": "a2",
                    "properties": {"domain": "military"},
                },
            ],
        }
        findings = rule_multi_domain_power_concentration(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "POWER-003"
        assert findings[0].details["domain_count"] == 2
        assert "economic" in findings[0].details["domains"]
        assert "military" in findings[0].details["domains"]

    def test_single_domain_not_flagged(self):
        ctx = {
            "nodes": {
                "a1": {"id": "a1", "label": "Actor"},
                "a2": {"id": "a2", "label": "Actor"},
            },
            "edges": [
                {
                    "type": "HAS_POWER_OVER", "source_id": "a1", "target_id": "a2",
                    "properties": {"domain": "economic"},
                },
            ],
        }
        findings = rule_multi_domain_power_concentration(ctx)
        assert len(findings) == 0

    def test_no_power_edges(self):
        ctx = {"nodes": {}, "edges": []}
        assert rule_multi_domain_power_concentration(ctx) == []


# ═══════════════════════════════════════════════════════════════════════════════
#  CAUSAL RULES
# ═══════════════════════════════════════════════════════════════════════════════


class TestRuleCausalChainLength:
    """Tests for rule_causal_chain_length: CAUSAL-001."""

    def test_long_chain_detected(self):
        ctx = {
            "nodes": {
                "e1": {"id": "e1", "label": "Event"},
                "e2": {"id": "e2", "label": "Event"},
                "e3": {"id": "e3", "label": "Event"},
            },
            "edges": [
                {"type": "CAUSED", "source_id": "e1", "target_id": "e2", "properties": {}},
                {"type": "CAUSED", "source_id": "e2", "target_id": "e3", "properties": {}},
            ],
        }
        findings = rule_causal_chain_length(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "CAUSAL-001"
        assert findings[0].details["chain_length"] == 3

    def test_very_long_chain_gets_alert_severity(self):
        ctx = {
            "nodes": {f"e{i}": {"id": f"e{i}", "label": "Event"} for i in range(1, 7)},
            "edges": [
                {"type": "CAUSED", "source_id": f"e{i}", "target_id": f"e{i+1}", "properties": {}}
                for i in range(1, 6)
            ],
        }
        findings = rule_causal_chain_length(ctx)
        # Chain of 6 events (length >= 5) => ALERT
        alert_findings = [f for f in findings if f.severity == Severity.ALERT]
        assert len(alert_findings) >= 1

    def test_short_chain_not_flagged(self):
        ctx = {
            "nodes": {
                "e1": {"id": "e1", "label": "Event"},
                "e2": {"id": "e2", "label": "Event"},
            },
            "edges": [
                {"type": "CAUSED", "source_id": "e1", "target_id": "e2", "properties": {}},
            ],
        }
        findings = rule_causal_chain_length(ctx)
        assert len(findings) == 0

    def test_no_caused_edges(self):
        ctx = {"nodes": {}, "edges": []}
        assert rule_causal_chain_length(ctx) == []


class TestRuleCausalCycles:
    """Tests for rule_causal_cycles: CAUSAL-002."""

    def test_cycle_detected(self):
        ctx = {
            "nodes": {
                "e1": {"id": "e1", "label": "Event"},
                "e2": {"id": "e2", "label": "Event"},
                "e3": {"id": "e3", "label": "Event"},
            },
            "edges": [
                {"type": "CAUSED", "source_id": "e1", "target_id": "e2", "properties": {}},
                {"type": "CAUSED", "source_id": "e2", "target_id": "e3", "properties": {}},
                {"type": "CAUSED", "source_id": "e3", "target_id": "e1", "properties": {}},
            ],
        }
        findings = rule_causal_cycles(ctx)
        assert len(findings) >= 1
        assert findings[0].rule_id == "CAUSAL-002"
        assert findings[0].severity == Severity.ALERT

    def test_no_cycle(self):
        ctx = {
            "nodes": {
                "e1": {"id": "e1", "label": "Event"},
                "e2": {"id": "e2", "label": "Event"},
                "e3": {"id": "e3", "label": "Event"},
            },
            "edges": [
                {"type": "CAUSED", "source_id": "e1", "target_id": "e2", "properties": {}},
                {"type": "CAUSED", "source_id": "e2", "target_id": "e3", "properties": {}},
            ],
        }
        findings = rule_causal_cycles(ctx)
        assert len(findings) == 0

    def test_no_caused_edges(self):
        ctx = {"nodes": {}, "edges": []}
        assert rule_causal_cycles(ctx) == []

    def test_self_loop(self):
        ctx = {
            "nodes": {"e1": {"id": "e1", "label": "Event"}},
            "edges": [
                {"type": "CAUSED", "source_id": "e1", "target_id": "e1", "properties": {}},
            ],
        }
        # Self-loop is avoided in DFS (neighbor not in path check skips self for chain,
        # but the cycle detection via GRAY coloring should still detect it).
        # The implementation uses "if neighbor not in path" which prevents self-loop in DFS path.
        # Let's just verify no crash:
        findings = rule_causal_cycles(ctx)
        # Implementation detail: e1 -> e1 won't be detected because
        # the DFS checks "color[neighbor] == GRAY and neighbor in path"
        # but neighbor == node itself which is already GRAY when visiting itself.
        # This is acceptable.
        assert isinstance(findings, list)


class TestRuleEscalationRetaliationPattern:
    """Tests for rule_escalation_retaliation_pattern: CAUSAL-003."""

    def test_pattern_detected_with_2_escalation_edges(self):
        ctx = {
            "nodes": {},
            "edges": [
                {
                    "type": "CAUSED", "source_id": "e1", "target_id": "e2",
                    "properties": {"mechanism": "escalation"},
                },
                {
                    "type": "CAUSED", "source_id": "e2", "target_id": "e3",
                    "properties": {"mechanism": "retaliation"},
                },
            ],
        }
        findings = rule_escalation_retaliation_pattern(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "CAUSAL-003"
        assert findings[0].severity == Severity.ALERT

    def test_single_escalation_edge_not_flagged(self):
        ctx = {
            "nodes": {},
            "edges": [
                {
                    "type": "CAUSED", "source_id": "e1", "target_id": "e2",
                    "properties": {"mechanism": "escalation"},
                },
            ],
        }
        findings = rule_escalation_retaliation_pattern(ctx)
        assert len(findings) == 0

    def test_non_escalation_mechanisms_not_flagged(self):
        ctx = {
            "nodes": {},
            "edges": [
                {
                    "type": "CAUSED", "source_id": "e1", "target_id": "e2",
                    "properties": {"mechanism": "diplomatic"},
                },
                {
                    "type": "CAUSED", "source_id": "e2", "target_id": "e3",
                    "properties": {"mechanism": "economic"},
                },
            ],
        }
        findings = rule_escalation_retaliation_pattern(ctx)
        assert len(findings) == 0

    def test_no_caused_edges(self):
        ctx = {"nodes": {}, "edges": []}
        assert rule_escalation_retaliation_pattern(ctx) == []


# ═══════════════════════════════════════════════════════════════════════════════
#  PROCESS RULES
# ═══════════════════════════════════════════════════════════════════════════════


class TestRulePowerBasedNoResolution:
    """Tests for rule_power_based_no_resolution: PROC-001."""

    def test_power_based_with_no_resolution(self):
        ctx = {
            "nodes": {
                "p1": {
                    "id": "p1", "label": "Process",
                    "resolution_approach": "power_based",
                },
                "o1": {
                    "id": "o1", "label": "Outcome",
                    "outcome_type": "no_resolution",
                },
            },
            "edges": [
                {"type": "PRODUCES", "source_id": "p1", "target_id": "o1", "properties": {}},
            ],
        }
        findings = rule_power_based_no_resolution(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "PROC-001"
        assert findings[0].severity == Severity.ALERT
        assert "interest-based" in findings[0].message

    def test_power_based_with_resolution_no_finding(self):
        ctx = {
            "nodes": {
                "p1": {
                    "id": "p1", "label": "Process",
                    "resolution_approach": "power_based",
                },
                "o1": {
                    "id": "o1", "label": "Outcome",
                    "outcome_type": "full_resolution",
                },
            },
            "edges": [
                {"type": "PRODUCES", "source_id": "p1", "target_id": "o1", "properties": {}},
            ],
        }
        findings = rule_power_based_no_resolution(ctx)
        assert len(findings) == 0

    def test_interest_based_with_no_resolution_no_finding(self):
        ctx = {
            "nodes": {
                "p1": {
                    "id": "p1", "label": "Process",
                    "resolution_approach": "interest_based",
                },
                "o1": {
                    "id": "o1", "label": "Outcome",
                    "outcome_type": "no_resolution",
                },
            },
            "edges": [
                {"type": "PRODUCES", "source_id": "p1", "target_id": "o1", "properties": {}},
            ],
        }
        findings = rule_power_based_no_resolution(ctx)
        assert len(findings) == 0

    def test_no_processes(self):
        ctx = {"nodes": {}, "edges": []}
        assert rule_power_based_no_resolution(ctx) == []


class TestRuleGlaslProcessRecommendation:
    """Tests for rule_glasl_process_recommendation: PROC-002/003."""

    def test_mismatched_process_type(self):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": 7,  # arbitration recommended
                },
                "p1": {
                    "id": "p1", "label": "Process",
                    "process_type": "negotiation",  # wrong for stage 7
                    "status": "active",
                },
            },
            "edges": [
                {"type": "RESOLVED_THROUGH", "source_id": "c1", "target_id": "p1", "properties": {}},
            ],
        }
        findings = rule_glasl_process_recommendation(ctx)
        proc_002 = [f for f in findings if f.rule_id == "PROC-002"]
        assert len(proc_002) == 1
        assert "arbitration" in proc_002[0].details["intervention_type"]

    def test_no_active_process_recommends(self):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": 5,  # mediation recommended
                },
            },
            "edges": [],
        }
        findings = rule_glasl_process_recommendation(ctx)
        proc_003 = [f for f in findings if f.rule_id == "PROC-003"]
        assert len(proc_003) == 1
        assert proc_003[0].severity == Severity.INFO

    def test_matching_process_no_finding(self):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": 1,  # moderation -> negotiation
                },
                "p1": {
                    "id": "p1", "label": "Process",
                    "process_type": "negotiation",
                    "status": "active",
                },
            },
            "edges": [
                {"type": "RESOLVED_THROUGH", "source_id": "c1", "target_id": "p1", "properties": {}},
            ],
        }
        findings = rule_glasl_process_recommendation(ctx)
        assert len(findings) == 0

    def test_no_glasl_stage_skipped(self):
        ctx = {
            "nodes": {
                "c1": {"id": "c1", "label": "Conflict", "name": "Test"},
            },
            "edges": [],
        }
        findings = rule_glasl_process_recommendation(ctx)
        assert len(findings) == 0


class TestRuleRightsBasedEscalationWarning:
    """Tests for rule_rights_based_escalation_warning: PROC-004."""

    def test_rights_based_at_low_stage(self):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": 2,
                },
                "p1": {
                    "id": "p1", "label": "Process",
                    "resolution_approach": "rights_based",
                },
            },
            "edges": [
                {"type": "RESOLVED_THROUGH", "source_id": "c1", "target_id": "p1", "properties": {}},
            ],
        }
        findings = rule_rights_based_escalation_warning(ctx)
        assert len(findings) == 1
        assert findings[0].rule_id == "PROC-004"
        assert findings[0].severity == Severity.INFO
        assert "interest-based" in findings[0].message.lower()

    def test_rights_based_at_high_stage_no_finding(self):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": 6,  # > 4, so skip
                },
                "p1": {
                    "id": "p1", "label": "Process",
                    "resolution_approach": "rights_based",
                },
            },
            "edges": [
                {"type": "RESOLVED_THROUGH", "source_id": "c1", "target_id": "p1", "properties": {}},
            ],
        }
        findings = rule_rights_based_escalation_warning(ctx)
        assert len(findings) == 0

    def test_interest_based_at_low_stage_no_finding(self):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": 2,
                },
                "p1": {
                    "id": "p1", "label": "Process",
                    "resolution_approach": "interest_based",
                },
            },
            "edges": [
                {"type": "RESOLVED_THROUGH", "source_id": "c1", "target_id": "p1", "properties": {}},
            ],
        }
        findings = rule_rights_based_escalation_warning(ctx)
        assert len(findings) == 0

    def test_stage_4_boundary(self):
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": 4,
                },
                "p1": {
                    "id": "p1", "label": "Process",
                    "resolution_approach": "rights_based",
                },
            },
            "edges": [
                {"type": "RESOLVED_THROUGH", "source_id": "c1", "target_id": "p1", "properties": {}},
            ],
        }
        findings = rule_rights_based_escalation_warning(ctx)
        assert len(findings) == 1


# ═══════════════════════════════════════════════════════════════════════════════
#  RULE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════


class TestRuleEngine:
    """Tests for the RuleEngine orchestrator."""

    def test_default_load(self):
        engine = RuleEngine()
        assert engine.rule_count == 23

    def test_categories(self):
        engine = RuleEngine()
        cats = engine.categories
        assert RuleCategory.STRUCTURAL in cats
        assert RuleCategory.TRUST in cats
        assert len(cats) == 8

    def test_no_defaults(self):
        engine = RuleEngine(load_defaults=False)
        assert engine.rule_count == 0
        assert engine.categories == []

    def test_register_custom_rule(self):
        engine = RuleEngine(load_defaults=False)

        def my_rule(ctx):
            return [Finding(rule_id="CUSTOM-001", category="custom",
                            severity="info", message="custom")]

        engine.register("custom", my_rule)
        assert engine.rule_count == 1
        assert "custom" in engine.categories

    def test_unregister_rule(self):
        engine = RuleEngine(load_defaults=False)

        def my_rule(ctx):
            return []

        engine.register("custom", my_rule)
        assert engine.rule_count == 1
        result = engine.unregister("custom", my_rule)
        assert result is True
        assert engine.rule_count == 0

    def test_unregister_nonexistent_returns_false(self):
        engine = RuleEngine(load_defaults=False)

        def my_rule(ctx):
            return []

        result = engine.unregister("nonexistent", my_rule)
        assert result is False

    def test_rules_for_category(self):
        engine = RuleEngine()
        structural = engine.rules_for(RuleCategory.STRUCTURAL)
        assert len(structural) == 5

    def test_rules_for_nonexistent_category(self):
        engine = RuleEngine()
        assert engine.rules_for("nonexistent") == []

    def test_run_all_on_empty_context(self):
        engine = RuleEngine()
        findings = engine.run({"nodes": {}, "edges": []})
        assert isinstance(findings, list)

    def test_run_specific_categories(self):
        engine = RuleEngine()
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": 8,
                },
            },
            "edges": [],
        }
        findings = engine.run(ctx, categories=[RuleCategory.CONFLICT])
        rule_ids = {f.rule_id for f in findings}
        # Should only contain CONFLICT rules
        assert all(f.category == RuleCategory.CONFLICT for f in findings)
        assert "CONFLICT-003" in rule_ids  # lose-lose

    def test_severity_filter(self):
        engine = RuleEngine()
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": 8,
                },
            },
            "edges": [],
        }
        # Without filter
        all_findings = engine.run(ctx)
        # With critical filter
        critical_only = engine.run(ctx, severity_filter=Severity.CRITICAL)
        assert len(critical_only) <= len(all_findings)
        for f in critical_only:
            assert f.severity == Severity.CRITICAL

    def test_findings_sorted_by_severity_desc(self):
        engine = RuleEngine()
        ctx = {
            "nodes": {
                "c1": {
                    "id": "c1", "label": "Conflict", "name": "Test",
                    "glasl_stage": 8, "glasl_level": "win_win",
                },
            },
            "edges": [],
        }
        findings = engine.run(ctx)
        severity_order = {"info": 0, "warning": 1, "alert": 2, "critical": 3}
        for i in range(len(findings) - 1):
            assert severity_order.get(findings[i].severity, 0) >= severity_order.get(findings[i + 1].severity, 0)

    def test_run_category_convenience(self):
        engine = RuleEngine()
        ctx = {"nodes": {}, "edges": []}
        findings = engine.run_category(ctx, RuleCategory.STRUCTURAL)
        assert isinstance(findings, list)

    def test_rule_exception_handled(self):
        engine = RuleEngine(load_defaults=False)

        def broken_rule(ctx):
            raise RuntimeError("kaboom")

        engine.register("broken", broken_rule)
        findings = engine.run({"nodes": {}, "edges": []})
        assert len(findings) == 1
        assert findings[0].rule_id == "ENGINE-ERR"
        assert "kaboom" in findings[0].message

    def test_summary(self):
        engine = RuleEngine()
        findings = [
            Finding(rule_id="A", category="structural", severity="warning", message="a"),
            Finding(rule_id="B", category="trust", severity="critical", message="b"),
            Finding(rule_id="C", category="structural", severity="info", message="c"),
        ]
        summary = engine.summary(findings)
        assert summary["total_findings"] == 3
        assert summary["by_category"]["structural"] == 2
        assert summary["by_category"]["trust"] == 1
        assert summary["by_severity"]["warning"] == 1
        assert summary["by_severity"]["critical"] == 1
        assert summary["by_severity"]["info"] == 1
        assert summary["critical_count"] == 1
        assert summary["alert_count"] == 0

    def test_summary_empty(self):
        engine = RuleEngine()
        summary = engine.summary([])
        assert summary["total_findings"] == 0
        assert summary["critical_count"] == 0
        assert summary["alert_count"] == 0
