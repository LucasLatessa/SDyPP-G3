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
#docker --version
sudo usermod -aG docker $USER
#Clonar los contenedores
docker pull lucaslatessa/h1
docker pull lucaslatessa/h2
docker pull lucaslatessa/h3
docker pull lucaslatessa/h4
docker pull lucaslatessa/h5
docker pull lucaslatessa/h6
docker pull lucaslatessa/h6contactos
docker pull lucaslatessa/h7contactos
docker pull lucaslatessa/h7

#Correr contenedores
sudo docker run -it --rm --name h1  -p 8081:8080 lucaslatessa/h1 >> logfileh1.txt 2>&1 &
sudo docker run -it --rm --name h2  -p 8082:8080 lucaslatessa/h2 >> logfileh2.txt 2>&1 &
sudo docker run -it --rm --name h3  -p 8083:8080 lucaslatessa/h3 >> logfileh3.txt 2>&1 &
sudo docker run -it --rm --name h4 -p 8084:8080 lucaslatessa/h4 0.0.0.0 8080 35.185.81.236 8084 >> logfileh4.txt 2>&1 &
sudo docker run -it --rm --name h5 -p 8085:8080 lucaslatessa/h5 0.0.0.0 8080 35.185.81.236 8085 >> logfileh5.txt 2>&1 &

#H6
#Contactos 
sudo docker run -it --rm --name h6contactos -p 8086:8080 lucaslatessa/h6contactos >> logfileh6r.txt 2>&1 &
#ServCli.py
export PUERTO_EXT=$(shuf -i 8087-8095 -n 1)
sudo docker run -it --rm --name h6 -p $PUERTO_EXT:8080 -e PUERTO_EXT=$PUERTO_EXT lucaslatessa/h6 35.196.99.208 8086 >> logfileh6.txt 2>&1 &

#H7
#Contactos
sudo docker run -it --rm --name h7contactos -p 8087:8080 lucaslatessa/h7contactos >> logfileh7r.txt 2>&1 &
#ServCli.py
export PUERTO_EXT=$(shuf -i 8088-8095 -n 1)
sudo docker run -it --rm --name h7 -p $PUERTO_EXT:8080 -e PUERTO_EXT=$PUERTO_EXT lucaslatessa/h7 35.196.99.208 8087 >> logfileh7.txt 2>&1 &

#export PUERTO_EXT=$(shuf -i 8088-8095 -n 1)
#sudo docker run -it --rm --name h7 -p $PUERTO_EXT:8080 -e PUERTO_EXT=$PUERTO_EXT josuegaticaodato/h7 35.196.99.208 8087 >> logfileh7.txt 2>&1 &
