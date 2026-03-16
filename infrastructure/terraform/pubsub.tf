# ─── Pub/Sub ──────────────────────────────────────────────────────────────────

resource "google_pubsub_topic" "ingest_events" {
  project = var.project_id
  name    = "dialectica-ingest-events"
  labels  = local.labels

  depends_on = [google_project_service.required_apis]
}

resource "google_pubsub_topic" "extraction_jobs" {
  project = var.project_id
  name    = "dialectica-extraction-jobs"
  labels  = local.labels

  depends_on = [google_project_service.required_apis]
}

resource "google_pubsub_subscription" "extraction_jobs_sub" {
  project = var.project_id
  name    = "dialectica-extraction-jobs-sub"
  topic   = google_pubsub_topic.extraction_jobs.name

  ack_deadline_seconds = 600

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "300s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.ingest_events.id
    max_delivery_attempts = 5
  }

  labels = local.labels
}
