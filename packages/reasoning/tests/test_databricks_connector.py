"""
Tests for Databricks Connector.

Mocks databricks.sdk to verify export, training, and prediction operations,
plus graceful degradation when the SDK is unavailable.
"""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reset_module():
    """Reset module-level lazy-import state."""
    import dialectica_reasoning.databricks_connector as mod

    mod._databricks_sdk = None
    mod._sdk_import_attempted = False
    return mod


def _make_connector(mod, mock_sdk=None, **config_kwargs):
    """Create a DatabricksConnector with controllable SDK state."""
    if mock_sdk is not None:
        mod._databricks_sdk = mock_sdk
        mod._sdk_import_attempted = True
    else:
        mod._databricks_sdk = None
        mod._sdk_import_attempted = True

    config = mod.DatabricksConfig(
        workspace_url="https://test.databricks.com",
        token="dapi-test-token",
        cluster_id="cluster-123",
        **config_kwargs,
    )
    return mod.DatabricksConnector(config=config)


# ---------------------------------------------------------------------------
# Tests — DatabricksConfig
# ---------------------------------------------------------------------------


def test_config_defaults():
    """DatabricksConfig should have sensible defaults."""
    mod = _reset_module()
    config = mod.DatabricksConfig()
    assert config.catalog == "dialectica"
    assert config.schema == "conflict_graphs"


def test_config_from_env():
    """DatabricksConfig should read from environment variables."""
    mod = _reset_module()
    env_vars = {
        "DATABRICKS_HOST": "https://env.databricks.com",
        "DATABRICKS_TOKEN": "env-token",
    }
    with patch.dict(os.environ, env_vars):
        config = mod.DatabricksConfig()
    assert config.workspace_url == "https://env.databricks.com"
    assert config.token == "env-token"


# ---------------------------------------------------------------------------
# Tests — export_graph_snapshot
# ---------------------------------------------------------------------------


def test_export_graph_snapshot_success():
    """export_graph_snapshot should execute SQL statements and return ok."""
    mod = _reset_module()
    mock_sdk = MagicMock()
    mock_ws_client = MagicMock()
    mock_sdk.WorkspaceClient.return_value = mock_ws_client

    connector = _make_connector(mod, mock_sdk=mock_sdk)

    nodes = [
        {"id": "n1", "label": "Actor", "name": "Party A"},
        {"id": "n2", "label": "Issue", "name": "Territory"},
    ]
    edges = [
        {"id": "e1", "source_id": "n1", "target_id": "n2", "type": "RAISES"},
    ]

    result = connector.export_graph_snapshot("ws-1", nodes, edges)

    assert result["status"] == "ok"
    assert result["rows_written"] == 3
    assert mock_ws_client.statement_execution.execute_statement.call_count == 2


def test_export_graph_snapshot_empty_data():
    """export_graph_snapshot with empty lists should not execute any statements."""
    mod = _reset_module()
    mock_sdk = MagicMock()
    mock_ws_client = MagicMock()
    mock_sdk.WorkspaceClient.return_value = mock_ws_client

    connector = _make_connector(mod, mock_sdk=mock_sdk)

    result = connector.export_graph_snapshot("ws-1", [], [])

    assert result["status"] == "ok"
    assert result["rows_written"] == 0
    mock_ws_client.statement_execution.execute_statement.assert_not_called()


def test_export_graph_snapshot_unavailable():
    """export_graph_snapshot should return unavailable when SDK is missing."""
    mod = _reset_module()
    connector = _make_connector(mod, mock_sdk=None)

    result = connector.export_graph_snapshot("ws-1", [{"id": "n1"}], [])

    assert result["status"] == "unavailable"


def test_export_graph_snapshot_exception():
    """export_graph_snapshot should return error on exception."""
    mod = _reset_module()
    mock_sdk = MagicMock()
    mock_ws_client = MagicMock()
    mock_ws_client.statement_execution.execute_statement.side_effect = RuntimeError("SQL error")
    mock_sdk.WorkspaceClient.return_value = mock_ws_client

    connector = _make_connector(mod, mock_sdk=mock_sdk)

    result = connector.export_graph_snapshot("ws-1", [{"id": "n1"}], [])

    assert result["status"] == "error"


# ---------------------------------------------------------------------------
# Tests — trigger_kge_training
# ---------------------------------------------------------------------------


