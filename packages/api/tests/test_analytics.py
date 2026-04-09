"""
Tests for BigQuery AnalyticsClient.

Mocks google.cloud.bigquery to verify row structure, table routing,
and graceful degradation when the SDK is unavailable.
"""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fresh_client(**kwargs):
    """Import and return a fresh AnalyticsClient, resetting module-level state."""
    import dialectica_api.analytics as mod

    # Reset lazy-import state so each test controls the import
    mod._bigquery_mod = None
    mod._bigquery_import_attempted = False

    return mod.AnalyticsClient(**kwargs)


# ---------------------------------------------------------------------------
# Tests — happy path (BigQuery available)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_log_extraction_inserts_correct_row():
    """log_extraction should call insert_rows_json with the extraction_events table."""
    mock_bq_module = MagicMock()
    mock_client_instance = MagicMock()
    mock_client_instance.insert_rows_json.return_value = []
    mock_bq_module.Client.return_value = mock_client_instance

    mock_modules = {
        "google.cloud.bigquery": mock_bq_module,
        "google.cloud": MagicMock(),
        "google": MagicMock(),
    }
    with patch.dict("sys.modules", mock_modules):
        client = _fresh_client(project_id="test-project")
        # Force the lazy import to pick up our mock
        import dialectica_api.analytics as mod

        mod._bigquery_mod = mock_bq_module
        mod._bigquery_import_attempted = True

        ts = datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC)
        await client.log_extraction(
            workspace_id="ws-1",
            tenant_id="t-1",
            nodes_extracted=10,
            edges_extracted=5,
            processing_time_ms=1234.5,
            tier="standard",
            errors=0,
            timestamp=ts,
        )

    mock_client_instance.insert_rows_json.assert_called_once()
    call_args = mock_client_instance.insert_rows_json.call_args
    table_ref = call_args[0][0]
    rows = call_args[0][1]

    assert "extraction_events" in table_ref
    assert len(rows) == 1
    row = rows[0]
    assert row["workspace_id"] == "ws-1"
    assert row["tenant_id"] == "t-1"
    assert row["nodes_extracted"] == 10
    assert row["edges_extracted"] == 5
    assert row["processing_time_ms"] == 1234.5
    assert row["tier"] == "standard"
    assert row["errors"] == 0


@pytest.mark.asyncio
async def test_log_query_inserts_correct_row():
    """log_query should call insert_rows_json with the query_events table."""
    mock_bq_module = MagicMock()
    mock_client_instance = MagicMock()
    mock_client_instance.insert_rows_json.return_value = []
    mock_bq_module.Client.return_value = mock_client_instance

    mock_modules = {
        "google.cloud.bigquery": mock_bq_module,
        "google.cloud": MagicMock(),
        "google": MagicMock(),
    }
    with patch.dict("sys.modules", mock_modules):
        client = _fresh_client(project_id="test-project")
        import dialectica_api.analytics as mod

        mod._bigquery_mod = mock_bq_module
        mod._bigquery_import_attempted = True

        await client.log_query(
            workspace_id="ws-2",
            query_text="Who are the main actors?",
            mode="hybrid",
            response_time_ms=456.7,
            nodes_retrieved=8,
            confidence=0.85,
        )

    call_args = mock_client_instance.insert_rows_json.call_args
    table_ref = call_args[0][0]
    rows = call_args[0][1]

    assert "query_events" in table_ref
    assert len(rows) == 1
    row = rows[0]
    assert row["workspace_id"] == "ws-2"
    assert row["query_text"] == "Who are the main actors?"
    assert row["mode"] == "hybrid"
    assert row["confidence"] == 0.85


