resource "google_container_cluster" "primary" {
  name                     = "cluster"
  location                 = "us-east1-b"
  remove_default_node_pool = true
  initial_node_count       = 1

  node_config {
    machine_type = var.tipo_maquina
  }

  deletion_protection = false

}


