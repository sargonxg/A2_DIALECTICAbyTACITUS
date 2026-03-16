resource "google_spanner_instance" "dialectica" {
  name             = var.spanner_instance_id
  config           = "regional-${var.region}"
  display_name     = "DIALECTICA Graph Database"
  processing_units = var.spanner_processing_units

  labels = {
    app = "dialectica"
    env = "production"
  }

  depends_on = [google_project_service.apis]
}

resource "google_spanner_database" "dialectica" {
  instance = google_spanner_instance.dialectica.name
  name     = var.spanner_database_id

  deletion_protection = true

  depends_on = [google_spanner_instance.dialectica]
}
