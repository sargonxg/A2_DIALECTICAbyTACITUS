variable "project_id" { type = string }
variable "labels" { type = map(string) default = {} }

resource "google_pubsub_topic" "extraction_requests" {
  project = var.project_id
  name    = "dialectica-extraction-requests"
  labels  = var.labels
}

resource "google_pubsub_topic" "graph_updates" {
  project = var.project_id
  name    = "dialectica-graph-updates"
  labels  = var.labels
}

resource "google_pubsub_topic" "extraction_dlq" {
  project = var.project_id
  name    = "dialectica-extraction-dlq"
  labels  = var.labels
}

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
  labels = var.labels
}

resource "google_pubsub_subscription" "graph_updates_sub" {
  project = var.project_id
  name    = "dialectica-graph-updates-sub"
  topic   = google_pubsub_topic.graph_updates.name
  ack_deadline_seconds = 300
  labels = var.labels
}

output "extraction_topic" { value = google_pubsub_topic.extraction_requests.name }
output "graph_updates_topic" { value = google_pubsub_topic.graph_updates.name }
output "dlq_topic" { value = google_pubsub_topic.extraction_dlq.name }
