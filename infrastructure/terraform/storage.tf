resource "google_storage_bucket" "documents" {
  name     = "${var.project_id}-dialectica-documents"
  location = var.region

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 365
    }
  }

  labels = {
    app = "dialectica"
  }

  depends_on = [google_project_service.apis]
}
