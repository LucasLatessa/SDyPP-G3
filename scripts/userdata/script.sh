#!/bin/bash
# Update package list
sudo apt update

# Install Node.js 18.x
sudo apt install -y nodejs


# Install OpenJDK
sudo apt install -y openjdk-18-jdk
sudo apt install -y mvn
java --version
nodejs --version

sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx

sudo systemctl status nginx

sudo touch prueba.js
sudo chmod 777 prueba.js

sudo echo "var http = require('http');

http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/html'});
  res.end('Hello World!');
}).listen(8080);"  >> prueba.js
sudo node prueba.js