@pytest.mark.asyncio
async def test_log_benchmark_inserts_correct_row():
    """log_benchmark should call insert_rows_json with the benchmark_results table."""
    mock_bq_module = MagicMock()
    mock_client_instance = MagicMock()
    mock_client_instance.insert_rows_json.return_value = []
    mock_bq_module.Client.return_value = mock_client_instance

    mock_modules = {
        "google.cloud.bigquery": mock_bq_module,
        "google.cloud": MagicMock(),
        "google": MagicMock(),
    }
    with patch.dict("sys.modules", mock_modules):
        client = _fresh_client(project_id="test-project")
        import dialectica_api.analytics as mod

        mod._bigquery_mod = mock_bq_module
        mod._bigquery_import_attempted = True

        await client.log_benchmark(
            benchmark_id="bench-001",
            corpus_id="jcpoa-v2",
            tier="deep",
            model="gemini-2.5-flash-001",
            f1=0.87,
            precision=0.90,
            recall=0.84,
            extraction_time_ms=5432.1,
            hallucination_rate=0.03,
        )

    call_args = mock_client_instance.insert_rows_json.call_args
    table_ref = call_args[0][0]
    rows = call_args[0][1]

    assert "benchmark_results" in table_ref
    assert len(rows) == 1
    row = rows[0]
    assert row["benchmark_id"] == "bench-001"
    assert row["f1"] == 0.87
    assert row["hallucination_rate"] == 0.03


# ---------------------------------------------------------------------------
# Tests — graceful degradation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_log_extraction_no_crash_without_bigquery():
    """When google-cloud-bigquery is missing, log_extraction should not raise."""
    client = _fresh_client(project_id="test-project")
    import dialectica_api.analytics as mod

    mod._bigquery_mod = None
    mod._bigquery_import_attempted = True

    # Should complete without error
    await client.log_extraction(
        workspace_id="ws-x",
        tenant_id="t-x",
        nodes_extracted=1,
        edges_extracted=0,
        processing_time_ms=100.0,
        tier="quick",
    )


@pytest.mark.asyncio
async def test_log_query_no_crash_without_bigquery():
    """When google-cloud-bigquery is missing, log_query should not raise."""
    client = _fresh_client(project_id="test-project")
    import dialectica_api.analytics as mod

    mod._bigquery_mod = None
    mod._bigquery_import_attempted = True

    await client.log_query(
        workspace_id="ws-x",
        query_text="test",
        mode="local",
        response_time_ms=50.0,
        nodes_retrieved=0,
    )


@pytest.mark.asyncio
async def test_log_benchmark_no_crash_without_bigquery():
    """When google-cloud-bigquery is missing, log_benchmark should not raise."""
    client = _fresh_client(project_id="test-project")
    import dialectica_api.analytics as mod

    mod._bigquery_mod = None
    mod._bigquery_import_attempted = True

    await client.log_benchmark(
        benchmark_id="b-1",
        corpus_id="c-1",
        tier="quick",
        model="test-model",
        f1=0.5,
        precision=0.5,
        recall=0.5,
        extraction_time_ms=100.0,
        hallucination_rate=0.0,
    )


# ---------------------------------------------------------------------------
# Tests — error handling
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_insert_errors_logged_not_raised():
    """BigQuery insert errors should be logged, not raised as exceptions."""
    mock_bq_module = MagicMock()
    mock_client_instance = MagicMock()
    # Simulate BigQuery returning insertion errors
    mock_client_instance.insert_rows_json.return_value = [{"index": 0, "errors": ["bad row"]}]
    mock_bq_module.Client.return_value = mock_client_instance

    client = _fresh_client(project_id="test-project")
    import dialectica_api.analytics as mod

    mod._bigquery_mod = mock_bq_module
    mod._bigquery_import_attempted = True

    # Should not raise
    await client.log_extraction(
        workspace_id="ws-err",
        tenant_id="t-err",
        nodes_extracted=0,
        edges_extracted=0,
        processing_time_ms=0.0,
        tier="quick",
    )


@pytest.mark.asyncio
async def test_client_creation_failure_handled():
    """If BigQuery Client() constructor throws, we degrade gracefully."""
    mock_bq_module = MagicMock()
    mock_bq_module.Client.side_effect = RuntimeError("no credentials")

    client = _fresh_client(project_id="test-project")
    import dialectica_api.analytics as mod

    mod._bigquery_mod = mock_bq_module
    mod._bigquery_import_attempted = True

    # Should not raise
    await client.log_extraction(
        workspace_id="ws-fail",
        tenant_id="t-fail",
        nodes_extracted=0,
        edges_extracted=0,
        processing_time_ms=0.0,
        tier="quick",
    )


def test_default_dataset_id():
    """Default dataset should be dialectica_analytics."""
    client = _fresh_client()
    assert client._dataset_id == "dialectica_analytics"


def test_custom_dataset_id():
    """Custom dataset ID should be respected."""
    client = _fresh_client(dataset_id="custom_analytics")
    assert client._dataset_id == "custom_analytics"
