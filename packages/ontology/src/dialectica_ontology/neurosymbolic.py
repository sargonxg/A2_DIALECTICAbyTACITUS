"""
Neurosymbolic Architecture Configuration — TACITUS four-layer system.

Converts the NEUROSYMBOLIC dict from ontology.py into structured configuration:
  NeurosymbolicConfig: Full architecture description
  SymbolicLayerConfig: All 9 symbolic components
  NeuralLayerConfig: All 7 neural components + embedding specs
  BridgeConfig: Reason-then-embed pattern
  ScientificRisks: Risk categories + mitigations

Architecture layers:
  1. Neural Ingestion (GLiNER + Gemini)
  2. Symbolic Representation (Conflict Grammar + Spanner Graph)
  3. Reasoning/Inference (Rules + GraphRAG + GNN)
  4. Decision Support (Agents + Human loop)
"""
from __future__ import annotations

# TODO: Implement in Prompt 3
