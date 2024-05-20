#!/bin/bash
# Actualizacion de los paquetes
sudo apt update

#Instalacion docker
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Agregar el usuario actual al grupo docker
sudo usermod -aG docker $USER

# Recargar los permisos del grupo docker
newgrp docker

# Esperar un poco para asegurarse de que Docker esté completamente cargado
sleep 10

# Clonar los contenedores
sudo docker pull josuegaticaodato/servidor_sobel

# Verificar si el pull fue exitoso
if [ $? -ne 0 ]; then
    echo "Error: El pull de la imagen Docker falló."
    exit 1
fi

# Esperar un poco más antes de ejecutar el contenedor
sleep 30

# Correr el contenedor
sudo docker run --rm --name servidor_sobel -p 5000:5000 josuegaticaodato/servidor_sobel

# Verificar si el contenedor se ejecutó correctamente
if [ $? -ne 0 ]; then
    echo "Error: El contenedor Docker no se ejecutó correctamente."
    exit 1
fi

