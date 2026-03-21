"""Tests for KGE training pipeline."""
from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_reasoning.kge.config import KGEConfig
from dialectica_reasoning.kge.graph_to_triples import triples_to_pykeen_factory


class TestKGEConfig:
    def test_defaults(self):
        cfg = KGEConfig()
        assert cfg.model == "RotatE"
        assert cfg.embedding_dim == 256
        assert cfg.epochs == 500

    def test_custom(self):
        cfg = KGEConfig(model="TransE", embedding_dim=128, epochs=100)
        assert cfg.model == "TransE"
        assert cfg.embedding_dim == 128


class TestGraphToTriples:
    def test_triples_factory_creation(self):
        """Small synthetic graph converts to triples factory."""
        triples = [
            ("actor_iran", "PARTY_TO", "conflict_jcpoa"),
            ("actor_usa", "PARTY_TO", "conflict_jcpoa"),
            ("actor_iran", "OPPOSED_TO", "actor_usa"),
            ("event_withdrawal", "CAUSED", "event_sanctions"),
            ("actor_usa", "PARTICIPATED_IN", "event_withdrawal"),
        ]
        try:
            factory = triples_to_pykeen_factory(triples)
            assert factory.num_triples == 5
            assert factory.num_entities == 5
            assert factory.num_relations >= 3
        except ImportError:
            pytest.skip("PyKEEN not installed")

    def test_empty_triples_raises(self):
        with pytest.raises(ValueError, match="No triples"):
            triples_to_pykeen_factory([])


class TestKGETrainer:
    @pytest.mark.slow
    def test_train_small_graph(self):
        """Training on small graph completes without errors."""
        try:
            from dialectica_reasoning.kge.trainer import KGETrainer

            triples = [
                ("A", "R1", "B"),
                ("B", "R2", "C"),
                ("A", "R1", "C"),
                ("C", "R2", "A"),
            ]
            factory = triples_to_pykeen_factory(triples)
            cfg = KGEConfig(epochs=5, embedding_dim=32, batch_size=4)
            trainer = KGETrainer(cfg)
            result = trainer.train(factory)
            assert result is not None

            embeddings = trainer.get_entity_embeddings()
            assert len(embeddings) == 3  # A, B, C
            for emb in embeddings.values():
                assert len(emb) == 32  # embedding_dim
        except ImportError:
            pytest.skip("PyKEEN not installed")


class TestLinkPredictor:
    def test_predictor_construction(self):
        """LinkPredictor can be constructed with a mock result."""
        from dialectica_reasoning.kge.predictor import LinkPredictor, PredictionResult
        from unittest.mock import MagicMock

        mock_result = MagicMock()
        predictor = LinkPredictor(mock_result)
        assert predictor._result is mock_result

    def test_prediction_result_dataclass(self):
        from dialectica_reasoning.kge.predictor import PredictionResult
        pr = PredictionResult(target_id="x", target_label="X", relation="R", score=0.95)
        assert pr.score == 0.95
