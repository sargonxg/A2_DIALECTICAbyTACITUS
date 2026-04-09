# ─── Neo4j Aura — Production Configuration ──────────────────────────────────
# Neo4j Aura is a fully managed service (TACITUS is in the Neo4j Startup
# Program). The instance itself is NOT Terraform-managed — it is provisioned
# through the Neo4j Aura Console at https://console.neo4j.io.
#
# This file manages:
# 1. Secret Manager secrets for Neo4j credentials
# 2. IAM bindings so the API service account can read the secrets
# 3. Cloud Run env var references (added to cloud_run.tf)

# ─── Neo4j Secrets ──────────────────────────────────────────────────────────

variable "neo4j_uri" {
  description = "Neo4j Aura connection URI (bolt+s://...)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "neo4j_user" {
  description = "Neo4j Aura username"
  type        = string
  sensitive   = true
  default     = "neo4j"
}

variable "neo4j_password" {
  description = "Neo4j Aura password"
  type        = string
  sensitive   = true
  default     = ""
}

locals {
  neo4j_configured = var.neo4j_uri != ""
}

resource "google_secret_manager_secret" "neo4j_uri" {
  count = local.neo4j_configured ? 1 : 0

  project   = var.project_id
  secret_id = "dialectica-neo4j-uri"

  labels = local.labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "neo4j_uri" {
  count = local.neo4j_configured ? 1 : 0

  secret      = google_secret_manager_secret.neo4j_uri[0].id
  secret_data = var.neo4j_uri
}

resource "google_secret_manager_secret" "neo4j_user" {
  count = local.neo4j_configured ? 1 : 0

  project   = var.project_id
  secret_id = "dialectica-neo4j-user"

  labels = local.labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "neo4j_user" {
  count = local.neo4j_configured ? 1 : 0

  secret      = google_secret_manager_secret.neo4j_user[0].id
  secret_data = var.neo4j_user
}

resource "google_secret_manager_secret" "neo4j_password" {
  count = local.neo4j_configured ? 1 : 0

  project   = var.project_id
  secret_id = "dialectica-neo4j-password"

  labels = local.labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "neo4j_password" {
  count = local.neo4j_configured ? 1 : 0

  secret      = google_secret_manager_secret.neo4j_password[0].id
  secret_data = var.neo4j_password
}
