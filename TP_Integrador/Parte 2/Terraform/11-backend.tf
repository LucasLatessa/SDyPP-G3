terraform {
  required_version = ">= 1.0.0"

  # Guardar el estado en la nube
  backend "gcs" {
    bucket  = "sdypp2026-terraform-state-g3" 
    prefix  = "terraform/state"              # La carpeta dentro del bucket
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.20.0"
    }
  }
}