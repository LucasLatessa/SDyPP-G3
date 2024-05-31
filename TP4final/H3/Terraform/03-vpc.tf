
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_network
resource "google_compute_network" "main" {
  count                           = length(data.google_compute_network.existing.*.self_link) == 0 ? 1 : 0
  name                            = "main"
  routing_mode                    = "REGIONAL"
  auto_create_subnetworks         = true
  mtu                             = 1460
  delete_default_routes_on_create = false

  depends_on = [
    google_project_service.compute,
    google_project_service.container
  ]
}
