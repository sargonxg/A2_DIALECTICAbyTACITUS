"""Tests for ConfliBERT event classifier."""
from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_ontology.enums import EventType
from dialectica_extraction.conflibert import ConfliBERTClassifier, _CONFLIBERT_TO_ACO


class TestConfliBERTMapping:
    def test_all_mappings_produce_valid_event_types(self):
        for label, event_type in _CONFLIBERT_TO_ACO.items():
            assert isinstance(event_type, EventType)
            assert isinstance(label, str)
            assert len(label) > 0

    def test_protest_maps_correctly(self):
        assert _CONFLIBERT_TO_ACO["protest"] == EventType.PROTEST

    def test_assault_maps_correctly(self):
        assert _CONFLIBERT_TO_ACO["assault"] == EventType.ASSAULT

    def test_agreement_maps_correctly(self):
        assert _CONFLIBERT_TO_ACO["agreement"] == EventType.AGREE


class TestConfliBERTClassifier:
    def test_classifier_construction(self):
        clf = ConfliBERTClassifier()
        assert clf._model_name == "snowood1/ConfliBERT-scr-uncased"

    def test_classify_returns_event_type(self):
        """Even without model loaded, fallback returns valid EventType."""
        clf = ConfliBERTClassifier()
        clf._pipeline = None  # Force fallback
        result = clf.classify_event_type("Armed forces attacked the village")
        assert isinstance(result, EventType)

    def test_classify_batch_returns_list(self):
        clf = ConfliBERTClassifier()
        clf._pipeline = None  # Force fallback
        results = clf.classify_batch(["Text 1", "Text 2"])
        assert len(results) == 2
        assert all(isinstance(r, EventType) for r in results)

    def test_extract_actors_returns_list(self):
        clf = ConfliBERTClassifier()
        clf._ner_pipeline = None
        result = clf.extract_conflict_actors("The United States imposed sanctions on Iran")
        assert isinstance(result, list)
