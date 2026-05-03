# ─── DIALECTICA Terraform Variables ──────────────────────────────────────────

variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "region" {
  description = "Primary GCP region for deployment"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment: dev, staging, prod"
  type        = string
  default     = "prod"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "api_min_instances" {
  description = "Minimum Cloud Run instances for API"
  type        = number
  default     = 0
}

variable "api_max_instances" {
  description = "Maximum Cloud Run instances for API"
  type        = number
  default     = 1
}

variable "web_min_instances" {
  description = "Minimum Cloud Run instances for Web"
  type        = number
  default     = 0
}

variable "web_max_instances" {
  description = "Maximum Cloud Run instances for Web"
  type        = number
  default     = 1
}

variable "spanner_processing_units" {
  description = "Spanner processing units (100 = 0.1 node, minimum billable)"
  type        = number
  default     = 100
}

variable "admin_api_key" {
  description = "Admin API key for DIALECTICA API (stored in Secret Manager)"
  type        = string
  sensitive   = true
}

variable "cors_origins" {
  description = "Allowed CORS origins for the API"
  type        = string
  default     = ""
}

variable "gemini_flash_model" {
  description = "Vertex AI Gemini Flash model ID"
  type        = string
  default     = "gemini-2.5-flash-001"
}

variable "gemini_pro_model" {
  description = "Vertex AI Gemini Pro model ID"
  type        = string
  default     = "gemini-2.5-pro-001"
}

variable "vertex_ai_location" {
  description = "Vertex AI location"
  type        = string
  default     = "us-east1"
}

locals {
  app_name = "dialectica"
  registry = "${var.region}-docker.pkg.dev/${var.project_id}/dialectica"
  labels = {
    app         = "dialectica"
    environment = var.environment
    managed_by  = "terraform"
  }
}
