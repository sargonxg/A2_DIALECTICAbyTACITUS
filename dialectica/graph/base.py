"""Graph adapter contract for the TACITUS core v1 pipeline."""

from __future__ import annotations

from typing import Protocol

from dialectica.ontology.models import GraphPrimitive


class GraphAdapter(Protocol):
    """Synchronous graph adapter used by the local CLI vertical slice."""

    def initialize_schema(self) -> None:
        """Create constraints and indexes."""

    def write_primitive(self, primitive: GraphPrimitive) -> str:
        """Write one primitive and return its ID."""

    def write_primitives(self, primitives: list[GraphPrimitive]) -> list[str]:
        """Write many primitives and return their IDs."""

    def query(self, question: str, workspace_id: str, case_id: str) -> list[dict]:
        """Run an allowlisted semantic query."""

    def episodes(self, workspace_id: str, case_id: str) -> list[dict]:
        """List episodes for a case."""

    def close(self) -> None:
        """Release resources."""
