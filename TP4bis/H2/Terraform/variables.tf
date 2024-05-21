variable "numero_instancias" {
  type    = number
  default = 1
}

variable "startup_rabbit" {
  type    = string
  default = "rabbit.sh"
}

variable "startup_worker" {
  type    = string
  default = "worker.sh"
}

variable "startup_ws" {
  type    = string
  default = "ws.sh"
}

variable "startup_redis" {
  type    = string
  default = "ws.sh"
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
  default = "ubuntu-2204-jammy-v20240515"
}

