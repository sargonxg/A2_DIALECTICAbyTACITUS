resource "google_cloud_run_v2_service" "api" {
  name     = "dialectica-api"
  location = var.region

  template {
    service_account = google_service_account.api.email

    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }

    containers {
      image = var.api_image != "" ? var.api_image : "${var.region}-docker.pkg.dev/${var.project_id}/dialectica/api:latest"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "SPANNER_INSTANCE_ID"
        value = var.spanner_instance_id
      }
      env {
        name  = "SPANNER_DATABASE_ID"
        value = var.spanner_database_id
      }
      env {
        name  = "VERTEX_AI_LOCATION"
        value = var.region
      }
      env {
        name  = "CORS_ORIGINS"
        value = var.cors_origins
      }
      env {
        name = "ADMIN_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.admin_api_key.id
            version = "latest"
          }
        }
      }

      startup_probe {
        http_get {
          path = "/health"
        }
        initial_delay_seconds = 10
        period_seconds        = 5
        failure_threshold     = 5
      }

      liveness_probe {
        http_get {
          path = "/health"
        }
        period_seconds = 30
      }
    }
  }

  depends_on = [
    google_spanner_database.dialectica,
    google_secret_manager_secret_version.admin_api_key,
  ]
}

resource "google_cloud_run_v2_service" "web" {
  name     = "dialectica-web"
  location = var.region

  template {
    scaling {
      min_instance_count = 1
      max_instance_count = 5
    }

    containers {
      image = var.web_image != "" ? var.web_image : "${var.region}-docker.pkg.dev/${var.project_id}/dialectica/web:latest"

      ports {
        container_port = 3000
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = google_cloud_run_v2_service.api.uri
      }
    }
  }

  depends_on = [google_cloud_run_v2_service.api]
}

# Public access for web
resource "google_cloud_run_v2_service_iam_member" "web_public" {
  name     = google_cloud_run_v2_service.web.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Public access for API
resource "google_cloud_run_v2_service_iam_member" "api_public" {
  name     = google_cloud_run_v2_service.api.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}
