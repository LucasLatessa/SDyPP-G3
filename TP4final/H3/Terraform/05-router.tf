#Create Cloud Router in GCP using Terraform¶
#Next, we need to create Cloud Router to advertise routes. 
#It will be used with the NAT gateway to allow VMs without public IP
#addresses to access the internet. For example, Kubernetes nodes will be able to pull docker images from the docker hub.

# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_router
resource "google_compute_router" "router" {
  name    = "router"
  region  = "us-east4"
  network = google_compute_network.main.id
}