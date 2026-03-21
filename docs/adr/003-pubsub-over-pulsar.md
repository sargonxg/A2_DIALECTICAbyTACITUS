# ADR-003: Google Cloud Pub/Sub Over Apache Pulsar

**Status:** Accepted
**Date:** 2025-02-01

## Context
DIALECTICA needs async message passing for extraction jobs, graph sync events, and DLQ. Options: Google Cloud Pub/Sub (managed), Apache Pulsar (self-hosted), Apache Kafka (self-hosted).

## Decision
Use Google Cloud Pub/Sub for its zero-ops managed service, native GCP IAM integration, and dead-letter queue support. At current scale (<1000 msgs/sec), Pub/Sub is cost-effective and simple.

## Consequences
- **Positive:** Zero operational burden; native IAM; DLQ built-in; auto-scaling
- **Negative:** GCP lock-in; higher per-message cost than self-hosted at scale; no exactly-once semantics
- **Migration path:** If throughput exceeds 10K msgs/sec or multi-cloud needed, migrate to Apache Pulsar with Bookkeeper
