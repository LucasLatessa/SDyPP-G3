# Hit #1
Implemente un servidor que resuelva “tareas genéricas” o “pre-compiladas”. Para ello, hay un conjunto de acciones de diseño y arquitectura que deben respetarse

Se construyo el servidor web utilizando Python con el framework Flask, que permite crear aplicaciones web.
Nuestro servidor tiene el metodo ejecutarTareaRemota(), vinculado al endpoint /getRemoteTask, para recibir las peticiones del cliente.
Este recibe el json enviado por el cliente, separando la imagen de los datos en si de la tarea a realizar, para poder crear el contenedor encargado de realizar la tarea, que sera nuestro tarea.py, encargado de realizar una tarea generica, en nuestro caso, una operacion matematica basica.
Una vez levantado el contenedor y escuchando en el puerto 5000 del contenedor, el servidor le envia la peticion para obtener como resultado la respuesta a la tarea y devolverla al cliente.

<h2>Comando para contenedores y gcloud</h2> <br>
Creando contenedor en docker: <br> 
docker build . -t josuegaticaodato/servidorweb -f servidor.dockerfile

<h2>Comandos ejecutados en la mv de google cloud:</h2><br>
Pull al servidor web: <br>
docker pull josuegaticaodato/servidorweb
<br>

Creacion de la red para comunicar los contenedores: <br>
docker network create --attachable prueba

Ejecucion del servidor web <br>
docker run --network=prueba --rm --name spweb -v /var/run/docker.sock:/var/run/docker.sock -p 8080:8080 josuegaticaodato/servidorweb

Para matar todos los contenedores<br>
docker stop $(docker ps -a -q)

<h2> Video explicativo </h2>
https://youtu.be/_GMM6e_9xYk