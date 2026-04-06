# ─── Outputs ─────────────────────────────────────────────────────────────────

output "api_url" {
  description = "DIALECTICA API Cloud Run URL"
  value       = google_cloud_run_v2_service.api.uri
}

output "web_url" {
  description = "DIALECTICA Web Cloud Run URL"
  value       = google_cloud_run_v2_service.web.uri
}

output "spanner_instance" {
  description = "Cloud Spanner instance name"
  value       = google_spanner_instance.dialectica.name
}

output "spanner_database" {
  description = "Cloud Spanner database name"
  value       = google_spanner_database.dialectica.name
}

output "artifact_registry" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/dialectica"
}

output "documents_bucket" {
  description = "GCS bucket for document uploads"
  value       = google_storage_bucket.documents.name
}

output "api_service_account" {
  description = "API service account email"
  value       = google_service_account.api_sa.email
}

output "bigquery_dataset" {
  description = "BigQuery analytics dataset ID"
  value       = google_bigquery_dataset.analytics.dataset_id
}

output "databricks_service_account" {
  description = "Databricks service account email (empty if not enabled)"
  value       = local.databricks_enabled ? google_service_account.databricks_sa[0].email : ""
}
