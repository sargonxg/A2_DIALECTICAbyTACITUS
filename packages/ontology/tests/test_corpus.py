"""Tests for ConflictCorpus — the core queryable entity."""

from dialectica_ontology.corpus import (
    ConflictCorpus,
    CorpusAnalytics,
    CorpusBenchmarkScore,
    SourceDocument,
)
from dialectica_ontology.domains import TacitusDomain


class TestConflictCorpus:
    def test_create_corpus(self):
        corpus = ConflictCorpus(
            workspace_id="ws-123",
            tenant_id="t-456",
            title="JCPOA Nuclear Crisis",
            domain=TacitusDomain.CONFLICT_WARFARE,
        )
        assert corpus.workspace_id == "ws-123"
        assert corpus.domain == TacitusDomain.CONFLICT_WARFARE
        assert corpus.is_conflict_warfare is True
        assert corpus.is_human_friction is False

    def test_create_human_friction_corpus(self):
        corpus = ConflictCorpus(
            workspace_id="ws-789",
            tenant_id="t-456",
            title="Workplace Dispute",
            domain=TacitusDomain.HUMAN_FRICTION,
        )
        assert corpus.is_human_friction is True
        assert corpus.is_conflict_warfare is False

    def test_add_source_document(self):
        corpus = ConflictCorpus(workspace_id="ws-1", tenant_id="t-1")
        doc = SourceDocument(title="JCPOA Text", word_count=1500)
        corpus.add_source_document(doc)
        assert len(corpus.source_documents) == 1
        assert corpus.total_source_words == 1500
        assert corpus.last_ingestion_at is not None

    def test_update_analytics(self):
        corpus = ConflictCorpus(workspace_id="ws-1", tenant_id="t-1")
        corpus.update_analytics(
            total_nodes=50,
            total_edges=75,
            glasl_stage=6,
            ripeness_score=0.35,
        )
        assert corpus.analytics.total_nodes == 50
        assert corpus.analytics.glasl_stage == 6
        assert corpus.glasl_stage == 6
        assert corpus.node_count == 50

    def test_add_benchmark_score(self):
        corpus = ConflictCorpus(workspace_id="ws-1", tenant_id="t-1")
        score = CorpusBenchmarkScore(
            benchmark_id="bench-001",
            f1=0.82,
            precision=0.85,
            recall=0.79,
            hallucination_rate=0.05,
        )
        corpus.add_benchmark_score(score)
        assert corpus.latest_benchmark_f1 == 0.82
        assert corpus.analytics.benchmark_f1 == 0.82

    def test_to_summary(self):
        corpus = ConflictCorpus(
            workspace_id="ws-1",
            tenant_id="t-1",
            title="Test Conflict",
            domain=TacitusDomain.CONFLICT_WARFARE,
        )
        corpus.update_analytics(total_nodes=10, total_edges=15, glasl_stage=3)
        summary = corpus.to_summary()
        assert summary["title"] == "Test Conflict"
        assert summary["node_count"] == 10
        assert summary["glasl_stage"] == 3

    def test_corpus_id_auto_generated(self):
        c1 = ConflictCorpus(workspace_id="ws-1", tenant_id="t-1")
        c2 = ConflictCorpus(workspace_id="ws-2", tenant_id="t-2")
        assert c1.id != c2.id
        assert len(c1.id) > 0


class TestCorpusAnalytics:
    def test_default_analytics(self):
        analytics = CorpusAnalytics()
        assert analytics.total_nodes == 0
        assert analytics.glasl_stage is None
        assert analytics.benchmark_f1 is None

    def test_analytics_with_values(self):
        analytics = CorpusAnalytics(
            total_nodes=50,
            total_edges=75,
            glasl_stage=6,
            ripeness_score=0.35,
            patterns_detected=["escalation_spiral", "trust_deficit"],
        )
        assert analytics.glasl_stage == 6
        assert len(analytics.patterns_detected) == 2
