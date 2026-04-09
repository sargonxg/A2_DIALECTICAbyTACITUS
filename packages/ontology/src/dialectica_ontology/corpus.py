"""
ConflictCorpus — The Core Queryable Entity in DIALECTICA.

A ConflictCorpus is the primary container and unit of analysis in DIALECTICA.
It wraps a workspace's conflict knowledge graph with metadata, domain classification,
and computed analytics. Every query, benchmark, and agent interaction targets
a ConflictCorpus.

Hierarchy:
    Tenant -> Workspace -> ConflictCorpus -> (Nodes + Edges + Embeddings + Analytics)

A ConflictCorpus is created when text is ingested into a workspace. It tracks:
- Source documents and extraction provenance
- The complete conflict graph (nodes, edges, embeddings)
- Domain classification (human friction vs conflict/warfare)
- Computed analytics (Glasl stage, ripeness, patterns, clusters)
- Benchmark scores and quality metrics

Usage:
    corpus = ConflictCorpus(
        workspace_id="ws-123",
        tenant_id="t-456",
        domain=TacitusDomain.CONFLICT_WARFARE,
        title="JCPOA Nuclear Crisis",
    )
    corpus.update_analytics(glasl_stage=6, ripeness_score=0.35)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from ulid import ULID

from dialectica_ontology.domains import TacitusDomain


def _ulid() -> str:
    return str(ULID())


# ─── Source Document ──────────────────────────────────────────────────────────


class SourceDocument(BaseModel):
    """A document ingested into a ConflictCorpus."""

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(default_factory=_ulid)
    title: str = ""
    content_hash: str = ""  # SHA-256 of source text
    word_count: int = 0
    language: str = "en"
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    extraction_tier: str = "standard"
    extraction_model: str = "gemini-2.5-flash"
    nodes_extracted: int = 0
    edges_extracted: int = 0
    errors: int = 0


# ─── Corpus Analytics ─────────────────────────────────────────────────────────


class CorpusAnalytics(BaseModel):
    """Computed analytics for a ConflictCorpus."""

    model_config = ConfigDict(use_enum_values=True)

    # Graph metrics
    total_nodes: int = 0
    total_edges: int = 0
    node_types: dict[str, int] = Field(default_factory=dict)
    edge_types: dict[str, int] = Field(default_factory=dict)
    graph_density: float = 0.0

    # Conflict assessment
    glasl_stage: int | None = None
    glasl_level: str | None = None  # win_win, win_lose, lose_lose
    kriesberg_phase: str | None = None
    ripeness_score: float | None = None
    is_ripe: bool | None = None

    # Pattern detection
    patterns_detected: list[str] = Field(default_factory=list)
    escalation_velocity: float | None = None
    escalation_direction: str | None = None  # escalating, de_escalating, stable

    # Knowledge clusters
    cluster_count: int = 0
    subdomain: str | None = None
    cross_cluster_edges: int = 0

    # Trust and power
    average_trust: float | None = None
    power_asymmetry: float | None = None

    # Quality metrics
    extraction_confidence: float = 0.0
    benchmark_f1: float | None = None
    hallucination_rate: float | None = None

    computed_at: datetime | None = None


# ─── Benchmark Score ──────────────────────────────────────────────────────────


class CorpusBenchmarkScore(BaseModel):
    """A benchmark evaluation score for a ConflictCorpus."""

    benchmark_id: str = ""
    corpus_id: str = ""
    tier: str = "standard"
    model: str = "gemini-2.5-flash"
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    hallucination_rate: float = 0.0
    extraction_time_ms: float = 0.0
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


# ─── ConflictCorpus ───────────────────────────────────────────────────────────


class ConflictCorpus(BaseModel):
    """
    The Core Queryable Entity in DIALECTICA.

    A ConflictCorpus represents a complete conflict knowledge graph with
    metadata, domain classification, and computed analytics. It is the
    primary unit that agents query, benchmarks evaluate, and the
    TACITUS ecosystem consumes.

    Every workspace maps to exactly one ConflictCorpus.
    """

    model_config = ConfigDict(use_enum_values=True)

    # Identity
    id: str = Field(default_factory=_ulid)
    workspace_id: str
    tenant_id: str

    # Metadata
    title: str = ""
    description: str = ""
    domain: TacitusDomain = TacitusDomain.HUMAN_FRICTION
    subdomain: str = ""
    tags: list[str] = Field(default_factory=list)

    # Lifecycle
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_ingestion_at: datetime | None = None
    last_analysis_at: datetime | None = None

    # Source tracking
    source_documents: list[SourceDocument] = Field(default_factory=list)
    total_source_words: int = 0

    # Computed analytics (cached, refreshed on demand)
    analytics: CorpusAnalytics = Field(default_factory=CorpusAnalytics)

    # Benchmark history
    benchmark_scores: list[CorpusBenchmarkScore] = Field(default_factory=list)

    # ── Convenience Properties ────────────────────────────────────────────

    @property
    def is_human_friction(self) -> bool:
        return self.domain == TacitusDomain.HUMAN_FRICTION

    @property
    def is_conflict_warfare(self) -> bool:
        return self.domain == TacitusDomain.CONFLICT_WARFARE

    @property
    def node_count(self) -> int:
        return self.analytics.total_nodes

    @property
    def edge_count(self) -> int:
        return self.analytics.total_edges

    @property
    def glasl_stage(self) -> int | None:
        return self.analytics.glasl_stage

    @property
    def latest_benchmark_f1(self) -> float | None:
        if self.benchmark_scores:
            return self.benchmark_scores[-1].f1
        return None

    # ── Methods ───────────────────────────────────────────────────────────

    def add_source_document(self, doc: SourceDocument) -> None:
        """Track a new ingested source document."""
        self.source_documents.append(doc)
        self.total_source_words += doc.word_count
        self.last_ingestion_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_analytics(self, **kwargs: Any) -> None:
        """Update computed analytics fields."""
        for key, value in kwargs.items():
            if hasattr(self.analytics, key):
                setattr(self.analytics, key, value)
        self.analytics.computed_at = datetime.utcnow()
        self.last_analysis_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def add_benchmark_score(self, score: CorpusBenchmarkScore) -> None:
        """Record a benchmark evaluation."""
        self.benchmark_scores.append(score)
        self.analytics.benchmark_f1 = score.f1
        self.analytics.hallucination_rate = score.hallucination_rate
        self.updated_at = datetime.utcnow()

    def to_summary(self) -> dict[str, Any]:
        """Return a concise summary for API responses and inter-app communication."""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "title": self.title,
            "domain": self.domain,
            "subdomain": self.subdomain,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "glasl_stage": self.glasl_stage,
            "ripeness_score": self.analytics.ripeness_score,
            "patterns": self.analytics.patterns_detected,
            "benchmark_f1": self.latest_benchmark_f1,
            "source_documents": len(self.source_documents),
            "updated_at": self.updated_at.isoformat(),
        }
