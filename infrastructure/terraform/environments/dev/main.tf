terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google      = { source = "hashicorp/google", version = "~> 5.0" }
    google-beta = { source = "hashicorp/google-beta", version = "~> 5.0" }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

variable "project_id" { type = string }
variable "region" { type = string default = "us-east1" }
variable "admin_api_key" { type = string sensitive = true default = "dev-admin-key" }

locals {
  environment = "dev"
  labels = {
    app         = "dialectica"
    environment = "dev"
    managed_by  = "terraform"
  }
}

module "networking" {
  source      = "../../modules/networking"
  project_id  = var.project_id
  region      = var.region
  environment = local.environment
}

module "iam" {
  source      = "../../modules/iam"
  project_id  = var.project_id
  environment = local.environment
}

module "pubsub" {
  source     = "../../modules/pubsub"
  project_id = var.project_id
  labels     = local.labels
}

module "secrets" {
  source        = "../../modules/secret-manager"
  project_id    = var.project_id
  environment   = local.environment
  admin_api_key = var.admin_api_key
}

# Dev uses smallest instance types — no GKE cluster, Cloud Run only
module "api" {
  source         = "../../modules/cloud-run-service"
  project_id     = var.project_id
  region         = var.region
  service_name   = "dialectica-api-dev"
  image          = "${var.region}-docker.pkg.dev/${var.project_id}/dialectica/api:latest"
  cpu            = "1"
  memory         = "1Gi"
  min_instances  = 0
  max_instances  = 2
  service_account = module.iam.api_sa_email
  labels         = local.labels
  env_vars = {
    ENVIRONMENT    = "development"
    GRAPH_BACKEND  = "falkordb"
    LOG_LEVEL      = "DEBUG"
    GCP_PROJECT_ID = var.project_id
  }
}

module "extraction_worker" {
  source         = "../../modules/cloud-run-service"
  project_id     = var.project_id
  region         = var.region
  service_name   = "dialectica-extraction-dev"
  image          = "${var.region}-docker.pkg.dev/${var.project_id}/dialectica/extraction-worker:latest"
  cpu            = "2"
  memory         = "4Gi"
  min_instances  = 0
  max_instances  = 2
  service_account = module.iam.extraction_sa_email
  labels         = local.labels
  allow_unauthenticated = false
  env_vars = {
    ENVIRONMENT    = "development"
    GCP_PROJECT_ID = var.project_id
  }
}
