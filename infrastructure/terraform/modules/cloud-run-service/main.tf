variable "project_id" { type = string }
variable "region" { type = string }
variable "service_name" { type = string }
variable "image" { type = string }
variable "port" { type = number default = 8080 }
variable "cpu" { type = string default = "2" }
variable "memory" { type = string default = "2Gi" }
variable "min_instances" { type = number default = 1 }
variable "max_instances" { type = number default = 10 }
variable "env_vars" { type = map(string) default = {} }
variable "service_account" { type = string default = "" }
variable "labels" { type = map(string) default = {} }
variable "vpc_connector" { type = string default = "" }
variable "allow_unauthenticated" { type = bool default = true }

resource "google_cloud_run_v2_service" "service" {
  name     = var.service_name
  location = var.region
  project  = var.project_id

  template {
    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    containers {
      image = var.image

      ports {
        container_port = var.port
      }

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
      }

      dynamic "env" {
        for_each = var.env_vars
        content {
          name  = env.key
          value = env.value
        }
      }

      startup_probe {
        http_get {
          path = "/health"
          port = var.port
        }
        initial_delay_seconds = 10
        period_seconds        = 10
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = var.port
        }
        period_seconds = 30
      }
    }

    service_account = var.service_account != "" ? var.service_account : null

    labels = var.labels
  }

  labels = var.labels
}

resource "google_cloud_run_v2_service_iam_member" "noauth" {
  count    = var.allow_unauthenticated ? 1 : 0
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "service_url" { value = google_cloud_run_v2_service.service.uri }
output "service_name" { value = google_cloud_run_v2_service.service.name }
