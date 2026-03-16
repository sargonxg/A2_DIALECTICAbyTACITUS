"""
Network Metrics — Graph topology analysis using networkx.

Computes centrality measures, detects communities, identifies brokers,
and measures polarisation.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from dialectica_graph import GraphClient
from dialectica_ontology.relationships import EdgeType

try:
    import networkx as nx  # type: ignore[import-untyped]
    _NX_AVAILABLE = True
except ImportError:
    _NX_AVAILABLE = False


@dataclass
class ActorCentrality:
    actor_id: str
    betweenness: float = 0.0
    closeness: float = 0.0
    eigenvector: float = 0.0
    degree: int = 0


@dataclass
class Community:
    community_id: int
    actor_ids: list[str] = field(default_factory=list)
    dominant_issues: list[str] = field(default_factory=list)
    escalation_level: str = "unknown"
    summary: str = ""


@dataclass
class BrokerActor:
    actor_id: str
    betweenness: float
    bridges_communities: list[int] = field(default_factory=list)
    mediation_potential: float = 0.0


@dataclass
class PolarisationReport:
    modularity: float = 0.0
    num_communities: int = 0
    polarisation_level: str = "low"
    most_isolated_community: int | None = None
    inter_community_edges: int = 0
    intra_community_edges: int = 0


class NetworkAnalyzer:
    """Computes network topology metrics for the conflict actor graph."""

    def __init__(self, graph_client: GraphClient) -> None:
        self._gc = graph_client

    async def _build_actor_graph(self, workspace_id: str) -> "nx.Graph":
        """Build networkx graph from actor nodes and edges between actors."""
        actors = await self._gc.get_nodes(workspace_id, label="Actor")
        edges = await self._gc.get_edges(workspace_id)
        actor_ids = {a.id for a in actors}

        G = nx.Graph() if _NX_AVAILABLE else None
        if G is None:
            return G  # type: ignore[return-value]

        for a in actors:
            G.add_node(a.id, label=getattr(a, "name", a.id))

        # Include edges between actors (interactions, alliances, oppositions)
        relevant_types = {
            EdgeType.PARTY_TO, EdgeType.ALLIED_WITH, EdgeType.OPPOSED_TO,
            EdgeType.TRUSTS, EdgeType.HAS_POWER_OVER,
        }
        for e in edges:
            if e.source_id in actor_ids and e.target_id in actor_ids:
                weight = float(e.weight) if e.weight else 1.0
                G.add_edge(e.source_id, e.target_id, weight=weight, edge_type=e.type)
        return G

    async def compute_centrality(self, workspace_id: str) -> list[ActorCentrality]:
        """Compute betweenness, closeness, and eigenvector centrality per actor."""
        if not _NX_AVAILABLE:
            return []

        G = await self._build_actor_graph(workspace_id)
        if not G or G.number_of_nodes() == 0:
            return []

        results: list[ActorCentrality] = []
        try:
            betweenness = nx.betweenness_centrality(G, normalized=True)
            closeness = nx.closeness_centrality(G)
            try:
                eigenvector = nx.eigenvector_centrality(G, max_iter=100)
            except nx.PowerIterationFailedConvergence:
                eigenvector = {n: 0.0 for n in G.nodes()}

            for node in G.nodes():
                results.append(ActorCentrality(
                    actor_id=node,
                    betweenness=round(betweenness.get(node, 0.0), 4),
                    closeness=round(closeness.get(node, 0.0), 4),
                    eigenvector=round(eigenvector.get(node, 0.0), 4),
                    degree=G.degree(node),  # type: ignore[arg-type]
                ))
        except Exception:
            pass
        return sorted(results, key=lambda r: r.betweenness, reverse=True)

    async def detect_communities(self, workspace_id: str) -> list[Community]:
        """Detect communities using Louvain algorithm."""
        if not _NX_AVAILABLE:
            return []

        G = await self._build_actor_graph(workspace_id)
        if not G or G.number_of_nodes() < 2:
            return []

        try:
            partition = nx.community.louvain_communities(G, seed=42)
        except Exception:
            # Fallback: connected components
            partition = list(nx.connected_components(G))

        communities: list[Community] = []
        for i, community_set in enumerate(partition):
            communities.append(Community(
                community_id=i,
                actor_ids=list(community_set),
                summary=f"Community {i}: {len(community_set)} actors",
            ))
        return communities

    async def identify_brokers(self, workspace_id: str) -> list[BrokerActor]:
        """Identify high-betweenness actors that bridge communities."""
        if not _NX_AVAILABLE:
            return []

        centrality = await self.compute_centrality(workspace_id)
        communities = await self.detect_communities(workspace_id)

        actor_community: dict[str, int] = {}
        for comm in communities:
            for actor_id in comm.actor_ids:
                actor_community[actor_id] = comm.community_id

        brokers: list[BrokerActor] = []
        for c in centrality:
            if c.betweenness < 0.1:
                continue
            bridges = set()
            G = await self._build_actor_graph(workspace_id)
            if G and c.actor_id in G:
                for neighbor in G.neighbors(c.actor_id):
                    nc = actor_community.get(neighbor)
                    ac = actor_community.get(c.actor_id)
                    if nc is not None and nc != ac:
                        bridges.add(nc)
            brokers.append(BrokerActor(
                actor_id=c.actor_id,
                betweenness=c.betweenness,
                bridges_communities=list(bridges),
                mediation_potential=round(min(1.0, c.betweenness * 2), 3),
            ))
        return sorted(brokers, key=lambda b: b.betweenness, reverse=True)

    async def compute_polarization(self, workspace_id: str) -> PolarisationReport:
        """Measure polarisation using modularity-based community detection."""
        if not _NX_AVAILABLE:
            return PolarisationReport()

        G = await self._build_actor_graph(workspace_id)
        if not G or G.number_of_nodes() < 2:
            return PolarisationReport()

        communities = await self.detect_communities(workspace_id)
        if not communities:
            return PolarisationReport()

        community_sets = [set(c.actor_ids) for c in communities]
        try:
            modularity = nx.community.modularity(G, community_sets)
        except Exception:
            modularity = 0.0

        # Count inter vs intra community edges
        actor_community: dict[str, int] = {}
        for c in communities:
            for a in c.actor_ids:
                actor_community[a] = c.community_id

        intra = inter = 0
        for u, v in G.edges():
            if actor_community.get(u) == actor_community.get(v):
                intra += 1
            else:
                inter += 1

        level = "low"
        if modularity > 0.6:
            level = "high"
        elif modularity > 0.3:
            level = "moderate"

        sizes = [(len(c.actor_ids), c.community_id) for c in communities]
        most_isolated = min(sizes, key=lambda x: x[0])[1] if sizes else None

        return PolarisationReport(
            modularity=round(modularity, 4),
            num_communities=len(communities),
            polarisation_level=level,
            most_isolated_community=most_isolated,
            inter_community_edges=inter,
            intra_community_edges=intra,
        )
