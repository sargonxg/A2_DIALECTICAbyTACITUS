variable "project_id" { type = string }
variable "region" { type = string }
variable "environment" { type = string }
variable "network_id" { type = string }
variable "subnet_id" { type = string }
variable "labels" { type = map(string) default = {} }
variable "default_pool_machine_type" { type = string default = "e2-standard-4" }
variable "default_pool_count" { type = number default = 3 }
variable "gpu_pool_machine_type" { type = string default = "g2-standard-4" }
variable "gpu_pool_count" { type = number default = 0 }

resource "google_container_cluster" "dialectica" {
  name     = "dialectica-${var.environment}"
  location = var.region
  project  = var.project_id

  networking_mode = "VPC_NATIVE"
  network         = var.network_id
  subnetwork      = var.subnet_id

  # Enable Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Private cluster
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  # Remove default node pool, we manage our own
  remove_default_node_pool = true
  initial_node_count       = 1

  resource_labels = var.labels

  release_channel {
    channel = "REGULAR"
  }

  addons_config {
    gce_persistent_disk_csi_driver_config { enabled = true }
    network_policy_config { disabled = false }
  }
}

resource "google_container_node_pool" "default" {
  name     = "default-pool"
  location = var.region
  cluster  = google_container_cluster.dialectica.name
  project  = var.project_id

  node_count = var.default_pool_count

  node_config {
    machine_type = var.default_pool_machine_type
    disk_size_gb = 100
    disk_type    = "pd-standard"

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    labels = merge(var.labels, { pool = "default" })
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

resource "google_container_node_pool" "gpu" {
  count    = var.gpu_pool_count > 0 ? 1 : 0
  name     = "gpu-pool"
  location = var.region
  cluster  = google_container_cluster.dialectica.name
  project  = var.project_id

  node_count = var.gpu_pool_count

  node_config {
    machine_type = var.gpu_pool_machine_type
    disk_size_gb = 200
    disk_type    = "pd-ssd"

    guest_accelerator {
      type  = "nvidia-l4"
      count = 1
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    labels = merge(var.labels, { pool = "gpu" })
    taint {
      key    = "nvidia.com/gpu"
      value  = "present"
      effect = "NO_SCHEDULE"
    }
  }
}

output "cluster_name" { value = google_container_cluster.dialectica.name }
output "cluster_endpoint" { value = google_container_cluster.dialectica.endpoint }
