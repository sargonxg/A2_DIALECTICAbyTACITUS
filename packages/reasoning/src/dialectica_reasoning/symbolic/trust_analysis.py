"""
Trust Analysis — Mayer/Davis/Schoorman ABIntegrity trust model.

Computes trust matrices between actors and detects trust-altering events.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import mean

from dialectica_graph import GraphClient
from dialectica_ontology.primitives import TrustState
from dialectica_ontology.relationships import EdgeType


@dataclass
class TrustDyad:
    trustor_id: str
    trustee_id: str
    ability: float = 0.5
    benevolence: float = 0.5
    integrity: float = 0.5
    overall_trust: float = 0.5
    confidence: float = 0.0


@dataclass
class TrustMatrix:
    workspace_id: str
    dyads: list[TrustDyad] = field(default_factory=list)
    average_trust: float = 0.5
    lowest_trust_pair: tuple[str, str] | None = None
    highest_trust_pair: tuple[str, str] | None = None


@dataclass
class TrustChange:
    trustor_id: str
    trustee_id: str
    event_id: str
    event_description: str
    trust_delta: float = 0.0
    timestamp: datetime | None = None
    change_type: str = "decrease"


class TrustAnalyzer:
    """Computes Mayer/Davis/Schoorman trust matrices and detects trust-altering events."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client

    async def compute_trust_matrix(self, workspace_id: str) -> TrustMatrix:
        """For each actor pair compute ability, benevolence, integrity, and overall trust."""
        trust_states = await self._gc.get_nodes(workspace_id, label="TrustState")
        edges = await self._gc.get_edges(workspace_id)
        trusts_edges = [e for e in edges if e.type == EdgeType.TRUSTS]

        # Build dyads from TRUSTS edges
        dyads: list[TrustDyad] = []
        ts_by_id: dict[str, TrustState] = {ts.id: ts for ts in trust_states}  # type: ignore[assignment]

        for e in trusts_edges:
            props = e.properties or {}
            ability = float(props.get("ability", 0.5))
            benevolence = float(props.get("benevolence", 0.5))
            integrity = float(props.get("integrity", 0.5))

            ts_id = props.get("trust_state_id")
            if ts_id and ts_id in ts_by_id:
                ts_node = ts_by_id[ts_id]
                ability = getattr(ts_node, "perceived_ability", ability)
                benevolence = getattr(ts_node, "perceived_benevolence", benevolence)
                integrity = getattr(ts_node, "perceived_integrity", integrity)

            overall = round(mean([ability, benevolence, integrity]), 3)
            dyads.append(TrustDyad(
                trustor_id=e.source_id,
                trustee_id=e.target_id,
                ability=round(float(ability), 3),
                benevolence=round(float(benevolence), 3),
                integrity=round(float(integrity), 3),
                overall_trust=overall,
                confidence=float(props.get("confidence", 0.5)),
            ))

        # Fallback: build from TrustState nodes directly
        if not dyads:
            for ts_node in trust_states:
                ts: TrustState = ts_node  # type: ignore[assignment]
                trustor = getattr(ts, "trustor_id", None)
                trustee = getattr(ts, "trustee_id", None)
                if not trustor or not trustee:
                    continue
                ability = float(getattr(ts, "perceived_ability", 0.5))
                benevolence = float(getattr(ts, "perceived_benevolence", 0.5))
                integrity = float(getattr(ts, "perceived_integrity", 0.5))
                overall = float(getattr(ts, "overall_trust", round(mean([ability, benevolence, integrity]), 3)))
                dyads.append(TrustDyad(
                    trustor_id=trustor,
                    trustee_id=trustee,
                    ability=round(ability, 3),
                    benevolence=round(benevolence, 3),
                    integrity=round(integrity, 3),
                    overall_trust=round(overall, 3),
                    confidence=float(getattr(ts, "confidence", 0.5)),
                ))

        matrix = TrustMatrix(workspace_id=workspace_id, dyads=dyads)
        if dyads:
            matrix.average_trust = round(mean(d.overall_trust for d in dyads), 3)
            matrix.lowest_trust_pair = (
                min(dyads, key=lambda d: d.overall_trust).trustor_id,
                min(dyads, key=lambda d: d.overall_trust).trustee_id,
            )
            matrix.highest_trust_pair = (
                max(dyads, key=lambda d: d.overall_trust).trustor_id,
                max(dyads, key=lambda d: d.overall_trust).trustee_id,
            )
        return matrix

    async def detect_trust_changes(
        self, workspace_id: str, window_days: int = 90
    ) -> list[TrustChange]:
        """Find Events that changed trust levels within a time window."""
        changes: list[TrustChange] = []
        cutoff = datetime.utcnow() - timedelta(days=window_days)
        events = await self._gc.get_nodes(workspace_id, label="Event")

        eroding = {"betray", "deceive", "violate_agreement", "threaten", "coerce", "assault", "accuse"}
        building = {"agree", "support", "cooperate", "yield", "apologise", "comply", "consult", "aid"}

        for node in events:
            occ = getattr(node, "occurred_at", None)
            if occ is not None and occ < cutoff:
                continue
            et = getattr(node, "event_type", "")
            severity = float(getattr(node, "severity", 0.3))
            performer = getattr(node, "performer_id", None)
            target = getattr(node, "target_id", None)
            if not performer or not target:
                continue
            if et in eroding:
                changes.append(TrustChange(
                    trustor_id=target,
                    trustee_id=performer,
                    event_id=node.id,
                    event_description=getattr(node, "description", et),
                    trust_delta=-round(severity * 0.3, 3),
                    timestamp=occ,
                    change_type="decrease",
                ))
            elif et in building:
                changes.append(TrustChange(
                    trustor_id=target,
                    trustee_id=performer,
                    event_id=node.id,
                    event_description=getattr(node, "description", et),
                    trust_delta=round(severity * 0.2, 3),
                    timestamp=occ,
                    change_type="increase",
                ))
        return changes
