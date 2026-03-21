variable "project_id" { type = string }
variable "region" { type = string }
variable "environment" { type = string }

resource "google_compute_network" "dialectica" {
  name                    = "dialectica-${var.environment}"
  project                 = var.project_id
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "dialectica" {
  name          = "dialectica-subnet-${var.environment}"
  project       = var.project_id
  region        = var.region
  network       = google_compute_network.dialectica.id
  ip_cidr_range = "10.0.0.0/20"

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.4.0.0/14"
  }
  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.8.0.0/20"
  }

  private_ip_google_access = true
}

resource "google_compute_router" "nat_router" {
  name    = "dialectica-nat-router-${var.environment}"
  project = var.project_id
  region  = var.region
  network = google_compute_network.dialectica.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "dialectica-nat-${var.environment}"
  project                            = var.project_id
  region                             = var.region
  router                             = google_compute_router.nat_router.name
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

resource "google_compute_firewall" "allow_internal" {
  name    = "dialectica-allow-internal-${var.environment}"
  project = var.project_id
  network = google_compute_network.dialectica.id

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }
  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.0.0.0/8"]
}

resource "google_compute_firewall" "allow_health_checks" {
  name    = "dialectica-allow-health-${var.environment}"
  project = var.project_id
  network = google_compute_network.dialectica.id

  allow {
    protocol = "tcp"
    ports    = ["8080", "6333", "6379", "6380", "7474", "7687"]
  }

  source_ranges = ["35.191.0.0/16", "130.211.0.0/22"]
}

output "network_id" { value = google_compute_network.dialectica.id }
output "subnet_id" { value = google_compute_subnetwork.dialectica.id }
