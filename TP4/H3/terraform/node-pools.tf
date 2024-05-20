resource "google_service_account" "kubernetes" {
  account_id = "kubernetes"
}

resource "google_container_node_pool" "infra_pool" {
  name       = "infra-pool"
  cluster    = google_container_cluster.primary.id
  node_count = 0

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  autoscaling {
    min_node_count = 1
    max_node_count = 10
  }

  node_config {
    preemptible  = false
    machine_type = var.tipo_maquina

    labels = {
      role = "infraestructura"
    }

    service_account = google_service_account.kubernetes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

  }
}

resource "google_container_node_pool" "app_pool" {
  name       = "app-pool"
  cluster    = google_container_cluster.primary.id
  node_count = 2

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  autoscaling {
    min_node_count = 2
    max_node_count = 10
  }

  node_config {
    preemptible  = false
    machine_type = var.tipo_maquina

    labels = {
      role = "application"
    }

    taint {
      key    = "instance_type"
      value  = "app-pool"
      effect = "NO_SCHEDULE"
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