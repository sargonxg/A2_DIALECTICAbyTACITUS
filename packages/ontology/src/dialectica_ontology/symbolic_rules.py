"""
Symbolic Rules Engine — Codified conflict grammar rules from the TACITUS ontology.

Implements deterministic rule functions for:
  STRUCTURAL_RULES: Basic graph structure validation
  ESCALATION_RULES: Glasl stage transition detection, rapid escalation alerts
  RIPENESS_RULES: Zartman ripeness theory (MHS + MEO detection)
  TRUST_RULES: Trust deficit and breach detection (Mayer/Davis/Schoorman)
  POWER_RULES: Power asymmetry analysis
  CAUSAL_RULES: Causal chain analysis (Event-CAUSED-Event paths)
  PROCESS_RULES: Stage-appropriate intervention recommendations
  CONFLICT_RULES: Glasl level derivation from stage

Each rule is a Python function that takes graph state and returns findings/alerts.
Rules fire deterministically BEFORE neural inference (neurosymbolic priority order).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Callable

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

GraphContext = dict[str, Any]
"""
Expected GraphContext structure:
{
    "nodes": {
        "<node_id>": {"id": str, "label": str, ...node properties},
        ...
    },
    "edges": [
        {"type": str, "source_id": str, "target_id": str, "properties": dict},
        ...
    ],
}
"""


# ---------------------------------------------------------------------------
# Finding — the output of every rule
# ---------------------------------------------------------------------------

class Severity(StrEnum):
    """Severity levels for rule findings."""
    INFO = "info"
    WARNING = "warning"
    ALERT = "alert"
    CRITICAL = "critical"


class RuleCategory(StrEnum):
    """Categories matching the ontology SYMBOLIC_RULES sections."""
    STRUCTURAL = "structural"
    ESCALATION = "escalation"
    RIPENESS = "ripeness"
    TRUST = "trust"
    POWER = "power"
    CAUSAL = "causal"
    PROCESS = "process"
    CONFLICT = "conflict"


@dataclass
class Finding:
    """A single finding produced by a symbolic rule."""
    rule_id: str
    category: str
    severity: str
    message: str
    affected_entities: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

RuleFunction = Callable[[GraphContext], list[Finding]]


def _nodes_by_label(ctx: GraphContext, label: str) -> dict[str, dict[str, Any]]:
    """Return all nodes whose 'label' matches *label*."""
    return {
        nid: n for nid, n in ctx.get("nodes", {}).items()
        if n.get("label") == label
    }


def _edges_by_type(ctx: GraphContext, edge_type: str) -> list[dict[str, Any]]:
    """Return all edges whose 'type' matches *edge_type*."""
    return [e for e in ctx.get("edges", []) if e.get("type") == edge_type]


def _get_node(ctx: GraphContext, node_id: str) -> dict[str, Any] | None:
    return ctx.get("nodes", {}).get(node_id)


# ═══════════════════════════════════════════════════════════════════════════
#  STRUCTURAL RULES — Basic graph structure validation
# ═══════════════════════════════════════════════════════════════════════════

def rule_conflict_has_parties(ctx: GraphContext) -> list[Finding]:
    """Every Conflict node must have at least 2 PARTY_TO edges (actors)."""
    findings: list[Finding] = []
    conflicts = _nodes_by_label(ctx, "Conflict")
    party_edges = _edges_by_type(ctx, "PARTY_TO")

    for cid, conflict in conflicts.items():
        party_count = sum(1 for e in party_edges if e.get("target_id") == cid)
        if party_count < 2:
            findings.append(Finding(
                rule_id="STRUCT-001",
                category=RuleCategory.STRUCTURAL,
                severity=Severity.WARNING,
                message=(
                    f"Conflict '{conflict.get('name', cid)}' has {party_count} "
                    f"party/parties — expected at least 2."
                ),
                affected_entities=[cid],
                details={"party_count": party_count},
            ))
    return findings


def rule_event_has_timestamp(ctx: GraphContext) -> list[Finding]:
    """Every Event node must have an occurred_at timestamp."""
    findings: list[Finding] = []
    events = _nodes_by_label(ctx, "Event")
    for eid, event in events.items():
        if not event.get("occurred_at"):
            findings.append(Finding(
                rule_id="STRUCT-002",
                category=RuleCategory.STRUCTURAL,
                severity=Severity.WARNING,
                message=f"Event '{eid}' is missing 'occurred_at' timestamp.",
                affected_entities=[eid],
            ))
    return findings


def rule_edge_endpoints_exist(ctx: GraphContext) -> list[Finding]:
    """Every edge must reference source and target nodes that exist in the graph."""
    findings: list[Finding] = []
    nodes = ctx.get("nodes", {})
    for edge in ctx.get("edges", []):
        src = edge.get("source_id")
        tgt = edge.get("target_id")
        missing: list[str] = []
        if src and src not in nodes:
            missing.append(f"source '{src}'")
        if tgt and tgt not in nodes:
            missing.append(f"target '{tgt}'")
        if missing:
            findings.append(Finding(
                rule_id="STRUCT-003",
                category=RuleCategory.STRUCTURAL,
                severity=Severity.WARNING,
                message=(
                    f"Edge '{edge.get('type', '?')}' references missing node(s): "
                    f"{', '.join(missing)}."
                ),
                affected_entities=[src or "", tgt or ""],
                details={"edge": edge},
            ))
    return findings


def rule_process_has_conflict(ctx: GraphContext) -> list[Finding]:
    """Every Process should be linked to a Conflict via RESOLVED_THROUGH."""
    findings: list[Finding] = []
    processes = _nodes_by_label(ctx, "Process")
    resolved_edges = _edges_by_type(ctx, "RESOLVED_THROUGH")
    linked_process_ids = {e.get("target_id") for e in resolved_edges}

    for pid in processes:
        if pid not in linked_process_ids:
            findings.append(Finding(
                rule_id="STRUCT-004",
                category=RuleCategory.STRUCTURAL,
                severity=Severity.INFO,
                message=f"Process '{pid}' is not linked to any Conflict via RESOLVED_THROUGH.",
                affected_entities=[pid],
            ))
    return findings


def rule_outcome_has_process(ctx: GraphContext) -> list[Finding]:
    """Every Outcome should be linked to a Process via PRODUCES."""
    findings: list[Finding] = []
    outcomes = _nodes_by_label(ctx, "Outcome")
    produces_edges = _edges_by_type(ctx, "PRODUCES")
    linked_outcome_ids = {e.get("target_id") for e in produces_edges}

    for oid in outcomes:
        if oid not in linked_outcome_ids:
            findings.append(Finding(
                rule_id="STRUCT-005",
                category=RuleCategory.STRUCTURAL,
                severity=Severity.INFO,
                message=f"Outcome '{oid}' is not linked to any Process via PRODUCES.",
                affected_entities=[oid],
            ))
    return findings


# ═══════════════════════════════════════════════════════════════════════════
#  CONFLICT RULES — Glasl level derivation
# ═══════════════════════════════════════════════════════════════════════════

def rule_glasl_level_derivation(ctx: GraphContext) -> list[Finding]:
    """
    IF glasl_stage IN [1,2,3] THEN glasl_level = 'win_win'
    IF glasl_stage IN [4,5,6] THEN glasl_level = 'win_lose'
    IF glasl_stage IN [7,8,9] THEN glasl_level = 'lose_lose'

    Flags mismatches between stored glasl_level and the derived value.
    """
    findings: list[Finding] = []
    conflicts = _nodes_by_label(ctx, "Conflict")

    for cid, conflict in conflicts.items():
        stage = conflict.get("glasl_stage")
        if stage is None:
            continue

        try:
            stage_int = int(stage)
        except (TypeError, ValueError):
            findings.append(Finding(
                rule_id="CONFLICT-001",
                category=RuleCategory.CONFLICT,
                severity=Severity.WARNING,
                message=f"Conflict '{cid}' has non-integer glasl_stage: {stage!r}.",
                affected_entities=[cid],
            ))
            continue

        if stage_int <= 3:
            derived_level = "win_win"
        elif stage_int <= 6:
            derived_level = "win_lose"
        else:
            derived_level = "lose_lose"

        stored_level = conflict.get("glasl_level")
        if stored_level and stored_level != derived_level:
            findings.append(Finding(
                rule_id="CONFLICT-002",
                category=RuleCategory.CONFLICT,
                severity=Severity.WARNING,
                message=(
                    f"Conflict '{conflict.get('name', cid)}': glasl_level is "
                    f"'{stored_level}' but stage {stage_int} implies '{derived_level}'."
                ),
                affected_entities=[cid],
                details={"glasl_stage": stage_int, "stored_level": stored_level,
                         "derived_level": derived_level},
            ))

        # Also flag lose-lose as critical situation
        if derived_level == "lose_lose":
            findings.append(Finding(
                rule_id="CONFLICT-003",
                category=RuleCategory.CONFLICT,
                severity=Severity.CRITICAL,
                message=(
                    f"Conflict '{conflict.get('name', cid)}' is at Glasl stage "
                    f"{stage_int} (lose-lose). Destructive dynamics likely."
                ),
                affected_entities=[cid],
                details={"glasl_stage": stage_int, "glasl_level": derived_level},
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════════════
#  ESCALATION RULES — Glasl stage transition detection
# ═══════════════════════════════════════════════════════════════════════════

def rule_rapid_escalation(ctx: GraphContext) -> list[Finding]:
    """
    IF glasl_stage increases by 2+ in < 30 days THEN ALERT:rapid_escalation.

    Requires a 'conflict_history' key in the context:
    {
        "<conflict_id>": [
            {"glasl_stage": int, "timestamp": str (ISO 8601)},
            ...
        ]
    }
    """
    findings: list[Finding] = []
    history = ctx.get("conflict_history", {})

    for cid, records in history.items():
        if not records or len(records) < 2:
            continue

        # Sort by timestamp ascending
        sorted_records = sorted(records, key=lambda r: r.get("timestamp", ""))

        for i in range(1, len(sorted_records)):
            prev = sorted_records[i - 1]
            curr = sorted_records[i]

            try:
                prev_stage = int(prev["glasl_stage"])
                curr_stage = int(curr["glasl_stage"])
                prev_ts = datetime.fromisoformat(prev["timestamp"])
                curr_ts = datetime.fromisoformat(curr["timestamp"])
            except (KeyError, TypeError, ValueError):
                continue

            stage_jump = curr_stage - prev_stage
            elapsed = curr_ts - prev_ts

            if stage_jump >= 2 and elapsed <= timedelta(days=30):
                conflict = _get_node(ctx, cid)
                findings.append(Finding(
                    rule_id="ESCAL-001",
                    category=RuleCategory.ESCALATION,
                    severity=Severity.ALERT,
                    message=(
                        f"RAPID ESCALATION: Conflict "
                        f"'{conflict.get('name', cid) if conflict else cid}' "
                        f"jumped from Glasl stage {prev_stage} to {curr_stage} "
                        f"in {elapsed.days} days (threshold: 2+ stages in 30 days)."
                    ),
                    affected_entities=[cid],
                    details={
                        "previous_stage": prev_stage,
                        "current_stage": curr_stage,
                        "days_elapsed": elapsed.days,
                        "previous_timestamp": prev["timestamp"],
                        "current_timestamp": curr["timestamp"],
                    },
                ))

    return findings


def rule_escalation_trajectory(ctx: GraphContext) -> list[Finding]:
    """Detect consistent escalation pattern (stage increasing over 3+ observations)."""
    findings: list[Finding] = []
    history = ctx.get("conflict_history", {})

    for cid, records in history.items():
        if not records or len(records) < 3:
            continue

        sorted_records = sorted(records, key=lambda r: r.get("timestamp", ""))
        stages = []
        for r in sorted_records:
            try:
                stages.append(int(r["glasl_stage"]))
            except (KeyError, TypeError, ValueError):
                continue

        if len(stages) < 3:
            continue

        # Check if last 3+ observations are monotonically increasing
        consecutive_increases = 0
        for i in range(1, len(stages)):
            if stages[i] > stages[i - 1]:
                consecutive_increases += 1
            else:
                consecutive_increases = 0

        if consecutive_increases >= 2:
            conflict = _get_node(ctx, cid)
            findings.append(Finding(
                rule_id="ESCAL-002",
                category=RuleCategory.ESCALATION,
                severity=Severity.WARNING,
                message=(
                    f"Escalation trajectory: Conflict "
                    f"'{conflict.get('name', cid) if conflict else cid}' "
                    f"has {consecutive_increases + 1} consecutive stage increases "
                    f"({stages[-consecutive_increases - 1]} -> {stages[-1]})."
                ),
                affected_entities=[cid],
                details={"stage_history": stages,
                         "consecutive_increases": consecutive_increases},
            ))

    return findings


def rule_stage_regression_alert(ctx: GraphContext) -> list[Finding]:
    """Detect de-escalation (stage decrease) — positive but worth noting."""
    findings: list[Finding] = []
    history = ctx.get("conflict_history", {})

    for cid, records in history.items():
        if not records or len(records) < 2:
            continue

        sorted_records = sorted(records, key=lambda r: r.get("timestamp", ""))

        prev = sorted_records[-2]
        curr = sorted_records[-1]

        try:
            prev_stage = int(prev["glasl_stage"])
            curr_stage = int(curr["glasl_stage"])
        except (KeyError, TypeError, ValueError):
            continue

        if curr_stage < prev_stage:
            conflict = _get_node(ctx, cid)
            findings.append(Finding(
                rule_id="ESCAL-003",
                category=RuleCategory.ESCALATION,
                severity=Severity.INFO,
                message=(
                    f"De-escalation detected: Conflict "
                    f"'{conflict.get('name', cid) if conflict else cid}' "
                    f"moved from stage {prev_stage} to {curr_stage}."
                ),
                affected_entities=[cid],
                details={"previous_stage": prev_stage, "current_stage": curr_stage},
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════════════
#  RIPENESS RULES — Zartman ripeness theory
# ═══════════════════════════════════════════════════════════════════════════

def rule_mutually_hurting_stalemate(ctx: GraphContext) -> list[Finding]:
    """
    Detect Mutually Hurting Stalemate (MHS) — Zartman ripeness theory.

    Heuristic: Conflict is in 'stalemate' Kriesberg phase, or has high intensity
    with no recent resolution process activity, and both parties experience
    negative emotional states.
    """
    findings: list[Finding] = []
    conflicts = _nodes_by_label(ctx, "Conflict")
    resolved_edges = _edges_by_type(ctx, "RESOLVED_THROUGH")
    party_edges = _edges_by_type(ctx, "PARTY_TO")
    experience_edges = _edges_by_type(ctx, "EXPERIENCES")

    for cid, conflict in conflicts.items():
        is_stalemate = conflict.get("kriesberg_phase") == "stalemate"
        is_high_intensity = conflict.get("intensity") in ("high", "severe", "extreme")

        if not (is_stalemate or is_high_intensity):
            continue

        # Check for active resolution processes
        active_processes = [
            e for e in resolved_edges
            if e.get("target_id") == cid or e.get("source_id") == cid
        ]
        has_active_process = False
        for pe in active_processes:
            proc_id = pe.get("target_id")
            proc = _get_node(ctx, proc_id)
            if proc and proc.get("status") == "active":
                has_active_process = True
                break

        if has_active_process:
            continue

        # Check party emotional states — look for negative emotions
        parties = [e.get("source_id") for e in party_edges if e.get("target_id") == cid]
        negative_emotions = {"anger", "fear", "sadness", "disgust"}
        parties_hurting = 0
        for actor_id in parties:
            actor_emotions = [
                e for e in experience_edges if e.get("source_id") == actor_id
            ]
            for em_edge in actor_emotions:
                em_node = _get_node(ctx, em_edge.get("target_id", ""))
                if em_node and em_node.get("primary_emotion") in negative_emotions:
                    parties_hurting += 1
                    break

        if parties_hurting >= 2 or (is_stalemate and len(parties) >= 2):
            findings.append(Finding(
                rule_id="RIPE-001",
                category=RuleCategory.RIPENESS,
                severity=Severity.ALERT,
                message=(
                    f"Mutually Hurting Stalemate detected for conflict "
                    f"'{conflict.get('name', cid)}': "
                    f"{'stalemate phase' if is_stalemate else 'high intensity'}, "
                    f"{parties_hurting}/{len(parties)} parties in negative emotional state, "
                    f"no active resolution process."
                ),
                affected_entities=[cid] + parties,
                details={
                    "kriesberg_phase": conflict.get("kriesberg_phase"),
                    "intensity": conflict.get("intensity"),
                    "parties_hurting": parties_hurting,
                    "total_parties": len(parties),
                },
            ))

    return findings


def rule_mutually_enticing_opportunity(ctx: GraphContext) -> list[Finding]:
    """
    Detect Mutually Enticing Opportunity (MEO) — Zartman ripeness theory.

    Heuristic: Parties share overlapping interests, or a recent cooperative
    event has occurred, suggesting a window for resolution.
    """
    findings: list[Finding] = []
    conflicts = _nodes_by_label(ctx, "Conflict")
    party_edges = _edges_by_type(ctx, "PARTY_TO")
    interest_edges = _edges_by_type(ctx, "HAS_INTEREST")
    event_edges = _edges_by_type(ctx, "PART_OF")
    events = _nodes_by_label(ctx, "Event")

    cooperative_event_types = {"agree", "consult", "support", "cooperate", "aid", "yield"}

    for cid, conflict in conflicts.items():
        parties = [e.get("source_id") for e in party_edges if e.get("target_id") == cid]
        if len(parties) < 2:
            continue

        # Check for overlapping interests
        party_interests: dict[str, set[str]] = {}
        for actor_id in parties:
            interests = set()
            for ie in interest_edges:
                if ie.get("source_id") == actor_id:
                    interest_node = _get_node(ctx, ie.get("target_id", ""))
                    if interest_node:
                        interests.add(ie.get("target_id", ""))
            party_interests[actor_id] = interests

        # Find shared interests (same Interest node referenced by multiple parties)
        all_interests = [v for v in party_interests.values() if v]
        shared = set.intersection(*all_interests) if len(all_interests) >= 2 else set()

        # Check for recent cooperative events in this conflict
        conflict_event_ids = {
            e.get("source_id") for e in event_edges if e.get("target_id") == cid
        }
        cooperative_events = [
            eid for eid, ev in events.items()
            if eid in conflict_event_ids
            and ev.get("event_type") in cooperative_event_types
        ]

        if shared or cooperative_events:
            findings.append(Finding(
                rule_id="RIPE-002",
                category=RuleCategory.RIPENESS,
                severity=Severity.INFO,
                message=(
                    f"Mutually Enticing Opportunity detected for conflict "
                    f"'{conflict.get('name', cid)}': "
                    f"{len(shared)} shared interest(s), "
                    f"{len(cooperative_events)} cooperative event(s). "
                    f"Window for resolution may exist."
                ),
                affected_entities=[cid] + parties,
                details={
                    "shared_interest_ids": list(shared),
                    "cooperative_event_ids": cooperative_events,
                },
            ))

    return findings


def rule_ripeness_window(ctx: GraphContext) -> list[Finding]:
    """
    Combined ripeness check: if both MHS and MEO indicators are present,
    the conflict is 'ripe' for intervention per Zartman theory.
    """
    mhs_findings = rule_mutually_hurting_stalemate(ctx)
    meo_findings = rule_mutually_enticing_opportunity(ctx)

    mhs_conflicts = {
        f.affected_entities[0] for f in mhs_findings if f.affected_entities
    }
    meo_conflicts = {
        f.affected_entities[0] for f in meo_findings if f.affected_entities
    }

    ripe = mhs_conflicts & meo_conflicts
    findings: list[Finding] = []
    for cid in ripe:
        conflict = _get_node(ctx, cid) if ctx.get("nodes") else None  # type: ignore[redundant-expr]
        findings.append(Finding(
            rule_id="RIPE-003",
            category=RuleCategory.RIPENESS,
            severity=Severity.CRITICAL,
            message=(
                f"RIPE FOR INTERVENTION: Conflict "
                f"'{conflict.get('name', cid) if conflict else cid}' shows both "
                f"Mutually Hurting Stalemate AND Mutually Enticing Opportunity. "
                f"Zartman ripeness conditions met."
            ),
            affected_entities=[cid],
        ))

    return findings


# ═══════════════════════════════════════════════════════════════════════════
#  TRUST RULES — Mayer/Davis/Schoorman model
# ═══════════════════════════════════════════════════════════════════════════

# Default weights from Mayer/Davis/Schoorman literature
_TRUST_W1_ABILITY = 0.30
_TRUST_W2_BENEVOLENCE = 0.30
_TRUST_W3_INTEGRITY = 0.40

_TRUST_DEFICIT_THRESHOLD = 0.3
_TRUST_BREACH_INTEGRITY_DROP = 0.3


def compute_overall_trust(
    propensity_to_trust: float,
    ability: float,
    benevolence: float,
    integrity: float,
    w1: float = _TRUST_W1_ABILITY,
    w2: float = _TRUST_W2_BENEVOLENCE,
    w3: float = _TRUST_W3_INTEGRITY,
) -> float:
    """
    overall_trust = propensity_to_trust x (w1*ability + w2*benevolence + w3*integrity)

    Mayer/Davis/Schoorman integrative trust formula.
    """
    composite = w1 * ability + w2 * benevolence + w3 * integrity
    return propensity_to_trust * composite


def rule_trust_deficit(ctx: GraphContext) -> list[Finding]:
    """IF overall_trust < 0.3 THEN flag: trust_deficit."""
    findings: list[Finding] = []
    trust_states = _nodes_by_label(ctx, "TrustState")
    trusts_edges = _edges_by_type(ctx, "TRUSTS")

    for tsid, ts in trust_states.items():
        overall = ts.get("overall_trust")
        if overall is None:
            continue

        try:
            trust_val = float(overall)
        except (TypeError, ValueError):
            continue

        if trust_val < _TRUST_DEFICIT_THRESHOLD:
            # Find which actors are involved
            involved_actors: list[str] = []
            for edge in trusts_edges:
                edge_trust_id = edge.get("properties", {}).get("trust_state_id")
                if edge_trust_id == tsid:
                    involved_actors.extend([
                        edge.get("source_id", ""),
                        edge.get("target_id", ""),
                    ])

            findings.append(Finding(
                rule_id="TRUST-001",
                category=RuleCategory.TRUST,
                severity=Severity.ALERT,
                message=(
                    f"TRUST DEFICIT: TrustState '{tsid}' has overall_trust = "
                    f"{trust_val:.2f} (below threshold {_TRUST_DEFICIT_THRESHOLD}). "
                    f"Meaningful cooperation unlikely without trust-building."
                ),
                affected_entities=[tsid] + involved_actors,
                details={
                    "overall_trust": trust_val,
                    "threshold": _TRUST_DEFICIT_THRESHOLD,
                    "ability": ts.get("perceived_ability"),
                    "benevolence": ts.get("perceived_benevolence"),
                    "integrity": ts.get("perceived_integrity"),
                },
            ))

    return findings


def rule_trust_breach_event(ctx: GraphContext) -> list[Finding]:
    """
    IF perceived_integrity drops > 0.3 in single assessment THEN flag: trust_breach_event.

    Requires 'trust_history' key in context:
    {
        "<trust_state_id>": [
            {"perceived_integrity": float, "timestamp": str},
            ...
        ]
    }
    """
    findings: list[Finding] = []
    history = ctx.get("trust_history", {})

    for tsid, records in history.items():
        if not records or len(records) < 2:
            continue

        sorted_records = sorted(records, key=lambda r: r.get("timestamp", ""))

        for i in range(1, len(sorted_records)):
            prev = sorted_records[i - 1]
            curr = sorted_records[i]

            try:
                prev_integrity = float(prev["perceived_integrity"])
                curr_integrity = float(curr["perceived_integrity"])
            except (KeyError, TypeError, ValueError):
                continue

            drop = prev_integrity - curr_integrity

            if drop > _TRUST_BREACH_INTEGRITY_DROP:
                findings.append(Finding(
                    rule_id="TRUST-002",
                    category=RuleCategory.TRUST,
                    severity=Severity.CRITICAL,
                    message=(
                        f"TRUST BREACH EVENT: TrustState '{tsid}' — perceived_integrity "
                        f"dropped from {prev_integrity:.2f} to {curr_integrity:.2f} "
                        f"(delta: {drop:.2f}, threshold: {_TRUST_BREACH_INTEGRITY_DROP}). "
                        f"Likely breach of trust event."
                    ),
                    affected_entities=[tsid],
                    details={
                        "previous_integrity": prev_integrity,
                        "current_integrity": curr_integrity,
                        "integrity_drop": drop,
                        "threshold": _TRUST_BREACH_INTEGRITY_DROP,
                        "previous_timestamp": prev.get("timestamp"),
                        "current_timestamp": curr.get("timestamp"),
                    },
                ))

    return findings


def rule_trust_formula_validation(ctx: GraphContext) -> list[Finding]:
    """
    Validate that stored overall_trust is consistent with the Mayer formula:
    overall_trust ~= propensity_to_trust * (w1*ability + w2*benevolence + w3*integrity).

    Tolerance: 0.1 absolute difference.
    """
    findings: list[Finding] = []
    trust_states = _nodes_by_label(ctx, "TrustState")

    for tsid, ts in trust_states.items():
        propensity = ts.get("propensity_to_trust")
        ability = ts.get("perceived_ability")
        benevolence = ts.get("perceived_benevolence")
        integrity = ts.get("perceived_integrity")
        stored_overall = ts.get("overall_trust")

        if any(v is None for v in [propensity, ability, benevolence, integrity, stored_overall]):
            continue

        try:
            computed = compute_overall_trust(
                float(propensity), float(ability),
                float(benevolence), float(integrity),
            )
            stored = float(stored_overall)
        except (TypeError, ValueError):
            continue

        if abs(computed - stored) > 0.1:
            findings.append(Finding(
                rule_id="TRUST-003",
                category=RuleCategory.TRUST,
                severity=Severity.WARNING,
                message=(
                    f"TrustState '{tsid}': stored overall_trust ({stored:.2f}) differs "
                    f"from Mayer formula result ({computed:.2f}) by "
                    f"{abs(computed - stored):.2f}."
                ),
                affected_entities=[tsid],
                details={
                    "stored_overall_trust": stored,
                    "computed_overall_trust": computed,
                    "propensity_to_trust": float(propensity),
                    "ability": float(ability),
                    "benevolence": float(benevolence),
                    "integrity": float(integrity),
                },
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════════════
#  POWER RULES — Power asymmetry analysis
# ═══════════════════════════════════════════════════════════════════════════

_POWER_ASYMMETRY_THRESHOLD = 0.6


def rule_power_asymmetry(ctx: GraphContext) -> list[Finding]:
    """
    Detect significant power asymmetry between conflict parties.

    Examines HAS_POWER_OVER edges and PowerDynamic nodes for high-magnitude
    relationships between actors in the same conflict.
    """
    findings: list[Finding] = []
    power_edges = _edges_by_type(ctx, "HAS_POWER_OVER")
    power_dynamics = _nodes_by_label(ctx, "PowerDynamic")
    party_edges = _edges_by_type(ctx, "PARTY_TO")
    conflicts = _nodes_by_label(ctx, "Conflict")

    # Map actors to their conflicts
    actor_conflicts: dict[str, set[str]] = {}
    for pe in party_edges:
        actor_id = pe.get("source_id", "")
        conflict_id = pe.get("target_id", "")
        actor_conflicts.setdefault(actor_id, set()).add(conflict_id)

    for edge in power_edges:
        src = edge.get("source_id", "")
        tgt = edge.get("target_id", "")

        # Get magnitude from edge properties or linked PowerDynamic node
        magnitude = edge.get("properties", {}).get("magnitude")
        pd_id = edge.get("properties", {}).get("power_dynamic_id")
        if magnitude is None and pd_id and pd_id in power_dynamics:
            magnitude = power_dynamics[pd_id].get("magnitude")

        if magnitude is None:
            continue

        try:
            mag_val = float(magnitude)
        except (TypeError, ValueError):
            continue

        if mag_val < _POWER_ASYMMETRY_THRESHOLD:
            continue

        # Find shared conflicts
        src_conflicts = actor_conflicts.get(src, set())
        tgt_conflicts = actor_conflicts.get(tgt, set())
        shared_conflicts = src_conflicts & tgt_conflicts

        domain = edge.get("properties", {}).get("domain", "unspecified")

        for shared_cid in shared_conflicts:
            src_node = _get_node(ctx, src)
            tgt_node = _get_node(ctx, tgt)
            findings.append(Finding(
                rule_id="POWER-001",
                category=RuleCategory.POWER,
                severity=Severity.WARNING,
                message=(
                    f"Power asymmetry in conflict "
                    f"'{conflicts.get(shared_cid, {}).get('name', shared_cid)}': "
                    f"'{src_node.get('name', src) if src_node else src}' has "
                    f"{domain} power over "
                    f"'{tgt_node.get('name', tgt) if tgt_node else tgt}' "
                    f"(magnitude: {mag_val:.2f}). "
                    f"Power-based dynamics may impede interest-based resolution."
                ),
                affected_entities=[shared_cid, src, tgt],
                details={
                    "domain": domain,
                    "magnitude": mag_val,
                    "source_actor": src,
                    "target_actor": tgt,
                    "threshold": _POWER_ASYMMETRY_THRESHOLD,
                },
            ))

        # Also flag even without shared conflict context
        if not shared_conflicts:
            findings.append(Finding(
                rule_id="POWER-002",
                category=RuleCategory.POWER,
                severity=Severity.INFO,
                message=(
                    f"Significant power relationship detected: "
                    f"'{src}' has {domain} power over '{tgt}' "
                    f"(magnitude: {mag_val:.2f})."
                ),
                affected_entities=[src, tgt],
                details={"domain": domain, "magnitude": mag_val},
            ))

    return findings


def rule_multi_domain_power_concentration(ctx: GraphContext) -> list[Finding]:
    """
    Flag when one actor holds power over another across multiple domains,
    indicating structural dominance.
    """
    findings: list[Finding] = []
    power_edges = _edges_by_type(ctx, "HAS_POWER_OVER")

    # Group by (source, target)
    pair_domains: dict[tuple[str, str], list[str]] = {}
    for edge in power_edges:
        src = edge.get("source_id", "")
        tgt = edge.get("target_id", "")
        domain = edge.get("properties", {}).get("domain", "unspecified")
        pair_domains.setdefault((src, tgt), []).append(domain)

    for (src, tgt), domains in pair_domains.items():
        if len(domains) >= 2:
            src_node = _get_node(ctx, src)
            tgt_node = _get_node(ctx, tgt)
            findings.append(Finding(
                rule_id="POWER-003",
                category=RuleCategory.POWER,
                severity=Severity.WARNING,
                message=(
                    f"Multi-domain power concentration: "
                    f"'{src_node.get('name', src) if src_node else src}' holds "
                    f"power over '{tgt_node.get('name', tgt) if tgt_node else tgt}' "
                    f"across {len(domains)} domains: {', '.join(domains)}."
                ),
                affected_entities=[src, tgt],
                details={"domains": domains, "domain_count": len(domains)},
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════════════
#  CAUSAL RULES — Causal chain analysis
# ═══════════════════════════════════════════════════════════════════════════

def rule_causal_chain_length(ctx: GraphContext) -> list[Finding]:
    """
    Detect long causal chains (Event -CAUSED-> Event paths of length >= 3).
    Long chains may indicate systemic escalation spirals.
    """
    findings: list[Finding] = []
    caused_edges = _edges_by_type(ctx, "CAUSED")

    if not caused_edges:
        return findings

    # Build adjacency list for CAUSED edges
    adj: dict[str, list[str]] = {}
    for edge in caused_edges:
        src = edge.get("source_id", "")
        tgt = edge.get("target_id", "")
        adj.setdefault(src, []).append(tgt)

    # Find all root events (events that are sources but not targets in CAUSED)
    targets = {edge.get("target_id", "") for edge in caused_edges}
    sources = {edge.get("source_id", "") for edge in caused_edges}
    roots = sources - targets

    # BFS/DFS from each root to find longest chains
    def _find_chains(start: str) -> list[list[str]]:
        chains: list[list[str]] = []
        stack: list[list[str]] = [[start]]
        visited_paths: set[tuple[str, ...]] = set()
        while stack:
            path = stack.pop()
            current = path[-1]
            extended = False
            for neighbor in adj.get(current, []):
                if neighbor not in path:  # Avoid cycles
                    new_path = path + [neighbor]
                    path_key = tuple(new_path)
                    if path_key not in visited_paths:
                        visited_paths.add(path_key)
                        stack.append(new_path)
                        extended = True
            if not extended and len(path) > 1:
                chains.append(path)
        return chains

    for root in roots:
        chains = _find_chains(root)
        for chain in chains:
            if len(chain) >= 3:
                findings.append(Finding(
                    rule_id="CAUSAL-001",
                    category=RuleCategory.CAUSAL,
                    severity=Severity.WARNING if len(chain) < 5 else Severity.ALERT,
                    message=(
                        f"Causal chain of length {len(chain)} detected: "
                        f"{' -> '.join(chain)}. "
                        f"May indicate escalation spiral or systemic pattern."
                    ),
                    affected_entities=chain,
                    details={"chain_length": len(chain), "chain": chain},
                ))

    return findings


def rule_causal_cycles(ctx: GraphContext) -> list[Finding]:
    """Detect causal cycles (Event A -> ... -> Event A), indicating feedback loops."""
    findings: list[Finding] = []
    caused_edges = _edges_by_type(ctx, "CAUSED")

    if not caused_edges:
        return findings

    adj: dict[str, list[str]] = {}
    for edge in caused_edges:
        src = edge.get("source_id", "")
        tgt = edge.get("target_id", "")
        adj.setdefault(src, []).append(tgt)

    # Standard DFS cycle detection
    WHITE, GRAY, BLACK = 0, 1, 2
    all_nodes = set(adj.keys())
    for edges in adj.values():
        all_nodes.update(edges)

    color: dict[str, int] = {n: WHITE for n in all_nodes}
    parent: dict[str, str | None] = {n: None for n in all_nodes}
    cycles_found: list[list[str]] = []

    def _dfs(node: str, path: list[str]) -> None:
        color[node] = GRAY
        for neighbor in adj.get(node, []):
            if color[neighbor] == GRAY and neighbor in path:
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles_found.append(cycle)
            elif color[neighbor] == WHITE:
                parent[neighbor] = node
                _dfs(neighbor, path + [neighbor])
        color[node] = BLACK

    for node in all_nodes:
        if color[node] == WHITE:
            _dfs(node, [node])

    for cycle in cycles_found:
        findings.append(Finding(
            rule_id="CAUSAL-002",
            category=RuleCategory.CAUSAL,
            severity=Severity.ALERT,
            message=(
                f"Causal feedback loop detected: {' -> '.join(cycle)}. "
                f"Self-reinforcing conflict dynamics may be present."
            ),
            affected_entities=cycle,
            details={"cycle": cycle, "cycle_length": len(cycle) - 1},
        ))

    return findings


def rule_escalation_retaliation_pattern(ctx: GraphContext) -> list[Finding]:
    """
    Detect escalation/retaliation patterns in causal chains:
    chains where the mechanism is 'escalation' or 'retaliation'.
    """
    findings: list[Finding] = []
    caused_edges = _edges_by_type(ctx, "CAUSED")

    escalation_mechanisms = {"escalation", "retaliation"}
    escalation_chains: list[dict[str, Any]] = []

    for edge in caused_edges:
        mechanism = edge.get("properties", {}).get("mechanism", "")
        if mechanism in escalation_mechanisms:
            escalation_chains.append(edge)

    if len(escalation_chains) >= 2:
        affected = set()
        for e in escalation_chains:
            affected.add(e.get("source_id", ""))
            affected.add(e.get("target_id", ""))

        findings.append(Finding(
            rule_id="CAUSAL-003",
            category=RuleCategory.CAUSAL,
            severity=Severity.ALERT,
            message=(
                f"Escalation/retaliation pattern: {len(escalation_chains)} causal "
                f"links with escalation or retaliation mechanism detected. "
                f"Tit-for-tat dynamics likely."
            ),
            affected_entities=list(affected),
            details={
                "mechanism_edges": [
                    {
                        "source": e.get("source_id"),
                        "target": e.get("target_id"),
                        "mechanism": e.get("properties", {}).get("mechanism"),
                    }
                    for e in escalation_chains
                ]
            },
        ))

    return findings


# ═══════════════════════════════════════════════════════════════════════════
#  PROCESS RULES — Glasl stage-based process recommendations
# ═══════════════════════════════════════════════════════════════════════════

# Glasl's stage-to-intervention mapping
GLASL_INTERVENTION_MAP: dict[int, str] = {
    1: "moderation",
    2: "moderation",
    3: "facilitation",
    4: "process_consultation",
    5: "mediation",
    6: "mediation",
    7: "arbitration",
    8: "power_intervention",
    9: "power_intervention",
}

# Mapping of interventions to recommended ProcessTypes
INTERVENTION_PROCESS_MAP: dict[str, list[str]] = {
    "moderation": ["negotiation"],
    "facilitation": ["mediation_facilitative", "conciliation"],
    "process_consultation": ["mediation_facilitative", "mediation_transformative", "ombuds"],
    "mediation": [
        "mediation_facilitative", "mediation_evaluative",
        "mediation_transformative", "mediation_narrative",
    ],
    "arbitration": ["arbitration", "adjudication", "early_neutral_evaluation"],
    "power_intervention": ["arbitration", "adjudication"],
}


def rule_power_based_no_resolution(ctx: GraphContext) -> list[Finding]:
    """
    IF Process.resolution_approach='power_based' AND Outcome.outcome_type='no_resolution'
    THEN recommend Process WHERE resolution_approach='interest_based'.
    """
    findings: list[Finding] = []
    processes = _nodes_by_label(ctx, "Process")
    outcomes = _nodes_by_label(ctx, "Outcome")
    produces_edges = _edges_by_type(ctx, "PRODUCES")

    for pid, proc in processes.items():
        if proc.get("resolution_approach") != "power_based":
            continue

        # Find outcomes produced by this process
        process_outcomes = [
            e.get("target_id") for e in produces_edges
            if e.get("source_id") == pid
        ]

        for oid in process_outcomes:
            outcome = outcomes.get(oid) if oid else None
            if outcome and outcome.get("outcome_type") == "no_resolution":
                findings.append(Finding(
                    rule_id="PROC-001",
                    category=RuleCategory.PROCESS,
                    severity=Severity.ALERT,
                    message=(
                        f"Power-based process '{pid}' produced 'no_resolution' "
                        f"outcome. Recommend switching to interest-based approach "
                        f"(e.g., facilitative mediation, negotiation)."
                    ),
                    affected_entities=[pid, oid],
                    details={
                        "current_approach": "power_based",
                        "recommended_approach": "interest_based",
                        "recommended_process_types": [
                            "negotiation", "mediation_facilitative",
                            "mediation_transformative",
                        ],
                    },
                ))

    return findings


def rule_glasl_process_recommendation(ctx: GraphContext) -> list[Finding]:
    """
    Recommend appropriate process types based on current Glasl stage.

    Glasl stage -> intervention type -> recommended processes.
    """
    findings: list[Finding] = []
    conflicts = _nodes_by_label(ctx, "Conflict")
    resolved_edges = _edges_by_type(ctx, "RESOLVED_THROUGH")
    processes = _nodes_by_label(ctx, "Process")

    for cid, conflict in conflicts.items():
        stage = conflict.get("glasl_stage")
        if stage is None:
            continue

        try:
            stage_int = int(stage)
        except (TypeError, ValueError):
            continue

        intervention = GLASL_INTERVENTION_MAP.get(stage_int)
        if not intervention:
            continue

        recommended_types = INTERVENTION_PROCESS_MAP.get(intervention, [])

        # Check current active processes for this conflict
        linked_process_ids = [
            e.get("target_id") for e in resolved_edges
            if e.get("source_id") == cid
        ]

        active_types: list[str] = []
        for lpid in linked_process_ids:
            proc = processes.get(lpid) if lpid else None
            if proc and proc.get("status") in ("active", "pending"):
                active_types.append(proc.get("process_type", ""))

        # Check if any active process matches recommendations
        type_match = any(at in recommended_types for at in active_types)

        if active_types and not type_match:
            findings.append(Finding(
                rule_id="PROC-002",
                category=RuleCategory.PROCESS,
                severity=Severity.WARNING,
                message=(
                    f"Conflict '{conflict.get('name', cid)}' is at Glasl stage "
                    f"{stage_int} (recommended intervention: {intervention}). "
                    f"Active process type(s) {active_types} may not be appropriate. "
                    f"Consider: {recommended_types}."
                ),
                affected_entities=[cid] + linked_process_ids,
                details={
                    "glasl_stage": stage_int,
                    "intervention_type": intervention,
                    "recommended_process_types": recommended_types,
                    "active_process_types": active_types,
                },
            ))
        elif not active_types:
            findings.append(Finding(
                rule_id="PROC-003",
                category=RuleCategory.PROCESS,
                severity=Severity.INFO,
                message=(
                    f"Conflict '{conflict.get('name', cid)}' at Glasl stage "
                    f"{stage_int} has no active resolution process. "
                    f"Recommended intervention: {intervention}. "
                    f"Suggested process types: {recommended_types}."
                ),
                affected_entities=[cid],
                details={
                    "glasl_stage": stage_int,
                    "intervention_type": intervention,
                    "recommended_process_types": recommended_types,
                },
            ))

    return findings


def rule_rights_based_escalation_warning(ctx: GraphContext) -> list[Finding]:
    """
    Ury/Brett/Goldberg: Rights-based processes are costlier than interest-based.
    Warn if rights-based processes are used when interest-based might suffice
    (Glasl stages 1-4).
    """
    findings: list[Finding] = []
    conflicts = _nodes_by_label(ctx, "Conflict")
    resolved_edges = _edges_by_type(ctx, "RESOLVED_THROUGH")
    processes = _nodes_by_label(ctx, "Process")

    for cid, conflict in conflicts.items():
        stage = conflict.get("glasl_stage")
        if stage is None:
            continue

        try:
            stage_int = int(stage)
        except (TypeError, ValueError):
            continue

        if stage_int > 4:
            continue

        linked_process_ids = [
            e.get("target_id") for e in resolved_edges
            if e.get("source_id") == cid
        ]

        for lpid in linked_process_ids:
            proc = processes.get(lpid) if lpid else None
            if proc and proc.get("resolution_approach") == "rights_based":
                findings.append(Finding(
                    rule_id="PROC-004",
                    category=RuleCategory.PROCESS,
                    severity=Severity.INFO,
                    message=(
                        f"Conflict '{conflict.get('name', cid)}' at Glasl stage "
                        f"{stage_int} is using a rights-based process. "
                        f"Interest-based approaches are typically more efficient "
                        f"at lower escalation stages (Ury/Brett/Goldberg)."
                    ),
                    affected_entities=[cid, lpid],
                    details={
                        "glasl_stage": stage_int,
                        "current_approach": "rights_based",
                        "recommended_approach": "interest_based",
                    },
                ))

    return findings


# ═══════════════════════════════════════════════════════════════════════════
#  RULE ENGINE — Registration and execution
# ═══════════════════════════════════════════════════════════════════════════

# Canonical rule registry: category -> list of rule functions
_DEFAULT_RULES: dict[str, list[RuleFunction]] = {
    RuleCategory.STRUCTURAL: [
        rule_conflict_has_parties,
        rule_event_has_timestamp,
        rule_edge_endpoints_exist,
        rule_process_has_conflict,
        rule_outcome_has_process,
    ],
    RuleCategory.CONFLICT: [
        rule_glasl_level_derivation,
    ],
    RuleCategory.ESCALATION: [
        rule_rapid_escalation,
        rule_escalation_trajectory,
        rule_stage_regression_alert,
    ],
    RuleCategory.RIPENESS: [
        rule_mutually_hurting_stalemate,
        rule_mutually_enticing_opportunity,
        rule_ripeness_window,
    ],
    RuleCategory.TRUST: [
        rule_trust_deficit,
        rule_trust_breach_event,
        rule_trust_formula_validation,
    ],
    RuleCategory.POWER: [
        rule_power_asymmetry,
        rule_multi_domain_power_concentration,
    ],
    RuleCategory.CAUSAL: [
        rule_causal_chain_length,
        rule_causal_cycles,
        rule_escalation_retaliation_pattern,
    ],
    RuleCategory.PROCESS: [
        rule_power_based_no_resolution,
        rule_glasl_process_recommendation,
        rule_rights_based_escalation_warning,
    ],
}


class RuleEngine:
    """
    Symbolic rule engine that registers and executes deterministic conflict rules.

    Rules fire BEFORE neural inference in the neurosymbolic pipeline.
    All rules are pure functions: (GraphContext) -> list[Finding].

    Usage::

        engine = RuleEngine()
        findings = engine.run(graph_context)

        # Run only specific categories
        findings = engine.run(graph_context, categories=["trust", "escalation"])

        # Add custom rules
        engine.register("custom_category", my_rule_function)
    """

    def __init__(self, *, load_defaults: bool = True) -> None:
        self._rules: dict[str, list[RuleFunction]] = {}
        if load_defaults:
            for category, fns in _DEFAULT_RULES.items():
                for fn in fns:
                    self.register(category, fn)

    def register(self, category: str, fn: RuleFunction) -> None:
        """Register a rule function under a category."""
        self._rules.setdefault(category, []).append(fn)

    def unregister(self, category: str, fn: RuleFunction) -> bool:
        """Remove a specific rule function. Returns True if found and removed."""
        rules = self._rules.get(category, [])
        try:
            rules.remove(fn)
            return True
        except ValueError:
            return False

    @property
    def categories(self) -> list[str]:
        """Return all registered categories."""
        return list(self._rules.keys())

    @property
    def rule_count(self) -> int:
        """Return total number of registered rules."""
        return sum(len(fns) for fns in self._rules.values())

    def rules_for(self, category: str) -> list[RuleFunction]:
        """Return all rule functions registered under a category."""
        return list(self._rules.get(category, []))

    def run(
        self,
        ctx: GraphContext,
        *,
        categories: list[str] | None = None,
        severity_filter: str | None = None,
    ) -> list[Finding]:
        """
        Execute all registered rules against the graph context.

        Parameters
        ----------
        ctx:
            The graph context dictionary containing nodes, edges, and
            optional history data.
        categories:
            If provided, only run rules from these categories.
        severity_filter:
            If provided, only return findings at or above this severity.
            Order: info < warning < alert < critical.

        Returns
        -------
        List of Finding objects from all executed rules, sorted by severity
        (critical first).
        """
        severity_order = {
            Severity.INFO: 0,
            Severity.WARNING: 1,
            Severity.ALERT: 2,
            Severity.CRITICAL: 3,
        }

        target_categories = categories or list(self._rules.keys())
        all_findings: list[Finding] = []

        for cat in target_categories:
            for rule_fn in self._rules.get(cat, []):
                try:
                    results = rule_fn(ctx)
                    all_findings.extend(results)
                except Exception as exc:
                    all_findings.append(Finding(
                        rule_id="ENGINE-ERR",
                        category=cat,
                        severity=Severity.WARNING,
                        message=(
                            f"Rule '{rule_fn.__name__}' raised {type(exc).__name__}: "
                            f"{exc}"
                        ),
                        affected_entities=[],
                        details={"exception": str(exc), "rule": rule_fn.__name__},
                    ))

        # Apply severity filter
        if severity_filter:
            min_level = severity_order.get(severity_filter, 0)
            all_findings = [
                f for f in all_findings
                if severity_order.get(f.severity, 0) >= min_level
            ]

        # Sort by severity descending (critical first)
        all_findings.sort(
            key=lambda f: severity_order.get(f.severity, 0),
            reverse=True,
        )

        return all_findings

    def run_category(self, ctx: GraphContext, category: str) -> list[Finding]:
        """Convenience: run only a single category of rules."""
        return self.run(ctx, categories=[category])

    def summary(self, findings: list[Finding]) -> dict[str, Any]:
        """Produce a summary of findings by category and severity."""
        by_category: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        for f in findings:
            by_category[f.category] = by_category.get(f.category, 0) + 1
            by_severity[f.severity] = by_severity.get(f.severity, 0) + 1

        return {
            "total_findings": len(findings),
            "by_category": by_category,
            "by_severity": by_severity,
            "critical_count": by_severity.get(Severity.CRITICAL, 0),
            "alert_count": by_severity.get(Severity.ALERT, 0),
        }
