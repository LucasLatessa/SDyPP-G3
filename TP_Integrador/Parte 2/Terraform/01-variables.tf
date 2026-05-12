variable "numero_instancias" {
  type    = number
  default = 3
}

variable "startup_worker" {
  type    = string
  default = "worker.sh"
}

variable "nombre_proyecto" {
  type    = string
  default = "sdypp2026"
}

variable "tipo_maquina" {
  type    = string
  default = "e2-standard-2"
}

variable "zona" {
  type    = string
  default = "us-east4-b"
}

variable "region" {
  type    = string
  default = "us-east4"
}

variable "imagen" {
  type    = string
  default = "ubuntu-os-cloud/ubuntu-2004-lts"
}

variable "nombre_infra" {
  type    = string
  default = "infra-node-pool"
}

variable "nombre_app" {
  type    = string
  default = "app-node-pool"
}
