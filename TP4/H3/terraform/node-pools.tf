resource "google_service_account" "kubernetes" {
  account_id = "kubernetes"
}

resource "google_container_node_pool" "infra_pool" {
  name       = "infra-pool"
  cluster    = google_container_cluster.primary.id
  node_count = 1

  node_config {
    preemptible  = false
    machine_type = var.tipo_maquina

    labels = {
      role = "infraestructura"
    }

  }
}

resource "google_container_node_pool" "app_pool" {
  name       = "app-pool"
  cluster    = google_container_cluster.primary.id
  node_count = 2

  node_config {
    preemptible  = false
    machine_type = var.tipo_maquina

    labels = {
      role = "application"
    }

  }
}

#Workers
resource "google_compute_instance" "workers" {
  count        = var.numero_instancias
  name         = "worker-v${count.index + 1}"
  machine_type = var.tipo_maquina
  zone         = var.zona
  metadata_startup_script = file(var.metadata_startup_script)
  
  metadata = {
    ssh-keys = "${split("@", data.google_client_openid_userinfo.me.email)[0]}:${tls_private_key.ssh.public_key_openssh}"
  }

  boot_disk {
    initialize_params {
      image = var.imagen
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }
  
}