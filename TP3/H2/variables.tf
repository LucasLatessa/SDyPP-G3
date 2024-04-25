
variable "numero_instancias" {
    type=number
    default= 3
}

variable "metadata_startup_script" {
    type= string
    default= "paquetes.sh"
}