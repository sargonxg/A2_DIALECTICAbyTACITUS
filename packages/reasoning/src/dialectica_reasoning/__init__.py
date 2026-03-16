"""
DIALECTICA Reasoning Package — GraphRAG + Symbolic Rule Engine + AI Agents.
"""
from dialectica_reasoning.query_engine import ConflictQueryEngine, AnalysisResponse
from dialectica_reasoning.graphrag.retriever import ConflictGraphRAGRetriever
from dialectica_reasoning.graphrag.context_builder import ConflictContextBuilder
from dialectica_reasoning.symbolic.constraint_engine import ConflictGrammarEngine
from dialectica_reasoning.symbolic.escalation import EscalationDetector
from dialectica_reasoning.symbolic.ripeness import RipenessScorer
from dialectica_reasoning.agents.analyst import AnalystAgent
from dialectica_reasoning.agents.mediator import MediatorAgent
from dialectica_reasoning.agents.forecaster import ForecasterAgent
from dialectica_reasoning.agents.comparator import ComparatorAgent
from dialectica_reasoning.agents.theorist import TheoristAgent
from dialectica_reasoning.agents.advisor import AdvisorAgent

__all__ = [
    "ConflictQueryEngine", "AnalysisResponse",
    "ConflictGraphRAGRetriever", "ConflictContextBuilder",
    "ConflictGrammarEngine", "EscalationDetector", "RipenessScorer",
    "AnalystAgent", "MediatorAgent", "ForecasterAgent",
    "ComparatorAgent", "TheoristAgent", "AdvisorAgent",
]
