variable "numero_instancias" {
  type    = number
  default = 1
}

variable "metadata_startup_script" {
  type    = string
  default = "paquetes.sh"
}

variable "nombre_proyecto" {
  type    = string
  default = "sdypp-2024"
}

variable "tipo_maquina" {
  type    = string
  default = "e2-micro"
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
  default = "debian-cloud/debian-10"
}

