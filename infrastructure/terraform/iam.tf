# ─── IAM — Service Accounts ──────────────────────────────────────────────────

resource "google_service_account" "api_sa" {
  project      = var.project_id
  account_id   = "dialectica-api"
  display_name = "DIALECTICA API Service Account"
  description  = "Service account for DIALECTICA API Cloud Run service"
}

resource "google_service_account" "web_sa" {
  project      = var.project_id
  account_id   = "dialectica-web"
  display_name = "DIALECTICA Web Service Account"
  description  = "Service account for DIALECTICA Web Cloud Run service"
}

# ─── API Service Account Bindings ────────────────────────────────────────────

resource "google_project_iam_member" "api_spanner_user" {
  project = var.project_id
  role    = "roles/spanner.databaseUser"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "api_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "api_vertex_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "api_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "api_storage_object_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "api_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "api_trace_agent" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

resource "google_project_iam_member" "api_bigquery_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

# ─── Cloud Run Public Access ─────────────────────────────────────────────────

data "google_iam_policy" "noauth" {
  binding {
    role = "roles/run.invoker"
    members = ["allUsers"]
  }
}

resource "google_cloud_run_v2_service_iam_policy" "api_noauth" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.api.name

  policy_data = data.google_iam_policy.noauth.policy_data
}

resource "google_cloud_run_v2_service_iam_policy" "web_noauth" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.web.name

  policy_data = data.google_iam_policy.noauth.policy_data
}
