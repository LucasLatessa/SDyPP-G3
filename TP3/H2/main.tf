data "google_client_openid_userinfo" "me" {}

# Configuración de Google Cloud Platform
provider "google" {
  credentials = file("credentials.json")
  project     = "organic-premise-416700"
  region      = "us-east1"
}

# Recurso de instancia de Google Compute Engine
resource "google_compute_instance" "ejemplo" {
  count        = var.numero_instancias
  name         = "instancia-${count.index + 1}"
  machine_type = "n1-standard-1"
  zone         = "us-east1-b"
  metadata_startup_script = file(var.metadata_startup_script)
  
  metadata = {
    ssh-keys = "${split("@", data.google_client_openid_userinfo.me.email)[0]}:${tls_private_key.ssh.public_key_openssh}"
  }

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-10"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }
  
}
resource "google_compute_firewall" "allow-http-https" {
  name    = "permitir-http-https"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
}
resource "google_compute_firewall" "ssh" {
  name    = "permitir-ssh"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
}
