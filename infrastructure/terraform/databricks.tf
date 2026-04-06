# ─── Databricks Prerequisites ────────────────────────────────────────────────
# Creates GCP service account and IAM bindings needed by Databricks.
# The actual Databricks workspace provisioning requires the separate
# databricks/databricks Terraform provider and is managed outside this
# configuration (see https://registry.terraform.io/providers/databricks/databricks).
#
# Set var.databricks_account_id to a non-empty string to enable these resources.

variable "databricks_account_id" {
  description = "Databricks account ID. Leave empty to skip Databricks resource creation."
  type        = string
  default     = ""
}

locals {
  databricks_enabled = var.databricks_account_id != ""
}

resource "google_service_account" "databricks_sa" {
  count = local.databricks_enabled ? 1 : 0

  project      = var.project_id
  account_id   = "dialectica-databricks"
  display_name = "DIALECTICA Databricks Service Account"
  description  = "Service account used by Databricks for BigQuery and GCS access"
}

resource "google_project_iam_member" "databricks_bq_editor" {
  count = local.databricks_enabled ? 1 : 0

  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.databricks_sa[0].email}"
}

resource "google_project_iam_member" "databricks_storage_admin" {
  count = local.databricks_enabled ? 1 : 0

  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.databricks_sa[0].email}"
}
