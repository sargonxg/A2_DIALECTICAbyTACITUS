"""KGE hyperparameters."""
from dataclasses import dataclass


@dataclass
class KGEConfig:
    model: str = "RotatE"
    embedding_dim: int = 256
    epochs: int = 500
    learning_rate: float = 0.001
    batch_size: int = 256
    negative_sampling: str = "bernoulli"
    num_negatives: int = 64
    regularizer_weight: float = 1e-5
    evaluation_batch_size: int = 128
