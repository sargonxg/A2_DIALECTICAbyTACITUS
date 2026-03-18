# ─── Cloud Run — API Service ──────────────────────────────────────────────────

resource "google_cloud_run_v2_service" "api" {
  project  = var.project_id
  name     = "dialectica-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  labels = local.labels

  template {
    service_account = google_service_account.api_sa.email

    scaling {
      min_instance_count = var.api_min_instances
      max_instance_count = var.api_max_instances
    }

    containers {
      image = "${local.registry}/api:${var.image_tag}"

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "SPANNER_INSTANCE_ID"
        value = google_spanner_instance.dialectica.name
      }
      env {
        name  = "SPANNER_DATABASE_ID"
        value = google_spanner_database.dialectica.name
      }
      env {
        name  = "VERTEX_AI_LOCATION"
        value = var.vertex_ai_location
      }
      env {
        name  = "GEMINI_FLASH_MODEL"
        value = var.gemini_flash_model
      }
      env {
        name  = "GEMINI_PRO_MODEL"
        value = var.gemini_pro_model
      }
      env {
        name  = "GRAPH_BACKEND"
        value = "spanner"
      }
      env {
        name  = "LOG_LEVEL"
        value = var.environment == "prod" ? "INFO" : "DEBUG"
      }
      env {
        name  = "CORS_ORIGINS"
        value = var.cors_origins != "" ? var.cors_origins : "*"
      }
      env {
        name = "ADMIN_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.admin_api_key.secret_id
            version = "latest"
          }
        }
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        initial_delay_seconds = 10
        timeout_seconds       = 5
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        initial_delay_seconds = 30
        timeout_seconds       = 5
        period_seconds        = 30
        failure_threshold     = 3
      }
    }
  }

  depends_on = [
    google_project_service.required_apis,
    google_spanner_database.dialectica,
    google_secret_manager_secret_version.admin_api_key,
    google_service_account.api_sa,
  ]
}

# ─── Cloud Run — Web Service ──────────────────────────────────────────────────

resource "google_cloud_run_v2_service" "web" {
  project  = var.project_id
  name     = "dialectica-web"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  labels = local.labels

  template {
    service_account = google_service_account.web_sa.email

    scaling {
      min_instance_count = var.web_min_instances
      max_instance_count = var.web_max_instances
    }

    containers {
      image = "${local.registry}/web:${var.image_tag}"

      ports {
        container_port = 3000
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
        cpu_idle = true
      }

      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = google_cloud_run_v2_service.api.uri
      }
      env {
        name  = "INTERNAL_API_URL"
        value = google_cloud_run_v2_service.api.uri
      }
      env {
        name  = "NODE_ENV"
        value = "production"
      }
    }
  }

  depends_on = [
    google_project_service.required_apis,
    google_service_account.web_sa,
  ]
}
