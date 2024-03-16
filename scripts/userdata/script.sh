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
#Ingresar a Docker(como hacer para que no me pida las credenciales ni dejarlas aca)
#CREO QUE QUEDO ANDANDO, NO TOCAR NADA. lucas;)
docker login 
docker pull lucaslatessa/prueba3
docker run --name prueba --rm -p 8080:8080 lucaslatessa/prueba3



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


