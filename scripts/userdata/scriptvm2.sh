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
docker pull lucaslatessa/h6
docker pull lucaslatessa/h6contactos
docker pull lucaslatessa/h7contactos
docker pull lucaslatessa/h7

#Correr contenedores
sudo docker run --rm --name h4 -p 8084:8080 lucaslatessa/h4 0.0.0.0 8080 35.196.99.208 8084  > logfileh4.txt 2>&1 &
sudo docker run --rm --name h5 -p 8085:8080 lucaslatessa/h5 0.0.0.0 8080 35.196.99.208 8085 > logfileh5.txt 2>&1 &

#H6
#ServCli.py
export PUERTO_EXT=$(shuf -i 8087-8095 -n 1)
sudo docker run -it --rm --name h6 -p $PUERTO_EXT:8080 -e PUERTO_EXT=$PUERTO_EXT lucaslatessa/h6 35.196.99.208 8086 >> logfileh6.txt 2>&1 &

#H7
#ATENCION LUCAS!!! MODIFICAR EL DE JOSU POR EL DE LUCAS UNA VEZ QUE ESTE HECHO
#ServCli.py
export PUERTO_EXT=$(shuf -i 8088-8095 -n 1)
sudo docker run -it --rm --name h7 -p $PUERTO_EXT:8080 -e PUERTO_EXT=$PUERTO_EXT josuegaticaodato/h7 35.196.99.208 8087 >> logfileh7.txt 2>&1 &

