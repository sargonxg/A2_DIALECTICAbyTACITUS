"""KGE (Knowledge Graph Embedding) module — RotatE training, export, prediction."""
from dialectica_reasoning.kge.trainer import KGETrainer
from dialectica_reasoning.kge.exporter import KGEExporter
from dialectica_reasoning.kge.predictor import LinkPredictor
from dialectica_reasoning.kge.config import KGEConfig

__all__ = ["KGETrainer", "KGEExporter", "LinkPredictor", "KGEConfig"]
