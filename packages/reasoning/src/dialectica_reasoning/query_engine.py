"""
Query Engine — Natural language → graph operations → LLM synthesis.

Orchestrates the full reasoning pipeline:
  1. Parse user question (intent classification)
  2. Determine required graph traversals and symbolic rules
  3. Execute hybrid retrieval via GraphRAG retriever
  4. Apply applicable symbolic rule checks
  5. Build structured context for LLM
  6. Synthesize response with Gemini Pro
  7. Return structured response with reasoning trace + citations

Supports query types: entity lookup, causal analysis, comparison,
escalation forecast, mediation strategy, trust assessment.
"""
from __future__ import annotations

# TODO: Implement in Prompt 7
