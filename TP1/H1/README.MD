# Hit #1
Elabore un código de servidor TCP para B que espere el saludo de A y lo responda.
Elabore un código de cliente TCP para A que se conecte con B y lo salude. <br>

El archivo server.py representar a el nodo B, mientras que el archivo cliente.py representara al nodo A. <br>
Se levanta el servidor desde la terminal con "python server.py", con el host 0.0.0.0 (cualquiera) y el puerto 8080 <br>
Se realiza una peticion con el cliente usando "python cliente.py", donde este enviara el mensaje al servidor y recibira una respuesta. <br>

<h2>Comando para contenedores y gcloud</h2> <br>
Creando contenedor en docker: <br> 
docker build . -t h1 -f H1/h1.dockerfile <br>
docker login <br>
docker tag h1 lucaslatessa/h1 <br>
docker push lucaslatessa/h1 <br>

<h2>Comandos ejecutados en la mv de google cloud:</h2><br>
sudo docker login <br>
sudo docker pull lucaslatessa/h1 <br>

Para visualziar el contenido en consola: sudo docker run -it --rm --name h1 -p 8081:8081 -p 10001:10001 lucaslatessa/h1 <br>
Para guarda en .txt: sudo docker run --rm --name h1 -p 8081:8081 -p 10001:10001 lucaslatessa/h1 >> logfileh1.txt 2>&1 & <br>