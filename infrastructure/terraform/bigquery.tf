# ─── BigQuery Analytics ──────────────────────────────────────────────────────
# Stores extraction events, query events, and benchmark results for
# operational analytics and model quality tracking.

resource "google_bigquery_dataset" "analytics" {
  project    = var.project_id
  dataset_id = "dialectica_analytics"
  location   = var.region

  friendly_name = "DIALECTICA Analytics"
  description   = "Operational analytics for extraction pipeline, queries, and benchmarks"

  labels = local.labels

  default_table_expiration_ms = null # keep data indefinitely

  depends_on = [google_project_service.required_apis]
}

resource "google_bigquery_table" "extraction_events" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "extraction_events"

  description = "Per-extraction event log: node/edge counts, latency, errors"

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  schema = file("${path.module}/schemas/extraction_events.json")

  labels = local.labels
}

resource "google_bigquery_table" "query_events" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "query_events"

  description = "Per-query event log: response time, nodes retrieved, confidence"

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  schema = file("${path.module}/schemas/query_events.json")

  labels = local.labels
}

resource "google_bigquery_table" "benchmark_results" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "benchmark_results"

  description = "Extraction benchmark results: F1, precision, recall, hallucination rate"

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  schema = file("${path.module}/schemas/benchmark_results.json")

  labels = local.labels
}
