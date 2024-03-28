#!/bin/bash
# Actualizacion de los paquetes
sudo apt update

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

sudo usermod -aG docker $USER

#Clonar los contenedores
docker pull lucaslatessa/h4
docker pull lucaslatessa/h5

#Correr contenedores
sudo docker run --rm --name h4 -p 8084:8080 lucaslatessa/h4 0.0.0.0 8080 35.196.99.208 8084  > logfileh4.txt 2>&1 &
sudo docker run --rm --name h5 -p 8085:8080 lucaslatessa/h5 0.0.0.0 8080 35.196.99.208 8085 > logfileh5.txt 2>&1 &

 docker pull lucaslatessa/h6
# docker run --name h6 --rm -p 8086:8080 lucaslatessa/h6 &

 docker pull lucaslatessa/h7
# docker run --name h7 --rm -p 8087:8080 -e IP_SERVIDOR_DESTINO=35.185.81.236 -e PUERTO_DESTINO=8087 -e IP_CLIENTE=127.0.0.1 -e PUERTO_CLIENTE=8090 lucaslatessa/h6 &
# docker run --name h7b --rm -p 8090:8080 -e IP_SERVIDOR_DESTINO=35.185.81.236 -e PUERTO_DESTINO=8090 -e IP_CLIENTE=127.0.0.1 -e PUERTO_CLIENTE=8087 lucaslatessa/h6 &
