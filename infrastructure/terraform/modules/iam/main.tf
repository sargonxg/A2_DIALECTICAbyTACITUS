variable "project_id" { type = string }
variable "environment" { type = string }

resource "google_service_account" "api" {
  account_id   = "dialectica-api-${var.environment}"
  display_name = "DIALECTICA API (${var.environment})"
  project      = var.project_id
}

resource "google_service_account" "extraction" {
  account_id   = "dialectica-extract-${var.environment}"
  display_name = "DIALECTICA Extraction Worker (${var.environment})"
  project      = var.project_id
}

resource "google_service_account" "mcp" {
  account_id   = "dialectica-mcp-${var.environment}"
  display_name = "DIALECTICA MCP Server (${var.environment})"
  project      = var.project_id
}

locals {
  api_roles = [
    "roles/spanner.databaseUser",
    "roles/secretmanager.secretAccessor",
    "roles/aiplatform.user",
    "roles/pubsub.publisher",
    "roles/storage.objectAdmin",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
  ]
  extraction_roles = [
    "roles/aiplatform.user",
    "roles/pubsub.subscriber",
    "roles/pubsub.publisher",
    "roles/storage.objectViewer",
    "roles/logging.logWriter",
  ]
}

resource "google_project_iam_member" "api_roles" {
  for_each = toset(local.api_roles)
  project  = var.project_id
  role     = each.key
  member   = "serviceAccount:${google_service_account.api.email}"
}

resource "google_project_iam_member" "extraction_roles" {
  for_each = toset(local.extraction_roles)
  project  = var.project_id
  role     = each.key
  member   = "serviceAccount:${google_service_account.extraction.email}"
}

# Workload Identity bindings
resource "google_service_account_iam_member" "api_wi" {
  service_account_id = google_service_account.api.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[dialectica/api]"
}

resource "google_service_account_iam_member" "extraction_wi" {
  service_account_id = google_service_account.extraction.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[dialectica/extraction-worker]"
}

output "api_sa_email" { value = google_service_account.api.email }
output "extraction_sa_email" { value = google_service_account.extraction.email }
output "mcp_sa_email" { value = google_service_account.mcp.email }
