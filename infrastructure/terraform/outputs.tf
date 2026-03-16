output "api_url" {
  description = "URL of the API Cloud Run service"
  value       = google_cloud_run_v2_service.api.uri
}

output "web_url" {
  description = "URL of the Web Cloud Run service"
  value       = google_cloud_run_v2_service.web.uri
}

output "spanner_instance" {
  description = "Spanner instance name"
  value       = google_spanner_instance.dialectica.name
}

output "documents_bucket" {
  description = "GCS bucket for documents"
  value       = google_storage_bucket.documents.name
}

output "registry_url" {
  description = "Artifact Registry URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/dialectica"
}
