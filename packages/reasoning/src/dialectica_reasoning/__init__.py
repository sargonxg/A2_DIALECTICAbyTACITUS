"""
DIALECTICA Reasoning Package — GraphRAG + Symbolic Rule Engine + AI Agents.

GraphRAG Layer:
  ConflictGraphRAGRetriever: Hybrid vector + graph retrieval
  ConflictContextBuilder: Format retrieved graph into LLM-ready context

Symbolic Layer:
  ConflictGrammarEngine: All symbolic rules from ontology.py
  Escalation detector (Glasl stage classification)
  Ripeness scorer (Zartman MHS composite)
  Trust analyzer (Mayer/Davis/Schoorman)
  Power mapper (French/Raven)
  Causal chain analyzer (Pearl-informed)
  Network metrics (networkx centrality + community detection)

Agent Layer:
  AnalystAgent: Main LangGraph agent combining GraphRAG + symbolic reasoning
  MediatorAgent: Mediation strategy generator (Fisher/Ury + BATNA)
  ForecasterAgent: Escalation prediction
  ComparatorAgent: Cross-workspace conflict comparison
"""
