"""GraphRAG modules for DIALECTICA."""
from dialectica_reasoning.graphrag.retriever import ConflictGraphRAGRetriever, RetrievalResult
from dialectica_reasoning.graphrag.context_builder import ConflictContextBuilder
from dialectica_reasoning.graphrag.community import GraphCommunityDetector

__all__ = [
    "ConflictGraphRAGRetriever",
    "RetrievalResult",
    "ConflictContextBuilder",
    "GraphCommunityDetector",
]
