"""
Tests for KGE module availability and graceful degradation.

When torch/pykeen are not installed, KGE_AVAILABLE should be False
and all exported names should be None stubs.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_reasoning.kge import KGE_AVAILABLE


def test_kge_available_flag_is_bool():
    """KGE_AVAILABLE must be a bool regardless of torch installation status."""
    assert isinstance(KGE_AVAILABLE, bool)


def test_kge_imports_without_torch():
    """If torch is not installed, KGE_AVAILABLE should be False
    and the exported stubs (KGETrainer, KGEConfig, etc.) should be None.
    If torch IS installed, KGE_AVAILABLE is True and they are real classes."""
    from dialectica_reasoning.kge import KGEConfig, KGETrainer

    if not KGE_AVAILABLE:
        assert KGETrainer is None
        assert KGEConfig is None
    else:
        # When KGE deps are installed, they should be importable classes
        assert KGETrainer is not None
        assert KGEConfig is not None


def test_kge_exporter_and_predictor_stubs():
    """KGEExporter and LinkPredictor follow the same availability pattern."""
    from dialectica_reasoning.kge import KGEExporter, LinkPredictor

    if not KGE_AVAILABLE:
        assert KGEExporter is None
        assert LinkPredictor is None
    else:
        assert KGEExporter is not None
        assert LinkPredictor is not None


def test_kge_all_exports():
    """The __all__ list should contain exactly the expected names."""
    from dialectica_reasoning import kge

    expected = {"KGE_AVAILABLE", "KGETrainer", "KGEExporter", "LinkPredictor", "KGEConfig"}
    assert set(kge.__all__) == expected
