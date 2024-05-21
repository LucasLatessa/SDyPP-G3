data "google_client_openid_userinfo" "me" {}

# Configuración de Google Cloud Platform
provider "google" {
  credentials = file("credentials.json")
  project     = var.nombre_proyecto
  region      = var.region
}

# Instancia rabbit
resource "google_compute_instance" "rabbitMQ" {
  count        = 1
  name         = "rabbit-mq"
  machine_type = var.tipo_maquina
  zone         = var.zona
  metadata_startup_script = file(var.startup_rabbit)

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

# Instancia redis
resource "google_compute_instance" "redis" {
  count        = 1
  name         = "redis"
  machine_type = var.tipo_maquina
  zone         = var.zona
  metadata_startup_script = file(var.startup_redis)

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

# Instancia de los workers
resource "google_compute_instance" "worker" {
  count        = var.numero_instancias
  name         = "worker-${count.index + 1}"
  machine_type = var.tipo_maquina
  zone         = var.zona
  metadata_startup_script = file(var.startup_worker)

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

# Instancia de los workers
resource "google_compute_instance" "web-server" {
  count        = var.numero_instancias
  name         = "web-server"
  machine_type = var.tipo_maquina
  zone         = var.zona
  metadata_startup_script = file(var.startup_ws)

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