#gcloud compute addresses create traefik-ip --global

resource "google_compute_global_address" "traefik-ip" {
  name = "traefik-ip"
}