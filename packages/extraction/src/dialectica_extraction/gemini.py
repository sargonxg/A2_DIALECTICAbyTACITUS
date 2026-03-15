"""
Gemini Extractor — Vertex AI Gemini integration for conflict entity extraction.

GeminiExtractor.extract():
  - Builds tier-appropriate prompt (system + extraction tier prompt)
  - Calls Gemini with response_mime_type="application/json" + response_schema
  - Parses JSON response into Pydantic ConflictPrimitive models
  - Returns ExtractionResult with nodes, edges, and extraction metadata

Models: gemini-2.5-flash-001 (default), gemini-2.5-pro-001 (complex cases)
Cost tracking: tokens in/out, estimated cost per extraction
"""
from __future__ import annotations

# TODO: Implement in Prompt 6
