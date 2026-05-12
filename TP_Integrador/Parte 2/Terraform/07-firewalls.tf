# resource "google_compute_firewall" "allow-http-https" {
#   name    = "permitir-http-https"
#   network = "default"

#   allow {
#     protocol = "tcp"
#     ports    = ["80", "443"]
#   }

#   source_ranges = ["0.0.0.0/0"]
# }
# resource "google_compute_firewall" "ssh" {
#   name    = "permitir-ssh"
#   network = "default"

#   allow {
#     protocol = "tcp"
#     ports    = ["22"]
#   }

#   source_ranges = ["0.0.0.0/0"]
# }

# resource "google_compute_firewall" "flask" {
#   name    = "permitir-flask"
#   network = "default"

#   allow {
#     protocol = "tcp"
#     ports    = ["5000"]
#   }

#   source_ranges = ["0.0.0.0/0"]
# }

# resource "google_compute_firewall" "allow-rabbit-redis" {
#     name    = "allow-rabbit-redis"
#     network = google_compute_network.main.name

#     allow {
#         protocol = "tcp"
#         ports    = ["5672", "6379", "5000", "5001","5002","15672"]
#     }

#     source_ranges = ["0.0.0.0/0"]
# }

# resource "google_compute_firewall" "allow_master_to_webhook" {
#   name        = "allow-master-to-webhook"
#   network     = google_compute_network.main.id # Asegúrate de que apunte a tu red principal
#   description = "Permite al Control Plane de GKE comunicarse con los webhooks (cert-manager, ingress-nginx) en los nodos"

#   # Los puertos que los webhooks necesitan para recibir la validación
#   allow {
#     protocol = "tcp"
#     ports    = ["443", "8443", "9443", "10250"]
#   }

#   # Terraform va a buscar automáticamente el CIDR del master dentro de la configuración de tu clúster
#   source_ranges = [
#     google_container_cluster.primary.private_cluster_config[0].master_ipv4_cidr_block
#   ]
# }