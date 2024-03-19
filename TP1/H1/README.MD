Creando contenedor en docker:
docker build . -t prueba3 -f dockerfiles/ejemplo3.dockerfile
docker login
docker tag h1 lucaslatessa/h1
docker push lucaslatessa/h1

Comandos ejecutados en la mv de google cloud:
docker login
docker pull lucaslatessa/h1
docker run --name h1 --rm -p 8080:8080 lucaslatessa/h1
