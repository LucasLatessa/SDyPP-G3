#!/bin/bash

sudo apt update -y

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
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER
#Clonar los contenedores
docker pull josuegaticaodato/servidor_sobel

#Correr contenedores
sudo docker run -it --rm --name servidor_sobel  -p 5000:5000 josuegaticaodato/servidor_sobel >> logfile.txt 2>&1 &