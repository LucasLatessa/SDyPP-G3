variable "numero_instancias" {
  type    = number
  default = 1
}

variable "startup-app" {
  type    = string
  default = "app.sh"
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

