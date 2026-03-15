"""
Conflict Context Builder — Format graph retrieval results into LLM-ready context.

ConflictContextBuilder.build_context():
  Structures retrieved entities and relationships into text blocks:
  - Workspace summary (conflict name, domain, scale)
  - Actors section with connections
  - Events section (chronological with CAUSED chains)
  - Theory assessment (Glasl stage, Kriesberg phase, trust scores)
  - Issues and interests (Fisher/Ury positions vs interests)
  - Norms and violations (Standard+ tier)
  - Narratives (Full tier)

Output optimized for Gemini Pro context window efficiency.
"""
from __future__ import annotations

# TODO: Implement in Prompt 7
