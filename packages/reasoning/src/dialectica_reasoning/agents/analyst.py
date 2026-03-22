"""
Analyst Agent — Main analysis agent combining all reasoning capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass

from dialectica_graph import GraphClient
from dialectica_reasoning.query_engine import AnalysisResponse, ConflictQueryEngine


@dataclass
class AnalystState:
    query: str
    workspace_id: str
    mode: str = "general"
    response: AnalysisResponse | None = None
    error: str | None = None


class AnalystAgent:
    """
    Main DIALECTICA analyst agent.

    Runs the full reasoning pipeline: retrieve → symbolic → synthesise → validate.
    """

    def __init__(self, graph_client: GraphClient, gemini_client: object | None = None) -> None:
        self._engine = ConflictQueryEngine(graph_client, gemini_client)

    async def run(self, query: str, workspace_id: str, mode: str = "general") -> AnalysisResponse:
        """Execute analysis and return structured response."""
        return await self._engine.analyze(query, workspace_id, mode=mode)
