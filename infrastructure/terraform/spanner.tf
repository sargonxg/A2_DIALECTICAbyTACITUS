# ─── Cloud Spanner ───────────────────────────────────────────────────────────

resource "google_spanner_instance" "dialectica" {
  project          = var.project_id
  name             = "dialectica-graph"
  display_name     = "DIALECTICA Graph Database"
  config           = "regional-${var.region}"
  processing_units = var.spanner_processing_units

  labels = local.labels

  depends_on = [google_project_service.required_apis]
}

resource "google_spanner_database" "dialectica" {
  project  = var.project_id
  instance = google_spanner_instance.dialectica.name
  name     = "dialectica"

  deletion_protection = var.environment == "prod" ? true : false

  depends_on = [google_spanner_instance.dialectica]
}
