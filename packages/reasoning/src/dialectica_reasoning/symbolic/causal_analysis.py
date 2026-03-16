"""
Causal Analysis — Pearl's causal hierarchy for conflict event chains.

Implements: association, intervention, and counterfactual reasoning.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dialectica_graph import GraphClient
from dialectica_ontology.relationships import EdgeType


@dataclass
class CausalChain:
    root_event_id: str
    chain: list[str] = field(default_factory=list)  # ordered event IDs
    depth: int = 0
    has_cycle: bool = False
    description: str = ""


@dataclass
class RootCause:
    event_id: str
    event_description: str
    downstream_count: int
    confidence: float


@dataclass
class CounterfactualResult:
    counterfactual_event_id: str
    affected_events: list[str] = field(default_factory=list)
    removed_chains: int = 0
    impact_assessment: str = ""


class CausalAnalyzer:
    """Builds causal chains, identifies root causes, and performs counterfactual analysis."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client

    async def _build_causal_graph(
        self, workspace_id: str
    ) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[str, Any]]:
        """Returns outgoing, incoming adjacency maps and event node data."""
        caused_edges = await self._gc.get_edges(workspace_id, edge_type=EdgeType.CAUSED)
        events = await self._gc.get_nodes(workspace_id, label="Event")

        event_data: dict[str, Any] = {e.id: e for e in events}
        outgoing: dict[str, list[str]] = {}
        incoming: dict[str, list[str]] = {}
        for e in caused_edges:
            outgoing.setdefault(e.source_id, []).append(e.target_id)
            incoming.setdefault(e.target_id, []).append(e.source_id)
        return outgoing, incoming, event_data

    def _trace_chain(
        self,
        node_id: str,
        outgoing: dict[str, list[str]],
        visited: set[str] | None = None,
    ) -> list[str]:
        if visited is None:
            visited = set()
        if node_id in visited:
            return [node_id]  # cycle terminator
        visited.add(node_id)
        result = [node_id]
        for child in outgoing.get(node_id, []):
            result.extend(self._trace_chain(child, outgoing, visited))
        return result

    def _chain_depth(
        self, node_id: str, outgoing: dict[str, list[str]], visited: set[str] | None = None
    ) -> int:
        if visited is None:
            visited = set()
        if node_id in visited:
            return 0
        visited.add(node_id)
        children = outgoing.get(node_id, [])
        if not children:
            return 1
        return 1 + max(self._chain_depth(c, outgoing, visited) for c in children)

    def _detect_cycles(self, outgoing: dict[str, list[str]]) -> set[str]:
        """Return set of node IDs that are part of a cycle."""
        visited: set[str] = set()
        rec_stack: set[str] = set()
        cycle_nodes: set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for child in outgoing.get(node, []):
                if child not in visited:
                    if dfs(child):
                        cycle_nodes.add(node)
                        return True
                elif child in rec_stack:
                    cycle_nodes.add(child)
                    cycle_nodes.add(node)
                    return True
            rec_stack.discard(node)
            return False

        all_nodes = set(outgoing.keys())
        for child_list in outgoing.values():
            all_nodes.update(child_list)
        for n in all_nodes:
            if n not in visited:
                dfs(n)
        return cycle_nodes

    async def extract_causal_chains(self, workspace_id: str) -> list[CausalChain]:
        """Follow CAUSED edges to build ordered event chains from each root."""
        outgoing, incoming, event_data = await self._build_causal_graph(workspace_id)
        if not outgoing:
            return []

        cycle_nodes = self._detect_cycles(outgoing)
        # Roots have no incoming CAUSED edges
        all_nodes = set(outgoing.keys())
        for targets in outgoing.values():
            all_nodes.update(targets)
        roots = [n for n in all_nodes if n not in incoming]

        chains: list[CausalChain] = []
        for root in roots:
            chain_ids = self._trace_chain(root, outgoing)
            depth = self._chain_depth(root, outgoing)
            has_cycle = any(n in cycle_nodes for n in chain_ids)
            ev = event_data.get(root)
            desc = getattr(ev, "description", root) if ev else root
            chains.append(CausalChain(
                root_event_id=root,
                chain=chain_ids,
                depth=depth,
                has_cycle=has_cycle,
                description=f"Chain from '{desc}' ({depth} steps)",
            ))

        return sorted(chains, key=lambda c: c.depth, reverse=True)

    async def identify_root_causes(self, workspace_id: str) -> list[RootCause]:
        """Trace chains to earliest causes with no incoming CAUSED edges."""
        outgoing, incoming, event_data = await self._build_causal_graph(workspace_id)
        all_nodes = set(outgoing.keys())
        for targets in outgoing.values():
            all_nodes.update(targets)
        roots = [n for n in all_nodes if n not in incoming]

        root_causes: list[RootCause] = []
        for root in roots:
            downstream = self._trace_chain(root, outgoing)
            ev = event_data.get(root)
            desc = getattr(ev, "description", root) if ev else root
            confidence = min(1.0, len(downstream) * 0.1 + 0.2)
            root_causes.append(RootCause(
                event_id=root,
                event_description=desc,
                downstream_count=len(downstream) - 1,
                confidence=round(confidence, 3),
            ))
        return sorted(root_causes, key=lambda r: r.downstream_count, reverse=True)

    async def counterfactual_analysis(
        self, workspace_id: str, event_id: str
    ) -> CounterfactualResult:
        """'What if this event hadn't happened?' — remove event and assess impact."""
        outgoing, incoming, event_data = await self._build_causal_graph(workspace_id)

        # Descendants that would be removed if event_id hadn't occurred
        affected = self._trace_chain(event_id, outgoing)
        affected.remove(event_id)  # exclude the event itself

        # Count chains that pass through this event
        removed_chains = 0
        for root in [n for n in outgoing if n not in incoming]:
            chain = self._trace_chain(root, outgoing)
            if event_id in chain:
                removed_chains += 1

        impact = "low"
        if len(affected) >= 5:
            impact = "critical"
        elif len(affected) >= 3:
            impact = "high"
        elif len(affected) >= 1:
            impact = "moderate"

        ev = event_data.get(event_id)
        desc = getattr(ev, "description", event_id) if ev else event_id

        return CounterfactualResult(
            counterfactual_event_id=event_id,
            affected_events=affected,
            removed_chains=removed_chains,
            impact_assessment=(
                f"Removing '{desc}' would have prevented {len(affected)} downstream events "
                f"across {removed_chains} causal chains. Impact: {impact}."
            ),
        )
