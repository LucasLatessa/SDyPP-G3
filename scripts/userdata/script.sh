#!/bin/bash
# Actualizacion de los paquetes
sudo apt update

# # Instalacion Node.js 18.x
# sudo apt install -y nodejs


# # Instalacion OpenJDK
# sudo apt install -y openjdk-18-jdk
# sudo apt install -y mvn
# java --version
# nodejs --version

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
docker run --name h1 --rm -p 8081:8080 lucaslatessa/h1 &
docker run --name h2 --rm -p 8082:8080 lucaslatessa/h2 &
docker run --name h3 --rm -p 8083:8080 lucaslatessa/h3 &

docker pull lucaslatessa/h4
# docker run --name h4 --rm -p 8084:8080 -e IP_SERVIDOR_DESTINO=35.185.81.236 -e PUERTO_DESTINO=8084 -e IP_CLIENTE=127.0.0.1 -e PUERTO_CLIENTE=8088 lucaslatessa/h4 &
# docker run --name h4b --rm -p 8088:8080 -e IP_SERVIDOR_DESTINO=35.185.81.236 -e PUERTO_DESTINO=8088 -e IP_CLIENTE=127.0.0.1 -e PUERTO_CLIENTE=8084 lucaslatessa/h4 &

 docker pull lucaslatessa/h5
# docker run --name h5 --rm -p 8085:8080 -e IP_SERVIDOR_DESTINO=35.185.81.236 -e PUERTO_DESTINO=8085 -e IP_CLIENTE=127.0.0.1 -e PUERTO_CLIENTE=8089 lucaslatessa/h5 &
# docker run --name h5b --rm -p 8089:8080 -e IP_SERVIDOR_DESTINO=35.185.81.236 -e PUERTO_DESTINO=8089 -e IP_CLIENTE=127.0.0.1 -e PUERTO_CLIENTE=8085 lucaslatessa/h5 &

 docker pull lucaslatessa/h6
# docker run --name h6 --rm -p 8086:8080 lucaslatessa/h6 &

 docker pull lucaslatessa/h7
# docker run --name h7 --rm -p 8087:8080 -e IP_SERVIDOR_DESTINO=35.185.81.236 -e PUERTO_DESTINO=8087 -e IP_CLIENTE=127.0.0.1 -e PUERTO_CLIENTE=8090 lucaslatessa/h6 &
# docker run --name h7b --rm -p 8090:8080 -e IP_SERVIDOR_DESTINO=35.185.81.236 -e PUERTO_DESTINO=8090 -e IP_CLIENTE=127.0.0.1 -e PUERTO_CLIENTE=8087 lucaslatessa/h6 &


# # Instalacion Nginx y poner el marcha el servidor web
# sudo apt install nginx -y
# sudo systemctl enable nginx
# sudo systemctl start nginx
# sudo systemctl status nginx

# # Creacion de la app node (basica)
# sudo touch prueba.js
# sudo chmod 777 prueba.js

# sudo echo "var http = require('http');

# http.createServer(function (req, res) {
#   res.writeHead(200, {'Content-Type': 'text/html'});
#   res.end('Hello World!');
# }).listen(8080);"  >> prueba.js
# sudo node prueba.js


