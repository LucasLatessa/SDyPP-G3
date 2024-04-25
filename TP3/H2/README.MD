# Hit #2

1. Utilice #user_data para instalar paquetes (wget, htop, etc) en sus servidores Linux como defecto.

Esto lo realizaremos mediante la ejecucion de un script "paquetes.sh"

```
#paquetes.sh

#!/bin/bash

sudo apt update -y 
sudo apt install -y nginx
sudo apt-get install -y wget htop
```

Que estara como variable a la hora de crear la instancia

```
#variables.tf
variable "metadata_startup_script" {
    type= string
    default= "paquetes.sh"
}
```

```
#main.tf
resource "google_compute_instance" "ejemplo" {
  ...
  metadata_startup_script = file(var.metadata_startup_script)
  ...
}
```

2. Cree reglas de seguridad para acceder a puertos necesarios en las instancias (ssh 22, http 80, https 443)

Las variables de firewall sera un nuevo resource

```
#main.tf
resource "google_compute_firewall" "allow-http-https" {
  name    = "permitir-http-https"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
}
resource "google_compute_firewall" "ssh" {
  name    = "permitir-ssh"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
}
```

3. Configure SSH para poder acceder al servidor.

Creamos un nuevo archivo terraform, que cree una clave privada SSH usando TLS y la guarde en un archivo

```
resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_file" "ssh_private_key_pem" {
  content         = tls_private_key.ssh.private_key_pem
  filename        = ".ssh/google_compute_engine"
  file_permission = "0600"
}
```

Esto se agrega al main.tf

```
resource "google_compute_instance" "ejemplo" {
    ...
  metadata = {
    ssh-keys = "${split("@", data.google_client_openid_userinfo.me.email)[0]}:${tls_private_key.ssh.public_key_openssh}"
  }
  ...
}
```

4. Conéctese por ssh y haga un wget de un archivo grande (por ejemplo ISO de ubuntu: https://releases.ubuntu.com/jammy/ubuntu-22.04.2-desktop-amd64.iso) desde su pc y uno desde la instancia virtual.  Compare y comente las velocidades de descarga. ¿A qué se debe esta diferencia?

Velocidad de descarga desde la instancia virtual: 40s
Velocidad de descargar desde nuestra pc: 15min.

Esta notable diferencia se debe a un factor principal que es la alta velocidad a Internet que presenta la instancia con respecto a la pc, haciendo que sea posible descargar archivos a velocidades cercanas a la capacidad maxima de su conexion. Ademas, entra en juego las distancias geograficas que hay entre el servidor que provee el archivo con la instancia y la pc.

5. Copie un archivo desde / hacia una Instancia (scp).

Copia de Maquina virtual a maquina local

```
gcloud compute scp --recurse instancia-1:/home/Leone/prueba.txt .
```

Copia de Maquina local a maquina virtual

```
gcloud compute scp ./prueba.txt instancia-1:/home/Leone
```