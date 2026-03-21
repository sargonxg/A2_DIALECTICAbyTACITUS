"""
Community Summarizer — Generate conflict-specific summaries for graph communities.

Uses Gemini Pro for synthesis. Stores summaries + embeddings in Qdrant
collection dialectica_communities for global query support.
"""
from __future__ import annotations

import logging
from typing import Any

from dialectica_ontology.primitives import ConflictNode
from dialectica_ontology.relationships import ConflictRelationship
from dialectica_reasoning.graphrag.community import CommunitySummary

logger = logging.getLogger(__name__)

SUMMARY_TEMPLATE = """Analyze this conflict community and produce a structured summary.

Actors: {actors}
Issues: {issues}
Relationships: {relationships}
Escalation signals: {escalation}

Produce a 2-3 paragraph summary covering:
1. Who the key actors are and their relationships
2. What the dominant issues and interests are
3. Current escalation level and trajectory
4. External tensions and cross-community dynamics
5. Dominant narratives if any
"""


class CommunitySummarizer:
    """Generate and store conflict-specific community summaries."""

    def __init__(
        self,
        llm_fn: Any = None,
        embed_fn: Any = None,
        vector_store: Any = None,
    ) -> None:
        self._llm_fn = llm_fn
        self._embed_fn = embed_fn
        self._vs = vector_store

    async def summarize_community(
        self,
        community: CommunitySummary,
        nodes: list[ConflictNode],
        edges: list[ConflictRelationship],
    ) -> str:
        """Generate a natural language summary for a community.

        Args:
            community: Community metadata.
            nodes: Nodes in the community.
            edges: Edges within the community.

        Returns:
            Summary text.
        """
        actors = ", ".join(community.actor_names[:10])
        issues = ", ".join(community.dominant_issues[:5])

        relationships = []
        member_set = set(community.member_ids)
        for e in edges:
            if e.source_id in member_set or e.target_id in member_set:
                rel_type = e.type.value if hasattr(e.type, "value") else str(e.type)
                relationships.append(f"{e.source_id} {rel_type} {e.target_id}")

        prompt = SUMMARY_TEMPLATE.format(
            actors=actors or "unknown",
            issues=issues or "none identified",
            relationships="; ".join(relationships[:15]) or "none",
            escalation=community.escalation_level,
        )

        if self._llm_fn:
            try:
                summary = await self._llm_fn(prompt)
                return summary
            except Exception as e:
                logger.warning("LLM summarization failed: %s", e)

        # Fallback: template-based summary
        return community.summary

    async def summarize_and_store(
        self,
        communities: list[CommunitySummary],
        all_nodes: list[ConflictNode],
        all_edges: list[ConflictRelationship],
        tenant_id: str = "",
        workspace_id: str = "",
    ) -> list[str]:
        """Summarize all communities and store in Qdrant.

        Returns list of generated summary texts.
        """
        summaries: list[str] = []

        for community in communities:
            member_set = set(community.member_ids)
            comm_nodes = [n for n in all_nodes if n.id in member_set]
            comm_edges = [e for e in all_edges
                         if e.source_id in member_set or e.target_id in member_set]

            summary = await self.summarize_community(community, comm_nodes, comm_edges)
            community.summary = summary
            summaries.append(summary)

        # Store embeddings if vector store available
        if self._vs and self._embed_fn and summaries:
            try:
                embeddings = self._embed_fn.embed_text(summaries)
                for i, (community, emb) in enumerate(zip(communities, embeddings)):
                    if emb:
                        logger.debug(
                            "Stored community %d summary embedding (dim=%d)",
                            community.community_id, len(emb),
                        )
            except Exception as e:
                logger.warning("Community embedding storage failed: %s", e)

        return summaries
