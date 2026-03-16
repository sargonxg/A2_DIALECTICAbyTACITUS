variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-east1"
}

variable "spanner_instance_id" {
  description = "Cloud Spanner instance ID"
  type        = string
  default     = "dialectica-graph"
}

variable "spanner_database_id" {
  description = "Cloud Spanner database ID"
  type        = string
  default     = "dialectica"
}

variable "spanner_processing_units" {
  description = "Spanner processing units (100 = minimum)"
  type        = number
  default     = 100
}

variable "api_image" {
  description = "Docker image for the API service"
  type        = string
  default     = ""
}

variable "web_image" {
  description = "Docker image for the web service"
  type        = string
  default     = ""
}

variable "admin_api_key" {
  description = "Initial admin API key"
  type        = string
  sensitive   = true
}

variable "cors_origins" {
  description = "Allowed CORS origins"
  type        = string
  default     = "https://app.dialectica.tacitus.ai"
}
