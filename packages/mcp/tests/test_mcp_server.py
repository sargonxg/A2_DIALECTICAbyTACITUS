"""Tests for DIALECTICA MCP server — tool definitions and resources."""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestMCPServerCreation:
    def test_create_server(self):
        """Server creates successfully with all tools registered."""
        with patch.dict(os.environ, {"GRAPH_BACKEND": "falkordb"}):
            from dialectica_mcp.server import create_mcp_server

            mcp = create_mcp_server()
            assert mcp is not None


class TestResources:
    def test_ontology_schema(self):
        from dialectica_mcp.resources import get_ontology_schema

        schema = get_ontology_schema()
        assert "node_types" in schema
        assert "edge_types" in schema
        assert "tiers" in schema
        assert len(schema["node_types"]) > 0

    def test_ontology_schema_has_actor(self):
        from dialectica_mcp.resources import get_ontology_schema

        schema = get_ontology_schema()
        names = [nt["name"] for nt in schema["node_types"]]
        assert "Actor" in names
        assert "Conflict" in names
        assert "Event" in names


class TestGraphClientFactory:
    def test_falkordb_config(self):
        with (
            patch.dict(
                os.environ,
                {
                    "GRAPH_BACKEND": "falkordb",
                    "FALKORDB_HOST": "test-host",
                    "FALKORDB_PORT": "6380",
                },
            ),
            patch("dialectica_mcp.server.create_graph_client") as mock_create,
        ):
            mock_create.return_value = MagicMock()
            from dialectica_mcp.server import _get_graph_client

            _get_graph_client()
            mock_create.assert_called_once_with(
                backend="falkordb",
                config={"host": "test-host", "port": 6380},
            )

    def test_neo4j_config(self):
        with (
            patch.dict(
                os.environ,
                {
                    "GRAPH_BACKEND": "neo4j",
                    "NEO4J_URI": "bolt://neo4j:7687",
                    "NEO4J_USER": "neo4j",
                    "NEO4J_PASSWORD": "pass",
                },
            ),
            patch("dialectica_mcp.server.create_graph_client") as mock_create,
        ):
            mock_create.return_value = MagicMock()
            from dialectica_mcp.server import _get_graph_client

            _get_graph_client()
            mock_create.assert_called_once()


class TestExtractionMessage:
    """Test the ingest_document tool's pipeline integration."""

    def test_extraction_pipeline_import(self):
        """Verify extraction pipeline can be imported."""
        from dialectica_extraction.pipeline import ExtractionPipeline

        assert ExtractionPipeline is not None

    def test_ontology_tier_values(self):
        from dialectica_ontology.tiers import OntologyTier

        assert OntologyTier("essential") == OntologyTier.ESSENTIAL
        assert OntologyTier("standard") == OntologyTier.STANDARD
        assert OntologyTier("full") == OntologyTier.FULL
