Creando contenedor en docker:
docker build . -t h2 -f TP1/H2/h2.dockerfile
docker login
docker tag h1 lucaslatessa/h2
docker push lucaslatessa/h2

Comandos ejecutados en la mv de google cloud:
docker login
docker pull lucaslatessa/h2
docker run --name h2 --rm -p 8080:8080 lucaslatessa/h2
