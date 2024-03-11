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

#sudo apt install nginx -y
#sudo systemctl enable nginx
#sudo systemctl start nginx

#sudo systemctl status nginx

sudo touch prueba.js
sudo chmod 777 prueba.js

sudo echo "http = require('node:http');
listener = function (request, response) {
   // Send the HTTP header 
   // HTTP Status: 200 : OK
   // Content Type: text/html
   response.writeHead(200, {'Content-Type': 'text/html'});

   // Send the response body as "Hello World"
   response.end('<h2 style="text-align: center;">Hello World</h2>');
};

server = http.createServer(listener);
server.listen(3000);"  >> prueba.js
sudo node prueba.js
