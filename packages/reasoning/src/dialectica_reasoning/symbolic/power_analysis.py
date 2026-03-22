"""
Power Analysis — French/Raven 6-base power model.

Computes power maps, detects asymmetries, and identifies leverage points.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean

from dialectica_graph import GraphClient
from dialectica_ontology.relationships import EdgeType


@dataclass
class PowerDyad:
    actor_id: str
    target_id: str
    reward: float = 0.0
    coercive: float = 0.0
    legitimate: float = 0.0
    referent: float = 0.0
    expert: float = 0.0
    informational: float = 0.0
    total_power: float = 0.0
    asymmetry: float = 0.0  # |A over B| - |B over A|


@dataclass
class PowerMap:
    workspace_id: str
    dyads: list[PowerDyad] = field(default_factory=list)
    most_powerful_actor: str | None = None
    least_powerful_actor: str | None = None
    average_asymmetry: float = 0.0


@dataclass
class PowerAsymmetry:
    actor_a: str
    actor_b: str
    advantage_holder: str
    asymmetry_score: float
    dominant_bases: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class LeveragePoint:
    actor_id: str
    leverage_type: str
    description: str
    target_actors: list[str] = field(default_factory=list)
    intervention_potential: float = 0.0


class PowerMapper:
    """Computes French/Raven power dynamics for workspace actors."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client

    async def compute_power_map(self, workspace_id: str) -> PowerMap:
        """For each actor pair compute power across all six French/Raven bases."""
        edges = await self._gc.get_edges(workspace_id)
        power_edges = [e for e in edges if e.type == EdgeType.HAS_POWER_OVER]

        dyads: list[PowerDyad] = []
        # Track total power per actor for finding most/least powerful
        actor_power: dict[str, float] = {}

        for e in power_edges:
            props = e.properties or {}
            reward = float(props.get("reward", 0.0))
            coercive = float(props.get("coercive", 0.0))
            legitimate = float(props.get("legitimate", 0.0))
            referent = float(props.get("referent", 0.0))
            expert = float(props.get("expert", 0.0))
            informational = float(props.get("informational", 0.0))

            # Fallback: use magnitude/weight if per-base scores absent
            magnitude = float(props.get("magnitude", e.weight if e.weight else 0.0))
            if not any([reward, coercive, legitimate, referent, expert, informational]):
                domain = props.get("domain", "")
                if domain == "coercive":
                    coercive = magnitude
                elif domain == "reward":
                    reward = magnitude
                elif domain == "legitimate":
                    legitimate = magnitude
                elif domain == "expert":
                    expert = magnitude
                elif domain == "referent":
                    referent = magnitude
                elif domain == "informational":
                    informational = magnitude
                else:
                    coercive = magnitude * 0.3
                    legitimate = magnitude * 0.4
                    expert = magnitude * 0.3

            total = round(mean([reward, coercive, legitimate, referent, expert, informational]), 3)
            actor_power[e.source_id] = actor_power.get(e.source_id, 0.0) + total

            dyads.append(
                PowerDyad(
                    actor_id=e.source_id,
                    target_id=e.target_id,
                    reward=round(reward, 3),
                    coercive=round(coercive, 3),
                    legitimate=round(legitimate, 3),
                    referent=round(referent, 3),
                    expert=round(expert, 3),
                    informational=round(informational, 3),
                    total_power=total,
                )
            )

        # Compute asymmetry for each dyad
        power_by_pair: dict[tuple[str, str], float] = {
            (d.actor_id, d.target_id): d.total_power for d in dyads
        }
        for d in dyads:
            reverse = power_by_pair.get((d.target_id, d.actor_id), 0.0)
            d.asymmetry = round(d.total_power - reverse, 3)

        pm = PowerMap(workspace_id=workspace_id, dyads=dyads)
        if actor_power:
            pm.most_powerful_actor = max(actor_power, key=actor_power.get)  # type: ignore[arg-type]
            pm.least_powerful_actor = min(actor_power, key=actor_power.get)  # type: ignore[arg-type]
            pm.average_asymmetry = round(mean(abs(d.asymmetry) for d in dyads), 3) if dyads else 0.0
        return pm

    async def detect_asymmetries(self, workspace_id: str) -> list[PowerAsymmetry]:
        """Identify significant power imbalances between actor pairs."""
        pm = await self.compute_power_map(workspace_id)
        asymmetries: list[PowerAsymmetry] = []
        seen: set[frozenset[str]] = set()

        for d in pm.dyads:
            pair = frozenset([d.actor_id, d.target_id])
            if pair in seen:
                continue
            if abs(d.asymmetry) < 0.2:
                continue
            seen.add(pair)
            advantage_holder = d.actor_id if d.asymmetry > 0 else d.target_id
            bases = []
            if d.coercive > 0.4:
                bases.append("coercive")
            if d.legitimate > 0.4:
                bases.append("legitimate")
            if d.expert > 0.4:
                bases.append("expert")
            if d.reward > 0.4:
                bases.append("reward")
            asymmetries.append(
                PowerAsymmetry(
                    actor_a=d.actor_id,
                    actor_b=d.target_id,
                    advantage_holder=advantage_holder,
                    asymmetry_score=round(abs(d.asymmetry), 3),
                    dominant_bases=bases,
                    recommendation=(
                        "Consider power-balancing through coalition formation or third-party involvement."  # noqa: E501
                        if abs(d.asymmetry) > 0.5
                        else "Monitor for escalating power differential."
                    ),
                )
            )
        return sorted(asymmetries, key=lambda a: a.asymmetry_score, reverse=True)

    async def identify_leverage_points(self, workspace_id: str) -> list[LeveragePoint]:
        """Identify where interventions could shift power balance."""
        pm = await self.compute_power_map(workspace_id)
        leverage: list[LeveragePoint] = []

        # Actors with high expert power are natural knowledge brokers
        expert_actors: dict[str, float] = {}
        for d in pm.dyads:
            expert_actors[d.actor_id] = expert_actors.get(d.actor_id, 0) + d.expert
        for actor_id, exp_score in expert_actors.items():
            if exp_score > 0.6:
                leverage.append(
                    LeveragePoint(
                        actor_id=actor_id,
                        leverage_type="expert_knowledge",
                        description="High expert power — potential information broker or technical authority.",  # noqa: E501
                        target_actors=[d.target_id for d in pm.dyads if d.actor_id == actor_id],
                        intervention_potential=round(min(1.0, exp_score), 3),
                    )
                )

        # Actors with high legitimate power can convene
        legitimate_actors: dict[str, float] = {}
        for d in pm.dyads:
            legitimate_actors[d.actor_id] = legitimate_actors.get(d.actor_id, 0) + d.legitimate
        for actor_id, leg_score in legitimate_actors.items():
            if leg_score > 0.5:
                leverage.append(
                    LeveragePoint(
                        actor_id=actor_id,
                        leverage_type="legitimate_authority",
                        description="High legitimate power — can convene parties or impose framework.",  # noqa: E501
                        target_actors=[d.target_id for d in pm.dyads if d.actor_id == actor_id],
                        intervention_potential=round(min(1.0, leg_score), 3),
                    )
                )

        return leverage
