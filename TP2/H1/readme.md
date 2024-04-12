comando
docker build . -t josuegaticaodato/servidorweb -f servidor.dockerfile

docker pull josuegaticaodato/servidorweb
docker network create --attachable prueba
docker run --network=prueba --rm --name spweb -v /var/run/docker.sock:/var/run/docker.sock -p 8080:8080 josuegaticaodato/servidorweb

docker stop $(docker ps -a -q)