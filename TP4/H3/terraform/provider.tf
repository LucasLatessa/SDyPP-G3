data "google_client_openid_userinfo" "me" {}

# Configuración de Google Cloud Platform
provider "google" {
  credentials = file("credentials.json")
  project     = var.nombre_proyecto
  region      = var.region
}