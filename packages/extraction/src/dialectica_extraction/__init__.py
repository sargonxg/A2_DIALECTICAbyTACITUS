"""
DIALECTICA Extraction Package — LangGraph pipeline for conflict entity extraction.

Pipeline: chunk_document → gliner_prefilter → extract_entities → validate_schema
          → repair_extraction → extract_relationships → resolve_coreference
          → validate_structural → compute_embeddings → write_to_graph

Uses:
  - Gemini 2.5 Flash for entity extraction (tier-appropriate schema)
  - Gemini 2.5 Pro for complex relationship extraction
  - GLiNER for pre-filtering entity-dense passages
  - Vertex AI text-embedding-005 for 768-dim embeddings
  - LangGraph for stateful pipeline with retry logic
"""

from dialectica_extraction.pipeline import (
    ExtractionError,
    ExtractionPipeline,
    ExtractionState,
    TextChunk,
    build_pipeline,
    chunk_document,
    compute_embeddings,
    extract_entities,
    extract_relationships,
    gliner_prefilter,
    repair_extraction,
    resolve_coreference,
    validate_schema,
    validate_structural_step,
    write_to_graph,
)

__all__ = [
    "ExtractionPipeline",
    "ExtractionState",
    "TextChunk",
    "ExtractionError",
    "chunk_document",
    "gliner_prefilter",
    "extract_entities",
    "validate_schema",
    "repair_extraction",
    "extract_relationships",
    "resolve_coreference",
    "validate_structural_step",
    "compute_embeddings",
    "write_to_graph",
    "build_pipeline",
]
