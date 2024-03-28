# Hit #1
Elabore un código de servidor TCP para B que espere el saludo de A y lo responda.
Elabore un código de cliente TCP para A que se conecte con B y lo salude.

El archivo server.py representar a el nodo B, mientras que el archivo cliente.py representara al nodo A.
Se levanta el servidor desde la terminal con "python server.py", con el host 0.0.0.0 (cualquiera) y el puerto 8080
Se realiza una peticion con el cliente usando "python cliente.py", donde este enviara el mensaje al servidor y recibira una respuesta.

Comando para contenedores y gcloud
Creando contenedor en docker:
docker build . -t h1 -f H1/h1.dockerfile
docker login
docker tag h1 lucaslatessa/h1
docker push lucaslatessa/h1

Comandos ejecutados en la mv de google cloud:
docker login
docker pull lucaslatessa/h1
docker run --name h1 --rm -p 8080:8080 lucaslatessa/h1