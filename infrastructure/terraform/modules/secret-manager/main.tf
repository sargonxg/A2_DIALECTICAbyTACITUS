variable "project_id" { type = string }
variable "environment" { type = string }
variable "admin_api_key" { type = string sensitive = true }

resource "google_secret_manager_secret" "admin_api_key" {
  project   = var.project_id
  secret_id = "dialectica-admin-api-key-${var.environment}"
  replication { auto {} }
}

resource "google_secret_manager_secret_version" "admin_api_key" {
  secret      = google_secret_manager_secret.admin_api_key.id
  secret_data = var.admin_api_key
}

output "admin_key_secret_id" { value = google_secret_manager_secret.admin_api_key.secret_id }
