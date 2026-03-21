"""Tests for Pub/Sub extraction worker."""
from __future__ import annotations

import json
import sys
import os
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dialectica_extraction.pubsub_worker import (
    PubSubExtractionWorker,
    ExtractionMessage,
    MAX_RETRIES,
)
from dialectica_extraction.gcs_loader import extract_text, _parse_gcs_uri


class TestExtractionMessage:
    def test_parse_message(self):
        data = {
            "document_id": "doc-1",
            "tenant_id": "t-1",
            "workspace_id": "ws-1",
            "gcs_uri": "gs://bucket/file.pdf",
            "tier": "standard",
            "priority": 1,
        }
        msg = ExtractionMessage(data)
        assert msg.document_id == "doc-1"
        assert msg.tier == "standard"
        assert msg.retry_count == 0

    def test_to_dict(self):
        msg = ExtractionMessage({"document_id": "d1", "tier": "full"})
        d = msg.to_dict()
        assert d["document_id"] == "d1"
        assert d["tier"] == "full"
        assert "retry_count" in d

    def test_defaults(self):
        msg = ExtractionMessage({})
        assert msg.document_id == ""
        assert msg.tier == "standard"
        assert msg.priority == 0


class TestWorkerProcessMessage:
    @pytest.fixture
    def worker(self):
        w = PubSubExtractionWorker(project_id="test-project")
        w._publisher = MagicMock()
        return w

    @pytest.mark.asyncio
    async def test_process_empty_document_retries(self, worker):
        message_data = json.dumps({
            "document_id": "doc-1",
            "tenant_id": "t-1",
            "workspace_id": "ws-1",
            "gcs_uri": "gs://bucket/empty.txt",
            "tier": "essential",
            "retry_count": 0,
        }).encode("utf-8")

        # Mock the document loader to return empty
        with patch.object(worker, "_load_document", new_callable=AsyncMock, return_value=""):
            result = await worker.process_message(message_data)
        assert result["status"] == "retrying"
        assert result["retry_count"] == 1

    @pytest.mark.asyncio
    async def test_process_max_retries_sends_to_dlq(self, worker):
        message_data = json.dumps({
            "document_id": "doc-1",
            "tenant_id": "t-1",
            "workspace_id": "ws-1",
            "gcs_uri": "gs://bucket/bad.txt",
            "tier": "essential",
            "retry_count": MAX_RETRIES,
        }).encode("utf-8")

        with patch.object(worker, "_load_document", new_callable=AsyncMock, return_value=""):
            result = await worker.process_message(message_data)
        assert result["status"] == "failed"


class TestGCSLoader:
    def test_parse_gcs_uri(self):
        bucket, path = _parse_gcs_uri("gs://my-bucket/path/to/file.pdf")
        assert bucket == "my-bucket"
        assert path == "path/to/file.pdf"

    def test_parse_gcs_uri_no_prefix(self):
        bucket, path = _parse_gcs_uri("my-bucket/file.txt")
        assert bucket == "my-bucket"
        assert path == "file.txt"

    def test_extract_text_txt(self):
        content = b"Hello world"
        result = extract_text(content, "txt")
        assert result == "Hello world"

    def test_extract_text_md(self):
        content = b"# Title\n\nSome markdown"
        result = extract_text(content, "md")
        assert "Title" in result

    def test_extract_text_html(self):
        content = b"<html><body><p>Hello</p><script>evil()</script></body></html>"
        result = extract_text(content, "html")
        assert "Hello" in result
        assert "evil" not in result

    def test_extract_text_unknown_extension(self):
        content = b"some text"
        result = extract_text(content, "xyz")
        assert result == "some text"
