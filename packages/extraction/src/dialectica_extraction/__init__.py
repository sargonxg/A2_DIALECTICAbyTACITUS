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
