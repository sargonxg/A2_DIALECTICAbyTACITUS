"""KGE (Knowledge Graph Embedding) module — RotatE training, export, prediction.

Requires optional dependencies: pip install dialectica-reasoning[kge]
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    from dialectica_reasoning.kge.trainer import KGETrainer
    from dialectica_reasoning.kge.exporter import KGEExporter
    from dialectica_reasoning.kge.predictor import LinkPredictor
    from dialectica_reasoning.kge.config import KGEConfig

    KGE_AVAILABLE = True
except ImportError:
    KGE_AVAILABLE = False
    logger.warning(
        "KGE features unavailable: install with pip install dialectica-reasoning[kge]"
    )

    # Provide stubs so downstream code can check KGE_AVAILABLE
    KGETrainer = None  # type: ignore[assignment,misc]
    KGEExporter = None  # type: ignore[assignment,misc]
    LinkPredictor = None  # type: ignore[assignment,misc]
    KGEConfig = None  # type: ignore[assignment,misc]

__all__ = ["KGE_AVAILABLE", "KGETrainer", "KGEExporter", "LinkPredictor", "KGEConfig"]
