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

resource "google_compute_firewall" "allow-rabbit-redis" {
    name    = "allow-rabbit-redis"
    network = google_compute_network.main.name

    allow {
        protocol = "tcp"
        ports    = ["5672", "6379", "5000", "5001","5002","15672"]
    }

    source_ranges = ["0.0.0.0/0"]
}