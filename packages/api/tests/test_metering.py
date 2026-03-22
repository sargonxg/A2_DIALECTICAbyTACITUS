"""Tests for metering middleware and API key management."""

from __future__ import annotations

from dialectica_api.middleware.metering import _classify_operation
from dialectica_api.routers.api_keys import VALID_SCOPES, _generate_key


class TestMeteringClassification:
    def test_extract_classified(self):
        assert _classify_operation("POST", "/v1/workspaces/ws/extract") == "extract"

    def test_graph_query_classified(self):
        assert _classify_operation("GET", "/v1/workspaces/ws/graph") == "graph_query"

    def test_reasoning_classified(self):
        assert _classify_operation("POST", "/v1/workspaces/ws/analyze") == "reasoning"

    def test_health_not_metered(self):
        assert _classify_operation("GET", "/health") is None
        assert _classify_operation("GET", "/metrics") is None

    def test_graph_write(self):
        assert _classify_operation("POST", "/v1/workspaces/ws/entities") == "graph_write"

    def test_graph_read(self):
        assert _classify_operation("GET", "/v1/workspaces/ws/entities") == "graph_read"


class TestAPIKeyGeneration:
    def test_live_key_prefix(self):
        key = _generate_key("live")
        assert key.startswith("pk_live_")
        assert len(key) > 20

    def test_test_key_prefix(self):
        key = _generate_key("test")
        assert key.startswith("pk_test_")

    def test_keys_are_unique(self):
        k1 = _generate_key("live")
        k2 = _generate_key("live")
        assert k1 != k2


class TestValidScopes:
    def test_scopes_defined(self):
        assert "graph:read" in VALID_SCOPES
        assert "graph:write" in VALID_SCOPES
        assert "extract" in VALID_SCOPES
        assert "reason" in VALID_SCOPES
        assert "admin" in VALID_SCOPES
