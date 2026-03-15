"""
GLiNER Pre-filter — Zero-shot NER for conflict entity-dense passage selection.

GLiNERPreFilter.prefilter():
  - Runs gliner-community/gliner_medium-v2.5 on input text
  - Uses 14 conflict-specific labels:
    "conflict actor", "political event", "conflict event", "stated interest",
    "claim or demand", "norm or law", "emotional state", "narrative frame",
    "power relationship", "trust indicator", "conflict process",
    "evidence source", "geographic location", "agreement or outcome"
  - Returns entity-dense windows (passages with >= threshold entity density)
  - Reduces Gemini token cost by 40-60% on large documents

Note: Model downloads ~500MB on first use. Set GLINER_ENABLED=false to skip.
"""
from __future__ import annotations

# TODO: Implement in Prompt 6
