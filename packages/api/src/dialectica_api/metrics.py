"""
Custom Prometheus Metrics for DIALECTICA API.

Provides domain-specific metrics beyond the automatic HTTP instrumentation.
"""

from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

# ─── Extraction Metrics ──────────────────────────────────────────────────────

dialectica_extraction_duration_seconds = Histogram(
    "dialectica_extraction_duration_seconds",
    "Time spent performing document extraction (seconds).",
    labelnames=["tier", "status"],
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0),
)

dialectica_extraction_nodes_extracted = Counter(
    "dialectica_extraction_nodes_extracted",
    "Total number of graph nodes extracted from documents.",
    labelnames=["node_type", "tier"],
)

# ─── Reasoning Metrics ───────────────────────────────────────────────────────

dialectica_reasoning_query_duration_seconds = Histogram(
    "dialectica_reasoning_query_duration_seconds",
    "Time spent on reasoning / theory-generation queries (seconds).",
    labelnames=["query_type", "status"],
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
)

# ─── Graph Metrics ───────────────────────────────────────────────────────────

dialectica_graph_query_duration_seconds = Histogram(
    "dialectica_graph_query_duration_seconds",
    "Time spent executing graph database queries (seconds).",
    labelnames=["operation", "backend"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# ─── Quality Metrics ─────────────────────────────────────────────────────────

dialectica_hallucination_rate = Gauge(
    "dialectica_hallucination_rate",
    "Estimated hallucination rate from the latest validation cycle.",
    labelnames=["model", "tier"],
)
