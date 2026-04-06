"""GraphRAG modules for DIALECTICA."""

from dialectica_reasoning.graphrag.community import GraphCommunityDetector
from dialectica_reasoning.graphrag.context_builder import ConflictContextBuilder
from dialectica_reasoning.graphrag.knowledge_clusters import (
    ClusterReport,
    KnowledgeCluster,
    KnowledgeClusterDetector,
)
from dialectica_reasoning.graphrag.retriever import ConflictGraphRAGRetriever, RetrievalResult

__all__ = [
    "ConflictGraphRAGRetriever",
    "RetrievalResult",
    "ConflictContextBuilder",
    "GraphCommunityDetector",
    "KnowledgeClusterDetector",
    "KnowledgeCluster",
    "ClusterReport",
]
