#!/bin/bash
# Actualizacion de los paquetes
sudo apt update

# Instalacion Node.js 18.x
sudo apt install -y nodejs


# Instalacion OpenJDK
sudo apt install -y openjdk-18-jdk
sudo apt install -y mvn
java --version
nodejs --version

# Instalacion Nginx y poner el marcha el servidor web
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl status nginx

# Creacion de la app node (basica)
sudo touch prueba.js
sudo chmod 777 prueba.js

sudo echo "var http = require('http');

http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/html'});
  res.end('Hello World!');
}).listen(8080);"  >> prueba.js
sudo node prueba.js

#Clono el repo
sudo git clone
sudo apt-get install python3
sudo apt install python3-pip
sudo pip install django
sudo pip install djangorestframework

cd Sdypp-2024/scripts/"Django Rest Framework"
sudo manage.py runserver 0.0.0.0:3000