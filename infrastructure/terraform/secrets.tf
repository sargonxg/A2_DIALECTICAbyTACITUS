# ─── Secret Manager ──────────────────────────────────────────────────────────

resource "google_secret_manager_secret" "admin_api_key" {
  project   = var.project_id
  secret_id = "dialectica-admin-api-key"

  labels = local.labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "admin_api_key" {
  secret      = google_secret_manager_secret.admin_api_key.id
  secret_data = var.admin_api_key
}
