"""
Conflict Grammar Engine — Deterministic symbolic rule evaluation.

Runs structural, escalation, ripeness, trust, power, and causal rules
against the workspace graph and produces a RuleEvaluationReport with
findings, summary score, and categorised results.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from dialectica_graph import GraphClient
from dialectica_ontology.enums import (
    ConflictStatus,
    GlaslStage,
    PrimaryEmotion,
    ViolenceType,
)
from dialectica_ontology.primitives import (
    Actor,
    Conflict,
    Event,
    Process,
    TrustState,
)
from dialectica_ontology.relationships import (
    ConflictRelationship,
    EdgeType,
    EDGE_SCHEMA,
    validate_relationship,
)


# ---------------------------------------------------------------------------
# Result data classes
# ---------------------------------------------------------------------------

class Severity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class Finding:
    """A single rule evaluation finding."""

    rule_name: str
    severity: Severity
    description: str
    evidence_ids: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class RuleEvaluationReport:
    """Aggregate report from evaluating all symbolic rules."""

    findings: list[Finding] = field(default_factory=list)
    summary_score: float = 1.0  # 0.0 = many critical issues, 1.0 = healthy
    categories: dict[str, list[Finding]] = field(default_factory=dict)

    def _categorise(self) -> None:
        self.categories.clear()
        for f in self.findings:
            self.categories.setdefault(f.rule_name, []).append(f)

    def _compute_score(self) -> None:
        if not self.findings:
            self.summary_score = 1.0
            return
        penalty = 0.0
        for f in self.findings:
            if f.severity == Severity.CRITICAL:
                penalty += 0.20
            elif f.severity == Severity.WARNING:
                penalty += 0.08
            else:
                penalty += 0.02
        self.summary_score = max(0.0, 1.0 - penalty)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class ConflictGrammarEngine:
    """Evaluates deterministic symbolic rules over a workspace graph."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client

    # -- public entry point -------------------------------------------------

    async def evaluate_all_rules(self, workspace_id: str) -> RuleEvaluationReport:
        """Run every rule category and return an aggregated report."""
        report = RuleEvaluationReport()

        report.findings.extend(await self._structural_consistency(workspace_id))
        report.findings.extend(await self._escalation_rules(workspace_id))
        report.findings.extend(await self._ripeness_rules(workspace_id))
        report.findings.extend(await self._trust_rules(workspace_id))
        report.findings.extend(await self._power_rules(workspace_id))
        report.findings.extend(await self._causal_rules(workspace_id))

        report._compute_score()
        report._categorise()
        return report

    # -- structural consistency ---------------------------------------------

    async def _structural_consistency(self, workspace_id: str) -> list[Finding]:
        findings: list[Finding] = []

        edges = await self._gc.get_edges(workspace_id)
        for edge in edges:
            errors = validate_relationship(edge)
            for err in errors:
                findings.append(Finding(
                    rule_name="structural_consistency",
                    severity=Severity.WARNING,
                    description=err,
                    evidence_ids=[edge.id],
                    recommendation="Review and correct edge source/target labels.",
                ))

        # Every conflict should have at least one PARTY_TO edge
        conflicts = await self._gc.get_nodes(workspace_id, label="Conflict")
        party_to_edges = [e for e in edges if e.type == EdgeType.PARTY_TO]
        conflict_ids_with_parties = {e.target_id for e in party_to_edges}

        for c in conflicts:
            if c.id not in conflict_ids_with_parties:
                findings.append(Finding(
                    rule_name="structural_consistency",
                    severity=Severity.WARNING,
                    description=f"Conflict '{getattr(c, 'name', c.id)}' has no PARTY_TO edges — no actors linked.",
                    evidence_ids=[c.id],
                    recommendation="Add at least two actors as parties to this conflict.",
                ))

        # Events should have at least one PART_OF edge to a conflict
        events = await self._gc.get_nodes(workspace_id, label="Event")
        part_of_edges = [e for e in edges if e.type == EdgeType.PART_OF]
        event_ids_in_conflict = {e.source_id for e in part_of_edges}
        for ev in events:
            if ev.id not in event_ids_in_conflict:
                findings.append(Finding(
                    rule_name="structural_consistency",
                    severity=Severity.INFO,
                    description=f"Event '{ev.id}' is not linked to any conflict via PART_OF.",
                    evidence_ids=[ev.id],
                    recommendation="Link event to its parent conflict.",
                ))

        return findings

    # -- escalation rules ---------------------------------------------------

    async def _escalation_rules(self, workspace_id: str) -> list[Finding]:
        findings: list[Finding] = []

        conflicts = await self._gc.get_nodes(workspace_id, label="Conflict")
        for node in conflicts:
            c: Conflict = node  # type: ignore[assignment]
            stage = getattr(c, "glasl_stage", None)
            if stage is not None and stage >= 7:
                sev = Severity.CRITICAL if stage >= 8 else Severity.WARNING
                findings.append(Finding(
                    rule_name="escalation",
                    severity=sev,
                    description=(
                        f"Conflict '{getattr(c, 'name', c.id)}' at Glasl stage {stage} "
                        f"(lose-lose territory). Immediate intervention required."
                    ),
                    evidence_ids=[c.id],
                    recommendation="Consider power intervention or arbitration.",
                ))

            violence = getattr(c, "violence_type", None)
            if violence == ViolenceType.DIRECT:
                findings.append(Finding(
                    rule_name="escalation",
                    severity=Severity.CRITICAL,
                    description=f"Conflict '{getattr(c, 'name', c.id)}' involves direct violence.",
                    evidence_ids=[c.id],
                    recommendation="Prioritise safety and de-escalation measures.",
                ))

        return findings

    # -- ripeness rules -----------------------------------------------------

    async def _ripeness_rules(self, workspace_id: str) -> list[Finding]:
        findings: list[Finding] = []

        conflicts = await self._gc.get_nodes(workspace_id, label="Conflict")
        edges = await self._gc.get_edges(workspace_id)

        resolved_through_sources = {
            e.source_id for e in edges if e.type == EdgeType.RESOLVED_THROUGH
        }

        for node in conflicts:
            c: Conflict = node  # type: ignore[assignment]
            status = getattr(c, "status", None)

            if status in (ConflictStatus.DORMANT, ConflictStatus.LATENT):
                if c.id not in resolved_through_sources:
                    findings.append(Finding(
                        rule_name="ripeness",
                        severity=Severity.INFO,
                        description=(
                            f"Conflict '{getattr(c, 'name', c.id)}' is {status} "
                            "with no resolution process — potential mutually hurting stalemate."
                        ),
                        evidence_ids=[c.id],
                        recommendation="Assess if a mutually enticing opportunity can be presented.",
                    ))

            if status == ConflictStatus.ACTIVE and c.id not in resolved_through_sources:
                findings.append(Finding(
                    rule_name="ripeness",
                    severity=Severity.WARNING,
                    description=(
                        f"Active conflict '{getattr(c, 'name', c.id)}' has no "
                        "RESOLVED_THROUGH process linked."
                    ),
                    evidence_ids=[c.id],
                    recommendation="Initiate a suitable resolution process.",
                ))

        return findings

    # -- trust rules --------------------------------------------------------

    async def _trust_rules(self, workspace_id: str) -> list[Finding]:
        findings: list[Finding] = []

        trust_states = await self._gc.get_nodes(workspace_id, label="TrustState")
        for node in trust_states:
            ts: TrustState = node  # type: ignore[assignment]
            overall = getattr(ts, "overall_trust", None)
            if overall is not None and overall < 0.2:
                findings.append(Finding(
                    rule_name="trust",
                    severity=Severity.WARNING,
                    description=f"Very low trust detected (overall_trust={overall:.2f}).",
                    evidence_ids=[ts.id],
                    recommendation="Prioritise trust-building measures before substantive negotiation.",
                ))

            ability = getattr(ts, "perceived_ability", None)
            benevolence = getattr(ts, "perceived_benevolence", None)
            integrity = getattr(ts, "perceived_integrity", None)
            if ability is not None and benevolence is not None and integrity is not None:
                if integrity < 0.15 and benevolence < 0.15:
                    findings.append(Finding(
                        rule_name="trust",
                        severity=Severity.CRITICAL,
                        description=(
                            "Integrity and benevolence both critically low — "
                            "suggests perceived bad faith."
                        ),
                        evidence_ids=[ts.id],
                        recommendation="Address perceived bad faith before proceeding.",
                    ))

        return findings

    # -- power rules --------------------------------------------------------

    async def _power_rules(self, workspace_id: str) -> list[Finding]:
        findings: list[Finding] = []

        edges = await self._gc.get_edges(workspace_id, edge_type=EdgeType.HAS_POWER_OVER)
        opposed_edges = await self._gc.get_edges(workspace_id, edge_type=EdgeType.OPPOSED_TO)

        opposed_pairs: set[tuple[str, str]] = set()
        for e in opposed_edges:
            opposed_pairs.add((e.source_id, e.target_id))
            opposed_pairs.add((e.target_id, e.source_id))

        for edge in edges:
            magnitude = edge.properties.get("magnitude", edge.weight)
            if magnitude > 0.8:
                findings.append(Finding(
                    rule_name="power",
                    severity=Severity.INFO,
                    description=(
                        f"Strong power asymmetry detected (magnitude={magnitude:.2f}) "
                        f"between {edge.source_id} and {edge.target_id}."
                    ),
                    evidence_ids=[edge.id],
                    recommendation="Consider power-balancing interventions.",
                ))

            # Check for opposed actors both wielding coercive power
            domain = edge.properties.get("domain", "")
            if domain == "coercive" and (edge.target_id, edge.source_id) in opposed_pairs:
                findings.append(Finding(
                    rule_name="power",
                    severity=Severity.WARNING,
                    description=(
                        "Opposing actors both possess coercive power — "
                        "potential security dilemma."
                    ),
                    evidence_ids=[edge.id, edge.source_id, edge.target_id],
                    recommendation="Monitor for arms-race dynamics; introduce confidence-building measures.",
                ))

        return findings

    # -- causal rules -------------------------------------------------------

    async def _causal_rules(self, workspace_id: str) -> list[Finding]:
        findings: list[Finding] = []

        caused_edges = await self._gc.get_edges(workspace_id, edge_type=EdgeType.CAUSED)
        if not caused_edges:
            return findings

        # Build adjacency for causal chains
        outgoing: dict[str, list[str]] = {}
        for e in caused_edges:
            outgoing.setdefault(e.source_id, []).append(e.target_id)

        incoming: dict[str, list[str]] = {}
        for e in caused_edges:
            incoming.setdefault(e.target_id, []).append(e.source_id)

        # Detect long causal chains (depth >= 4)
        def _chain_depth(node_id: str, visited: set[str] | None = None) -> int:
            if visited is None:
                visited = set()
            if node_id in visited:
                return 0
            visited.add(node_id)
            children = outgoing.get(node_id, [])
            if not children:
                return 1
            return 1 + max(_chain_depth(c, visited) for c in children)

        roots = [nid for nid in outgoing if nid not in incoming]
        for root in roots:
            depth = _chain_depth(root)
            if depth >= 4:
                findings.append(Finding(
                    rule_name="causal",
                    severity=Severity.WARNING,
                    description=(
                        f"Long causal chain detected (depth={depth}) originating from event {root}."
                    ),
                    evidence_ids=[root],
                    recommendation="Investigate root cause to break the causal chain.",
                ))

        # Detect cycles (feedback loops)
        all_nodes = set(outgoing.keys()) | set(incoming.keys())
        visited_global: set[str] = set()
        rec_stack: set[str] = set()

        def _has_cycle(node_id: str) -> bool:
            visited_global.add(node_id)
            rec_stack.add(node_id)
            for child in outgoing.get(node_id, []):
                if child not in visited_global:
                    if _has_cycle(child):
                        return True
                elif child in rec_stack:
                    return True
            rec_stack.discard(node_id)
            return False

        for n in all_nodes:
            if n not in visited_global:
                if _has_cycle(n):
                    findings.append(Finding(
                        rule_name="causal",
                        severity=Severity.WARNING,
                        description="Causal feedback loop detected in event chain.",
                        evidence_ids=[n],
                        recommendation="Identify and interrupt feedback loops to prevent escalation.",
                    ))
                    break  # report once

        return findings
