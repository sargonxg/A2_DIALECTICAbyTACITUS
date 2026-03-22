"""KGE Trainer — Train RotatE model on conflict graph triples via PyKEEN."""

from __future__ import annotations

import logging
from typing import Any

from dialectica_reasoning.kge.config import KGEConfig

logger = logging.getLogger(__name__)


class KGETrainer:
    """Train a knowledge graph embedding model using PyKEEN.

    Args:
        config: Hyperparameter configuration.
    """

    def __init__(self, config: KGEConfig | None = None) -> None:
        self._config = config or KGEConfig()
        self._result: Any = None

    def train(self, triples_factory: Any) -> Any:
        """Train the KGE model on a TriplesFactory.

        Args:
            triples_factory: PyKEEN TriplesFactory with training triples.

        Returns:
            PyKEEN pipeline result.
        """
        try:
            from pykeen.pipeline import pipeline

            self._result = pipeline(
                training=triples_factory,
                model=self._config.model,
                model_kwargs={"embedding_dim": self._config.embedding_dim},
                training_kwargs={
                    "num_epochs": self._config.epochs,
                    "batch_size": self._config.batch_size,
                },
                optimizer_kwargs={"lr": self._config.learning_rate},
                negative_sampler=self._config.negative_sampling,
                negative_sampler_kwargs={"num_negs_per_pos": self._config.num_negatives},
                evaluation_kwargs={"batch_size": self._config.evaluation_batch_size},
            )

            logger.info(
                "KGE training complete: model=%s dim=%d epochs=%d",
                self._config.model,
                self._config.embedding_dim,
                self._config.epochs,
            )
            return self._result
        except ImportError as err:
            raise ImportError("PyKEEN not installed") from err

    def get_entity_embeddings(self) -> dict[str, list[float]]:
        """Extract entity embeddings from trained model.

        Returns:
            Dict mapping entity label to embedding vector.
        """
        if self._result is None:
            raise RuntimeError("Model not trained yet — call train() first")

        model = self._result.model
        factory = self._result.training

        embeddings: dict[str, list[float]] = {}
        entity_to_id = factory.entity_to_id

        for entity_label, entity_id in entity_to_id.items():
            emb = (
                model.entity_representations[0](indices=None)[entity_id]
                .detach()
                .cpu()
                .numpy()
                .tolist()
            )
            embeddings[entity_label] = emb

        return embeddings

    @property
    def result(self) -> Any:
        return self._result
