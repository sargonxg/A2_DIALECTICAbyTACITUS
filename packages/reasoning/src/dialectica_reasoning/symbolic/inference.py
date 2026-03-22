"""
Symbolic Inference — Forward-chaining rule engine for derived facts.

Generates inferred edges/properties from structural, temporal, and
relational rules. Inferred facts are marked with confidence < 1.0.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from dialectica_graph import GraphClient
from dialectica_ontology.relationships import EdgeType


@dataclass
class InferredFact:
    """A fact derived by symbolic inference."""

    fact_type: str  # "edge" | "property"
    subject_id: str
    predicate: str
    object_id: str | None = None
    object_value: object = None
    confidence: float = 0.7
    method: str = "symbolic_inference"
    rule_name: str = ""
    evidence_ids: list[str] = field(default_factory=list)


@dataclass
class InferenceResult:
    inferred_facts: list[InferredFact] = field(default_factory=list)
    rules_applied: int = 0
    facts_generated: int = 0


class SymbolicInference:
    """Forward-chains symbolic rules to generate inferred facts."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client

    async def forward_chain(self, workspace_id: str) -> InferenceResult:
        """Apply ALL symbolic rules and generate inferred edges/properties."""
        result = InferenceResult()
        rules = [
            self._infer_transitivity,
            self._infer_enemy_of_enemy,
            self._infer_trust_from_alliance,
            self._infer_opposition_from_power,
            self._infer_conflict_escalation_level,
            self._infer_temporal_ordering,
        ]
        for rule in rules:
            facts = await rule(workspace_id)
            result.inferred_facts.extend(facts)
            result.rules_applied += 1
            result.facts_generated += len(facts)
        return result

    async def _infer_transitivity(self, workspace_id: str) -> list[InferredFact]:
        """If A ALLIED_WITH B and B ALLIED_WITH C, infer A potentially allied with C."""
        edges = await self._gc.get_edges(workspace_id)
        allied = [e for e in edges if e.type == EdgeType.ALLIED_WITH]

        alliance_map: dict[str, set[str]] = {}
        for e in allied:
            alliance_map.setdefault(e.source_id, set()).add(e.target_id)
            alliance_map.setdefault(e.target_id, set()).add(e.source_id)

        existing_pairs = {frozenset([e.source_id, e.target_id]) for e in allied}
        facts: list[InferredFact] = []

        for a, b_set in alliance_map.items():
            for b in list(b_set):
                for c in alliance_map.get(b, set()):
                    if c != a and frozenset([a, c]) not in existing_pairs:
                        facts.append(
                            InferredFact(
                                fact_type="edge",
                                subject_id=a,
                                predicate="POTENTIALLY_ALLIED_WITH",
                                object_id=c,
                                confidence=0.6,
                                method="symbolic_inference",
                                rule_name="alliance_transitivity",
                                evidence_ids=[b],
                            )
                        )
                        existing_pairs.add(frozenset([a, c]))  # prevent duplicates

        return facts

    async def _infer_enemy_of_enemy(self, workspace_id: str) -> list[InferredFact]:
        """If A OPPOSED_TO B and B OPPOSED_TO C, infer A potentially allied with C."""
        edges = await self._gc.get_edges(workspace_id)
        opposed = [e for e in edges if e.type == EdgeType.OPPOSED_TO]

        opposition_map: dict[str, set[str]] = {}
        for e in opposed:
            opposition_map.setdefault(e.source_id, set()).add(e.target_id)

        facts: list[InferredFact] = []
        seen: set[frozenset[str]] = set()

        for a, b_set in opposition_map.items():
            for b in list(b_set):
                for c in opposition_map.get(b, set()):
                    if c != a:
                        pair = frozenset([a, c])
                        if pair not in seen:
                            seen.add(pair)
                            facts.append(
                                InferredFact(
                                    fact_type="edge",
                                    subject_id=a,
                                    predicate="POTENTIALLY_ALLIED_WITH",
                                    object_id=c,
                                    confidence=0.55,
                                    method="symbolic_inference",
                                    rule_name="enemy_of_enemy",
                                    evidence_ids=[b],
                                )
                            )
        return facts

    async def _infer_trust_from_alliance(self, workspace_id: str) -> list[InferredFact]:
        """Allied actors likely have higher mutual trust than baseline."""
        edges = await self._gc.get_edges(workspace_id)
        allied = [e for e in edges if e.type == EdgeType.ALLIED_WITH]
        trusts = {(e.source_id, e.target_id) for e in edges if e.type == EdgeType.TRUSTS}

        facts: list[InferredFact] = []
        for e in allied:
            if (e.source_id, e.target_id) not in trusts:
                facts.append(
                    InferredFact(
                        fact_type="edge",
                        subject_id=e.source_id,
                        predicate="INFERRED_TRUST",
                        object_id=e.target_id,
                        object_value={"overall_trust": 0.65, "inferred": True},
                        confidence=0.65,
                        method="symbolic_inference",
                        rule_name="trust_from_alliance",
                        evidence_ids=[e.id],
                    )
                )
        return facts

    async def _infer_opposition_from_power(self, workspace_id: str) -> list[InferredFact]:
        """Strong coercive power asymmetry suggests latent opposition."""
        edges = await self._gc.get_edges(workspace_id)
        power_edges = [e for e in edges if e.type == EdgeType.HAS_POWER_OVER]
        opposed = {
            frozenset([e.source_id, e.target_id]) for e in edges if e.type == EdgeType.OPPOSED_TO
        }

        facts: list[InferredFact] = []
        for e in power_edges:
            props = e.properties or {}
            if props.get("domain") == "coercive" and float(props.get("magnitude", 0)) > 0.7:
                pair = frozenset([e.source_id, e.target_id])
                if pair not in opposed:
                    facts.append(
                        InferredFact(
                            fact_type="edge",
                            subject_id=e.source_id,
                            predicate="LATENT_OPPOSITION",
                            object_id=e.target_id,
                            confidence=0.5,
                            method="symbolic_inference",
                            rule_name="opposition_from_coercive_power",
                            evidence_ids=[e.id],
                        )
                    )
        return facts

    async def _infer_conflict_escalation_level(self, workspace_id: str) -> list[InferredFact]:
        """Infer escalation level property from event severity patterns."""
        events = await self._gc.get_nodes(workspace_id, label="Event")
        conflicts = await self._gc.get_nodes(workspace_id, label="Conflict")
        facts: list[InferredFact] = []

        if not events or not conflicts:
            return facts

        avg_severity = sum(float(getattr(ev, "severity", 0)) for ev in events) / len(events)
        inferred_stage = round(1 + avg_severity * 8)

        for c in conflicts:
            explicit_stage = getattr(c, "glasl_stage", None)
            if explicit_stage is None:
                facts.append(
                    InferredFact(
                        fact_type="property",
                        subject_id=c.id,
                        predicate="inferred_glasl_stage",
                        object_value=inferred_stage,
                        confidence=0.5,
                        method="symbolic_inference",
                        rule_name="escalation_from_events",
                    )
                )
        return facts

    async def _infer_temporal_ordering(self, workspace_id: str) -> list[InferredFact]:
        """Infer PRECEDED_BY relationships from event timestamps."""
        events = await self._gc.get_nodes(workspace_id, label="Event")
        facts: list[InferredFact] = []

        timed = [(ev, getattr(ev, "occurred_at", None)) for ev in events]
        timed = [(ev, t) for ev, t in timed if t is not None]
        timed.sort(key=lambda x: x[1])

        for i in range(len(timed) - 1):
            ev_a, _ = timed[i]
            ev_b, _ = timed[i + 1]
            facts.append(
                InferredFact(
                    fact_type="edge",
                    subject_id=ev_b.id,
                    predicate="PRECEDED_BY",
                    object_id=ev_a.id,
                    confidence=0.95,
                    method="symbolic_inference",
                    rule_name="temporal_ordering",
                )
            )
        return facts
