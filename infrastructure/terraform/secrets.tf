resource "google_secret_manager_secret" "admin_api_key" {
  secret_id = "dialectica-admin-api-key"

  replication {
    auto {}
  }

  labels = {
    app = "dialectica"
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "admin_api_key" {
  secret      = google_secret_manager_secret.admin_api_key.id
  secret_data = var.admin_api_key
}

resource "google_secret_manager_secret_iam_member" "api_access" {
  secret_id = google_secret_manager_secret.admin_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.api.email}"
}
