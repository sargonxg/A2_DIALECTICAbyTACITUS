# ─── DIALECTICA Terraform — Root Configuration ───────────────────────────────
# Google Cloud Platform deployment for DIALECTICA conflict intelligence platform.
# Deploys: Cloud Run (API + Web), Cloud Spanner, Secret Manager, Cloud Storage,
#          Pub/Sub, Artifact Registry, Cloud Monitoring.

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }

  # Uncomment to use GCS backend for team collaboration:
  # backend "gcs" {
  #   bucket = "dialectica-terraform-state"
  #   prefix = "terraform/state"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# ─── Enable Required APIs ─────────────────────────────────────────────────────

resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "spanner.googleapis.com",
    "secretmanager.googleapis.com",
    "storage.googleapis.com",
    "pubsub.googleapis.com",
    "artifactregistry.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "aiplatform.googleapis.com",
    "iam.googleapis.com",
  ])

  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

# ─── Artifact Registry ────────────────────────────────────────────────────────

resource "google_artifact_registry_repository" "dialectica" {
  provider      = google-beta
  location      = var.region
  repository_id = "dialectica"
  description   = "DIALECTICA Docker images"
  format        = "DOCKER"

  depends_on = [google_project_service.required_apis]
}
