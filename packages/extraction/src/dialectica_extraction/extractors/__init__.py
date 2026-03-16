"""
Extractor/enrichment module exports.
"""
from dialectica_extraction.extractors.entity import enrich_actors, deduplicate_nodes
from dialectica_extraction.extractors.coreference import (
    find_coreferences,
    merge_coreferent_nodes,
    token_sort_ratio,
    CoreferenceMatch,
)
from dialectica_extraction.extractors.causal import detect_causal_signals, has_causal_language
from dialectica_extraction.extractors.narrative import analyze_frame, FrameAnalysis
from dialectica_extraction.extractors.emotion import detect_emotions, EmotionDetection
from dialectica_extraction.extractors.temporal import parse_date, extract_temporal_sequence
from dialectica_extraction.extractors.relationship import (
    score_relationship,
    apply_relationship_scoring,
)

__all__ = [
    "enrich_actors",
    "deduplicate_nodes",
    "find_coreferences",
    "merge_coreferent_nodes",
    "token_sort_ratio",
    "CoreferenceMatch",
    "detect_causal_signals",
    "has_causal_language",
    "analyze_frame",
    "FrameAnalysis",
    "detect_emotions",
    "EmotionDetection",
    "parse_date",
    "extract_temporal_sequence",
    "score_relationship",
    "apply_relationship_scoring",
]
