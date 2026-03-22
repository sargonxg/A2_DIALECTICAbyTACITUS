"""
Response Models — Data classes for graph query results.

SubgraphResult, ScoredNode, WorkspaceStats, ActorNetworkResult, EscalationResult.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from dialectica_ontology.primitives import ConflictNode
from dialectica_ontology.relationships import ConflictRelationship


@dataclass
class SubgraphResult:
    """Result of a multi-hop traversal or subgraph query."""

    nodes: list[ConflictNode] = field(default_factory=list)
    edges: list[ConflictRelationship] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return len(self.edges)


@dataclass
class ScoredNode:
    """A node with a similarity score from vector search."""

    node: ConflictNode
    score: float  # cosine similarity (higher = more similar)
    distance: float  # cosine distance (lower = more similar)


@dataclass
class WorkspaceStats:
    """Aggregate statistics for a workspace's graph."""

    node_counts_by_label: dict[str, int] = field(default_factory=dict)
    edge_counts_by_type: dict[str, int] = field(default_factory=dict)
    total_nodes: int = 0
    total_edges: int = 0
    density: float = 0.0

    def compute_density(self) -> float:
        """Graph density = |E| / (|V| * (|V| - 1))."""
        if self.total_nodes < 2:
            return 0.0
        max_edges = self.total_nodes * (self.total_nodes - 1)
        self.density = self.total_edges / max_edges if max_edges > 0 else 0.0
        return self.density


@dataclass
class ActorNetworkResult:
    """Network analysis result centered on a specific actor."""

    actor: ConflictNode
    allies: list[ConflictNode] = field(default_factory=list)
    opponents: list[ConflictNode] = field(default_factory=list)
    connections: list[ConflictRelationship] = field(default_factory=list)
    centrality_scores: dict[str, float] = field(default_factory=dict)


@dataclass
class EscalationTrajectoryPoint:
    """A single point on an escalation trajectory."""

    timestamp: datetime
    glasl_stage: int
    evidence: str


@dataclass
class EscalationResult:
    """Glasl escalation trajectory analysis for a workspace."""

    trajectory: list[EscalationTrajectoryPoint] = field(default_factory=list)
    current_stage: int | None = None
    velocity: float = 0.0  # stages per month (positive = escalating)
    direction: str = "stable"  # "escalating", "de-escalating", "stable"
