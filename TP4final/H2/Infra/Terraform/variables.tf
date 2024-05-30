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
  default = "sdypp-2024"
}

variable "tipo_maquina" {
  type    = string
  default = "e2-small"
}

variable "zona" {
  type    = string
  default = "us-east4-a"
}

variable "region" {
  type    = string
  default = "us-east4"
}

variable "imagen" {
  type    = string
  default = "ubuntu-os-cloud/ubuntu-2004-lts"
}

