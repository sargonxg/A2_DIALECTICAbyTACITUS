"""
Extraction Pipeline — LangGraph DAG for conflict entity extraction.

States: ExtractionState (text, tier, workspace_id, tenant_id, chunks,
        prefilter_results, raw_entities, validated_entities, relationships,
        embeddings, retry_count, errors)

Nodes (10 pipeline steps):
  1. chunk_document: Split text into overlapping chunks (2000 chars, 200 overlap)
  2. gliner_prefilter: GLiNER pre-filter for entity-dense passage selection
  3. extract_entities: Gemini Flash with tier-appropriate JSON schema
  4. validate_schema: Pydantic validation of extracted entities
  5. repair_extraction: Send validation errors back to Gemini (max 3 retries)
  6. extract_relationships: Focused Gemini call for edge extraction
  7. resolve_coreference: Check against existing graph for deduplication
  8. validate_structural: Conflict Grammar constraint checks
  9. compute_embeddings: Vertex AI embeddings for all entities
  10. write_to_graph: Upsert all to Spanner via GraphClient

Conditional edges: validate_schema → pass/fail/max_retries
"""
from __future__ import annotations

# TODO: Implement in Prompt 6
