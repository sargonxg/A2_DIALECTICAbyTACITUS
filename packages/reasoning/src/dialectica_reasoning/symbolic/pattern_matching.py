"""
Pattern Matching — Known conflict pattern detection against workspace graphs.

Detects: escalation spiral, security dilemma, spoiler dynamics,
hurting stalemate formation, and alliance cascade.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from dialectica_graph import GraphClient
from dialectica_ontology.enums import ConflictStatus
from dialectica_ontology.relationships import EdgeType


@dataclass
class PatternMatch:
    pattern_name: str
    confidence: float
    evidence_ids: list[str] = field(default_factory=list)
    description: str = ""
    intervention_recommendation: str = ""


class PatternMatcher:
    """Matches known conflict patterns against workspace graph."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client

    async def detect_all(self, workspace_id: str) -> list[PatternMatch]:
        """Run all pattern detectors and return list of matches."""
        results: list[PatternMatch] = []
        detectors = [
            self.detect_escalation_spiral,
            self.detect_security_dilemma,
            self.detect_spoiler_dynamics,
            self.detect_hurting_stalemate,
            self.detect_alliance_cascade,
        ]
        for detector in detectors:
            matches = await detector(workspace_id)
            results.extend(matches)
        return sorted(results, key=lambda m: m.confidence, reverse=True)

    async def detect_escalation_spiral(self, workspace_id: str) -> list[PatternMatch]:
        """Detect tit-for-tat event chains (A attacks B, B attacks A, repeat)."""
        events = await self._gc.get_nodes(workspace_id, label="Event")
        matches: list[PatternMatch] = []
        hostile_types = {"threaten", "coerce", "assault", "accuse", "reduce_relations"}

        # Group hostile events by performer-target pairs
        pairs: dict[tuple[str, str], list[str]] = {}
        for ev in events:
            et = getattr(ev, "event_type", "")
            performer = getattr(ev, "performer_id", None)
            target = getattr(ev, "target_id", None)
            if et in hostile_types and performer and target:
                pairs.setdefault((performer, target), []).append(ev.id)

        # Check for reciprocal hostile events
        for (a, b), ev_ids in pairs.items():
            reverse = pairs.get((b, a), [])
            if reverse and len(ev_ids) >= 2 and len(reverse) >= 2:
                evidence = ev_ids[:3] + reverse[:3]
                confidence = min(1.0, (len(ev_ids) + len(reverse)) * 0.1)
                matches.append(PatternMatch(
                    pattern_name="escalation_spiral",
                    confidence=round(confidence, 3),
                    evidence_ids=evidence,
                    description=(
                        f"Tit-for-tat hostile exchange between actors "
                        f"({len(ev_ids)} + {len(reverse)} hostile events)."
                    ),
                    intervention_recommendation=(
                        "Introduce circuit-breaker: mutual ceasefire, third-party monitor, "
                        "or confidence-building measures."
                    ),
                ))
        return matches

    async def detect_security_dilemma(self, workspace_id: str) -> list[PatternMatch]:
        """Detect defensive actions perceived as offensive by the other side."""
        edges = await self._gc.get_edges(workspace_id)
        power_edges = [e for e in edges if e.type == EdgeType.HAS_POWER_OVER]
        opposed_edges = [e for e in edges if e.type == EdgeType.OPPOSED_TO]
        matches: list[PatternMatch] = []

        opposed_pairs: set[tuple[str, str]] = set()
        for e in opposed_edges:
            opposed_pairs.add((e.source_id, e.target_id))
            opposed_pairs.add((e.target_id, e.source_id))

        # Two opposed actors both building coercive power
        coercive_actors: dict[str, list[str]] = {}
        for e in power_edges:
            domain = (e.properties or {}).get("domain", "")
            if domain == "coercive":
                coercive_actors.setdefault(e.source_id, []).append(e.id)

        for a, ev_a in coercive_actors.items():
            for b, ev_b in coercive_actors.items():
                if a != b and (a, b) in opposed_pairs:
                    confidence = min(1.0, (len(ev_a) + len(ev_b)) * 0.25)
                    matches.append(PatternMatch(
                        pattern_name="security_dilemma",
                        confidence=round(confidence, 3),
                        evidence_ids=ev_a[:2] + ev_b[:2],
                        description=(
                            "Opposing actors both accumulating coercive power — "
                            "defensive measures perceived as threatening."
                        ),
                        intervention_recommendation=(
                            "Introduce transparency measures, mutual inspections, or "
                            "confidence-building agreements to reduce threat perception."
                        ),
                    ))
        return matches

    async def detect_spoiler_dynamics(self, workspace_id: str) -> list[PatternMatch]:
        """Detect actors benefiting from continued conflict (spoilers)."""
        edges = await self._gc.get_edges(workspace_id)
        events = await self._gc.get_nodes(workspace_id, label="Event")
        outcomes = await self._gc.get_nodes(workspace_id, label="Outcome")
        matches: list[PatternMatch] = []

        # Actors opposing resolution processes
        opposed_edges = [e for e in edges if e.type == EdgeType.OPPOSED_TO]
        processes = await self._gc.get_nodes(workspace_id, label="Process")
        process_ids = {p.id for p in processes}

        spoiler_actors: dict[str, list[str]] = {}
        for e in opposed_edges:
            if e.target_id in process_ids:
                spoiler_actors.setdefault(e.source_id, []).append(e.id)

        # Actors disrupting agreements through hostile events during peace talks
        disruption_types = {"violate_agreement", "assault", "threaten", "betray"}
        for ev in events:
            et = getattr(ev, "event_type", "")
            performer = getattr(ev, "performer_id", None)
            if et in disruption_types and performer:
                spoiler_actors.setdefault(performer, []).append(ev.id)

        for actor_id, evidence in spoiler_actors.items():
            if len(evidence) >= 2:
                confidence = min(1.0, len(evidence) * 0.25)
                matches.append(PatternMatch(
                    pattern_name="spoiler_dynamics",
                    confidence=round(confidence, 3),
                    evidence_ids=evidence[:5],
                    description=f"Actor '{actor_id}' shows spoiler behaviour — opposing resolution.",
                    intervention_recommendation=(
                        "Include potential spoilers in the process, address their core interests, "
                        "or build a coalition to marginalise/contain them."
                    ),
                ))
        return matches

    async def detect_hurting_stalemate(self, workspace_id: str) -> list[PatternMatch]:
        """Detect mutually hurting stalemate formation (Zartman pattern)."""
        conflicts = await self._gc.get_nodes(workspace_id, label="Conflict")
        events = await self._gc.get_nodes(workspace_id, label="Event")
        matches: list[PatternMatch] = []

        stalemate_statuses = {ConflictStatus.DORMANT, ConflictStatus.LATENT}
        for c in conflicts:
            status = getattr(c, "status", None)
            if status not in stalemate_statuses:
                continue
            # High-cost events with no resolution outcome
            costly_events = [
                ev for ev in events
                if getattr(ev, "severity", 0) >= 0.6
            ]
            if len(costly_events) >= 2:
                confidence = min(1.0, len(costly_events) * 0.15 + 0.2)
                matches.append(PatternMatch(
                    pattern_name="hurting_stalemate",
                    confidence=round(confidence, 3),
                    evidence_ids=[c.id] + [ev.id for ev in costly_events[:4]],
                    description=(
                        f"Stalemate detected with {len(costly_events)} costly events — "
                        "both sides paying costs without decisive outcome."
                    ),
                    intervention_recommendation=(
                        "Conflict may be ripe for intervention. Introduce a mutually enticing "
                        "opportunity and a trusted mediator."
                    ),
                ))
        return matches

    async def detect_alliance_cascade(self, workspace_id: str) -> list[PatternMatch]:
        """Detect expanding coalition formation (alliance cascade)."""
        edges = await self._gc.get_edges(workspace_id)
        matches: list[PatternMatch] = []

        allied_edges = [e for e in edges if e.type == EdgeType.ALLIED_WITH]
        opposed_edges = [e for e in edges if e.type == EdgeType.OPPOSED_TO]

        if len(allied_edges) < 3:
            return matches

        # Build alliance clusters
        actor_alliances: dict[str, set[str]] = {}
        for e in allied_edges:
            actor_alliances.setdefault(e.source_id, set()).add(e.target_id)
            actor_alliances.setdefault(e.target_id, set()).add(e.source_id)

        # Look for actors with 3+ allies
        cascade_actors = [a for a, allies in actor_alliances.items() if len(allies) >= 3]
        if cascade_actors:
            confidence = min(1.0, len(cascade_actors) * 0.2 + len(allied_edges) * 0.05)
            all_evidence = [e.id for e in allied_edges[:5]] + [e.id for e in opposed_edges[:3]]
            matches.append(PatternMatch(
                pattern_name="alliance_cascade",
                confidence=round(confidence, 3),
                evidence_ids=all_evidence,
                description=(
                    f"Alliance cascade: {len(allied_edges)} alliances forming across "
                    f"{len(actor_alliances)} actors, with {len(opposed_edges)} opposition edges."
                ),
                intervention_recommendation=(
                    "Prevent polarisation by engaging cross-cutting actors. "
                    "Introduce confidence-building measures between blocs."
                ),
            ))
        return matches
