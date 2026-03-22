"""
Extractor/enrichment module exports.
"""

from dialectica_extraction.extractors.causal import detect_causal_signals, has_causal_language
from dialectica_extraction.extractors.coreference import (
    CoreferenceMatch,
    find_coreferences,
    merge_coreferent_nodes,
    token_sort_ratio,
)
from dialectica_extraction.extractors.emotion import EmotionDetection, detect_emotions
from dialectica_extraction.extractors.entity import deduplicate_nodes, enrich_actors
from dialectica_extraction.extractors.narrative import FrameAnalysis, analyze_frame
from dialectica_extraction.extractors.relationship import (
    apply_relationship_scoring,
    score_relationship,
)
from dialectica_extraction.extractors.temporal import extract_temporal_sequence, parse_date

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
