resource "google_pubsub_topic" "extraction_requests" {
  name = "dialectica-extraction-requests"

  message_retention_duration = "86400s"

  labels = {
    app = "dialectica"
  }

  depends_on = [google_project_service.apis]
}

resource "google_pubsub_subscription" "extraction_worker" {
  name  = "dialectica-extraction-worker"
  topic = google_pubsub_topic.extraction_requests.id

  ack_deadline_seconds       = 600
  message_retention_duration = "604800s"

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.extraction_dlq.id
    max_delivery_attempts = 5
  }
}

resource "google_pubsub_topic" "extraction_dlq" {
  name = "dialectica-extraction-dlq"

  labels = {
    app = "dialectica"
  }
}
