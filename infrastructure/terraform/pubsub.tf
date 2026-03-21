# ─── Pub/Sub Topics ──────────────────────────────────────────────────────────

resource "google_pubsub_topic" "extraction_requests" {
  project = var.project_id
  name    = "dialectica-extraction-requests"
  labels  = local.labels

  depends_on = [google_project_service.required_apis]
}

resource "google_pubsub_topic" "graph_updates" {
  project = var.project_id
  name    = "dialectica-graph-updates"
  labels  = local.labels

  depends_on = [google_project_service.required_apis]
}

resource "google_pubsub_topic" "extraction_dlq" {
  project = var.project_id
  name    = "dialectica-extraction-dlq"
  labels  = local.labels

  depends_on = [google_project_service.required_apis]
}

resource "google_pubsub_topic" "ingest_events" {
  project = var.project_id
  name    = "dialectica-ingest-events"
  labels  = local.labels

  depends_on = [google_project_service.required_apis]
}

# ─── Pub/Sub Subscriptions ───────────────────────────────────────────────────

resource "google_pubsub_subscription" "extraction_requests_sub" {
  project = var.project_id
  name    = "dialectica-extraction-requests-sub"
  topic   = google_pubsub_topic.extraction_requests.name

  ack_deadline_seconds = 600

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "300s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.extraction_dlq.id
    max_delivery_attempts = 5
  }

  labels = local.labels
}

resource "google_pubsub_subscription" "graph_updates_sub" {
  project = var.project_id
  name    = "dialectica-graph-updates-sub"
  topic   = google_pubsub_topic.graph_updates.name

  ack_deadline_seconds = 300

  retry_policy {
    minimum_backoff = "5s"
    maximum_backoff = "60s"
  }

  labels = local.labels
}

resource "google_pubsub_subscription" "extraction_dlq_sub" {
  project = var.project_id
  name    = "dialectica-extraction-dlq-sub"
  topic   = google_pubsub_topic.extraction_dlq.name

  ack_deadline_seconds = 300
  labels = local.labels
}
