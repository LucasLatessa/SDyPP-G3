
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