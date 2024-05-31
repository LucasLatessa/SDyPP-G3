data "google_client_openid_userinfo" "me" {}

# Recurso de instancia de Google Compute Engine
resource "google_compute_instance" "worker" {
  count        = var.numero_instancias
  name         = "worker-${count.index + 1}"
  machine_type = var.tipo_maquina
  zone         = var.zona
  metadata_startup_script = file(var.startup_worker)
  
  metadata = {
    ssh-keys = "${split("@", data.google_client_openid_userinfo.me.email)[0]}:${tls_private_key.ssh.public_key_openssh}"
  }

  scheduling {
      preemptible                 = true
      automatic_restart           = false
      provisioning_model          = "SPOT"
      instance_termination_action = "TERMINATE"
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