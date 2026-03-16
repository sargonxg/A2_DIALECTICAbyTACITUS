"""
Ripeness Scoring — Zartman's Mutually Hurting Stalemate (MHS) and
Mutually Enticing Opportunity (MEO) computation.

Produces a composite ripeness score used to determine whether a
conflict is ready for productive intervention.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean

from dialectica_graph import GraphClient
from dialectica_ontology.enums import ConflictStatus, ProcessStatus, RoleType
from dialectica_ontology.primitives import (
    Conflict,
    Event,
    Process,
)
from dialectica_ontology.relationships import EdgeType


# ---------------------------------------------------------------------------
# Result data classes
# ---------------------------------------------------------------------------

@dataclass
class RipenessAssessment:
    """Full ripeness assessment combining MHS and MEO."""

    mhs_score: float = 0.0
    meo_score: float = 0.0
    overall_score: float = 0.0
    is_ripe: bool = False
    factors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------

class RipenessScorer:
    """Computes Zartman ripeness from workspace graph data."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client

    # -- MHS ----------------------------------------------------------------

    async def compute_mhs(self, workspace_id: str) -> float:
        """Mutually Hurting Stalemate score (0-1).

        Indicators:
        - Cost accumulation: high-severity events
        - Stalemate signals: dormant/latent conflict status
        - Perception of pain: negative emotional states
        """
        components: list[float] = []

        # 1. Cost accumulation — average event severity
        events = await self._gc.get_nodes(workspace_id, label="Event")
        if events:
            severities = [getattr(ev, "severity", 0.0) for ev in events]
            components.append(mean(severities))

        # 2. Stalemate indicators — conflicts that are dormant or in stalemate
        conflicts = await self._gc.get_nodes(workspace_id, label="Conflict")
        if conflicts:
            stalemate_count = sum(
                1 for c in conflicts
                if getattr(c, "status", None) in (
                    ConflictStatus.DORMANT,
                    ConflictStatus.LATENT,
                )
            )
            components.append(stalemate_count / len(conflicts))

        # 3. Perception of pain — proportion of negative emotions
        emotions = await self._gc.get_nodes(workspace_id, label="EmotionalState")
        if emotions:
            negative = {"anger", "fear", "sadness", "disgust"}
            neg_count = sum(
                1 for e in emotions
                if getattr(e, "primary_emotion", None) in negative
            )
            components.append(neg_count / len(emotions))

        # 4. No resolution process yet but high activity = stalemate
        edges = await self._gc.get_edges(workspace_id)
        resolved_ids = {e.source_id for e in edges if e.type == EdgeType.RESOLVED_THROUGH}
        active_unresolved = [
            c for c in conflicts
            if getattr(c, "status", None) == ConflictStatus.ACTIVE
            and c.id not in resolved_ids
        ]
        if conflicts:
            components.append(len(active_unresolved) / len(conflicts))

        if not components:
            return 0.0
        return round(min(1.0, mean(components)), 3)

    # -- MEO ----------------------------------------------------------------

    async def compute_meo(self, workspace_id: str) -> float:
        """Mutually Enticing Opportunity score (0-1).

        Indicators:
        - Process availability: existing resolution processes
        - Third-party involvement: mediator/facilitator roles
        - Leadership openness: cooperative events or signals
        """
        components: list[float] = []

        # 1. Process availability
        processes = await self._gc.get_nodes(workspace_id, label="Process")
        conflicts = await self._gc.get_nodes(workspace_id, label="Conflict")
        n_conflicts = max(len(conflicts), 1)

        active_processes = [
            p for p in processes
            if getattr(p, "status", None) in (
                ProcessStatus.ACTIVE,
                ProcessStatus.PENDING,
            )
        ]
        # ratio of processes to conflicts (capped at 1.0)
        process_ratio = min(1.0, len(active_processes) / n_conflicts) if n_conflicts else 0.0
        components.append(process_ratio)

        # 2. Third-party involvement — look for mediator/facilitator roles
        edges = await self._gc.get_edges(workspace_id)
        participates_edges = [e for e in edges if e.type == EdgeType.PARTICIPATES_IN]
        third_party_roles = {"mediator", "facilitator", "arbitrator", "neutral", "guarantor"}
        tp_count = sum(
            1 for e in participates_edges
            if e.properties.get("role_type", "").lower() in third_party_roles
        )
        components.append(min(1.0, tp_count * 0.25))

        # 3. Cooperative events indicating leadership openness
        events = await self._gc.get_nodes(workspace_id, label="Event")
        cooperative_types = {"agree", "consult", "support", "cooperate", "aid", "yield"}
        coop_count = sum(
            1 for ev in events
            if getattr(ev, "event_type", "") in cooperative_types
        )
        total_events = max(len(events), 1)
        components.append(min(1.0, coop_count / total_events))

        # 4. Existing outcomes (even partial) suggest path forward
        outcomes = await self._gc.get_nodes(workspace_id, label="Outcome")
        if outcomes:
            components.append(min(1.0, len(outcomes) * 0.3))

        if not components:
            return 0.0
        return round(min(1.0, mean(components)), 3)

    # -- Combined ripeness --------------------------------------------------

    async def compute_ripeness(self, workspace_id: str) -> RipenessAssessment:
        """Compute overall ripeness combining MHS and MEO."""
        mhs = await self.compute_mhs(workspace_id)
        meo = await self.compute_meo(workspace_id)

        # Zartman: ripeness requires BOTH MHS and MEO
        # Use geometric-mean-like combination so both must be present
        overall = (mhs * meo) ** 0.5 if (mhs > 0 and meo > 0) else 0.0
        overall = round(min(1.0, overall), 3)

        is_ripe = mhs >= 0.4 and meo >= 0.3 and overall >= 0.35

        factors: list[str] = []
        if mhs >= 0.5:
            factors.append("Strong mutually hurting stalemate indicators.")
        elif mhs >= 0.3:
            factors.append("Moderate stalemate pressure detected.")
        else:
            factors.append("Low stalemate pressure — parties may not yet feel pain.")

        if meo >= 0.5:
            factors.append("Good mutually enticing opportunity — processes and third parties available.")
        elif meo >= 0.3:
            factors.append("Some opportunity for resolution exists.")
        else:
            factors.append("Limited resolution opportunities — consider creating an enticing option.")

        if is_ripe:
            factors.append("Conflict appears ripe for intervention.")
        else:
            factors.append("Conflict does not yet appear ripe for productive intervention.")

        return RipenessAssessment(
            mhs_score=mhs,
            meo_score=meo,
            overall_score=overall,
            is_ripe=is_ripe,
            factors=factors,
        )