def test_trigger_kge_training_success():
    """trigger_kge_training should submit a job and return ok with run_id."""
    mod = _reset_module()
    mock_sdk = MagicMock()
    mock_ws_client = MagicMock()
    mock_run = MagicMock()
    mock_run.run_id = 42
    mock_ws_client.jobs.submit.return_value = mock_run
    mock_sdk.WorkspaceClient.return_value = mock_ws_client

    connector = _make_connector(mod, mock_sdk=mock_sdk)

    result = connector.trigger_kge_training("ws-1", model_type="RotatE", epochs=200)

    assert result["status"] == "ok"
    assert result["run_id"] == 42
    mock_ws_client.jobs.submit.assert_called_once()


def test_trigger_kge_training_unavailable():
    """trigger_kge_training should return unavailable when SDK is missing."""
    mod = _reset_module()
    connector = _make_connector(mod, mock_sdk=None)

    result = connector.trigger_kge_training("ws-1")

    assert result["status"] == "unavailable"


def test_trigger_kge_training_exception():
    """trigger_kge_training should return error on exception."""
    mod = _reset_module()
    mock_sdk = MagicMock()
    mock_ws_client = MagicMock()
    mock_ws_client.jobs.submit.side_effect = RuntimeError("job failed")
    mock_sdk.WorkspaceClient.return_value = mock_ws_client

    connector = _make_connector(mod, mock_sdk=mock_sdk)

    result = connector.trigger_kge_training("ws-1")

    assert result["status"] == "error"


# ---------------------------------------------------------------------------
# Tests — get_kge_predictions
# ---------------------------------------------------------------------------


def test_get_kge_predictions_success():
    """get_kge_predictions should parse result rows correctly."""
    mod = _reset_module()
    mock_sdk = MagicMock()
    mock_ws_client = MagicMock()

    mock_result = MagicMock()
    mock_result.result.data_array = [
        ["tail-1", "0.95"],
        ["tail-2", "0.87"],
    ]
    mock_ws_client.statement_execution.execute_statement.return_value = mock_result
    mock_sdk.WorkspaceClient.return_value = mock_ws_client

    connector = _make_connector(mod, mock_sdk=mock_sdk)

    predictions = connector.get_kge_predictions("head-1", "ALLIES_WITH", top_k=5)

    assert len(predictions) == 2
    assert predictions[0]["tail_id"] == "tail-1"
    assert predictions[0]["score"] == 0.95
    assert predictions[1]["tail_id"] == "tail-2"
    assert predictions[1]["score"] == 0.87


def test_get_kge_predictions_unavailable():
    """get_kge_predictions should return empty list when SDK is missing."""
    mod = _reset_module()
    connector = _make_connector(mod, mock_sdk=None)

    predictions = connector.get_kge_predictions("head-1", "ALLIES_WITH")

    assert predictions == []


def test_get_kge_predictions_exception():
    """get_kge_predictions should return empty list on exception."""
    mod = _reset_module()
    mock_sdk = MagicMock()
    mock_ws_client = MagicMock()
    mock_ws_client.statement_execution.execute_statement.side_effect = RuntimeError("query failed")
    mock_sdk.WorkspaceClient.return_value = mock_ws_client

    connector = _make_connector(mod, mock_sdk=mock_sdk)

    predictions = connector.get_kge_predictions("head-1", "ALLIES_WITH")

    assert predictions == []


def test_get_kge_predictions_empty_result():
    """get_kge_predictions should handle empty result set."""
    mod = _reset_module()
    mock_sdk = MagicMock()
    mock_ws_client = MagicMock()

    mock_result = MagicMock()
    mock_result.result.data_array = []
    mock_ws_client.statement_execution.execute_statement.return_value = mock_result
    mock_sdk.WorkspaceClient.return_value = mock_ws_client

    connector = _make_connector(mod, mock_sdk=mock_sdk)

    predictions = connector.get_kge_predictions("head-1", "ALLIES_WITH")

    assert predictions == []


# ---------------------------------------------------------------------------
# Tests — available property
# ---------------------------------------------------------------------------


def test_available_true_with_sdk():
    """available should be True when SDK and client creation succeed."""
    mod = _reset_module()
    mock_sdk = MagicMock()
    mock_sdk.WorkspaceClient.return_value = MagicMock()

    connector = _make_connector(mod, mock_sdk=mock_sdk)

    assert connector.available is True


def test_available_false_without_sdk():
    """available should be False when SDK is not installed."""
    mod = _reset_module()
    connector = _make_connector(mod, mock_sdk=None)

    assert connector.available is False


def test_available_false_client_creation_fails():
    """available should be False when WorkspaceClient constructor throws."""
    mod = _reset_module()
    mock_sdk = MagicMock()
    mock_sdk.WorkspaceClient.side_effect = RuntimeError("bad credentials")

    connector = _make_connector(mod, mock_sdk=mock_sdk)

    assert connector.available is False
