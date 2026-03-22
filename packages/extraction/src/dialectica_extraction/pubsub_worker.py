"""
Pub/Sub Extraction Worker — Async event-driven ingestion pipeline.

Subscribes to dialectica-extraction-requests topic, runs the LangGraph
extraction pipeline, and publishes results to dialectica-graph-updates.
Failed messages (after 3 retries) go to dialectica-extraction-dlq.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

SUBSCRIPTION = os.getenv("PUBSUB_EXTRACTION_SUBSCRIPTION", "dialectica-extraction-requests-sub")
GRAPH_UPDATES_TOPIC = os.getenv("PUBSUB_GRAPH_UPDATES_TOPIC", "dialectica-graph-updates")
DLQ_TOPIC = os.getenv("PUBSUB_DLQ_TOPIC", "dialectica-extraction-dlq")
MAX_RETRIES = 3


class ExtractionMessage:
    """Parsed Pub/Sub extraction request message."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.document_id: str = data.get("document_id", "")
        self.tenant_id: str = data.get("tenant_id", "")
        self.workspace_id: str = data.get("workspace_id", "")
        self.gcs_uri: str = data.get("gcs_uri", "")
        self.tier: str = data.get("tier", "standard")
        self.priority: int = data.get("priority", 0)
        self.retry_count: int = data.get("retry_count", 0)

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "tenant_id": self.tenant_id,
            "workspace_id": self.workspace_id,
            "gcs_uri": self.gcs_uri,
            "tier": self.tier,
            "priority": self.priority,
            "retry_count": self.retry_count,
        }


class PubSubExtractionWorker:
    """Pub/Sub subscriber that runs extraction pipeline on incoming messages.

    Args:
        project_id: GCP project ID.
        graph_client: Graph database client for writing results.
    """

    def __init__(
        self,
        project_id: str | None = None,
        graph_client: Any = None,
    ) -> None:
        self._project_id = project_id or os.getenv("GCP_PROJECT_ID", "")
        self._graph_client = graph_client
        self._subscriber: Any = None
        self._publisher: Any = None

    def _get_subscriber(self) -> Any:
        if self._subscriber is None:
            from google.cloud import pubsub_v1

            self._subscriber = pubsub_v1.SubscriberClient()
        return self._subscriber

    def _get_publisher(self) -> Any:
        if self._publisher is None:
            from google.cloud import pubsub_v1

            self._publisher = pubsub_v1.PublisherClient()
        return self._publisher

    def _publish(self, topic: str, data: dict[str, Any]) -> None:
        """Publish a message to a Pub/Sub topic."""
        publisher = self._get_publisher()
        topic_path = publisher.topic_path(self._project_id, topic)
        message_bytes = json.dumps(data).encode("utf-8")
        publisher.publish(topic_path, message_bytes)

    async def process_message(self, message_data: bytes) -> dict[str, Any]:
        """Process a single extraction request message.

        Args:
            message_data: Raw Pub/Sub message bytes.

        Returns:
            Result dict with status and extracted counts.
        """
        data = json.loads(message_data.decode("utf-8"))
        msg = ExtractionMessage(data)

        logger.info(
            "Processing extraction: doc=%s ws=%s tier=%s retry=%d",
            msg.document_id,
            msg.workspace_id,
            msg.tier,
            msg.retry_count,
        )

        try:
            # Load document text
            text = await self._load_document(msg.gcs_uri)
            if not text:
                raise ValueError(f"Empty document: {msg.gcs_uri}")

            # Run extraction pipeline
            from dialectica_extraction.pipeline import ExtractionPipeline
            from dialectica_ontology.tiers import OntologyTier

            pipeline = ExtractionPipeline()
            tier = OntologyTier(msg.tier)
            result = pipeline.run(
                text=text,
                tier=tier,
                workspace_id=msg.workspace_id,
                tenant_id=msg.tenant_id,
            )

            stats = result.get("ingestion_stats", {})

            # Publish success to graph-updates topic
            self._publish(
                GRAPH_UPDATES_TOPIC,
                {
                    "document_id": msg.document_id,
                    "workspace_id": msg.workspace_id,
                    "tenant_id": msg.tenant_id,
                    "status": "complete",
                    "nodes_extracted": stats.get("nodes_written", 0),
                    "edges_extracted": stats.get("edges_written", 0),
                },
            )

            logger.info(
                "Extraction complete: doc=%s nodes=%d edges=%d",
                msg.document_id,
                stats.get("nodes_written", 0),
                stats.get("edges_written", 0),
            )
            return {"status": "complete", **stats}

        except Exception as e:
            logger.error("Extraction failed: doc=%s error=%s", msg.document_id, e)

            if msg.retry_count < MAX_RETRIES:
                # Re-publish with incremented retry count
                msg.retry_count += 1
                self._publish(
                    SUBSCRIPTION.replace("-sub", ""),
                    msg.to_dict(),
                )
                return {"status": "retrying", "retry_count": msg.retry_count}
            else:
                # Send to DLQ
                self._publish(
                    DLQ_TOPIC,
                    {
                        **msg.to_dict(),
                        "error": str(e)[:500],
                        "status": "failed",
                    },
                )
                return {"status": "failed", "error": str(e)[:200]}

    async def _load_document(self, gcs_uri: str) -> str:
        """Load document from GCS and extract text."""
        from dialectica_extraction.gcs_loader import load_document_from_gcs

        return await load_document_from_gcs(gcs_uri)

    def start_pull(self) -> None:
        """Start pulling messages from the subscription (blocking)."""
        subscriber = self._get_subscriber()
        sub_path = subscriber.subscription_path(self._project_id, SUBSCRIPTION)

        def callback(message: Any) -> None:
            import asyncio

            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.process_message(message.data))
                message.ack()
            except Exception as e:
                logger.error("Message processing failed: %s", e)
                message.nack()

        future = subscriber.subscribe(sub_path, callback=callback)
        logger.info("Listening on %s", sub_path)

        try:
            future.result()
        except KeyboardInterrupt:
            future.cancel()
