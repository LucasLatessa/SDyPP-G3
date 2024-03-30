# Hit #2
Revise el código de A para implementar una funcionalidad que permita la reconexión y el envío del saludo nuevamente en caso de que el proceso B cierre la conexión, como por ejemplo, al ser terminado abruptamente. <br>

El servidor funciona de igual manera que el ejercicio anterior <br>
En el caso del cliente, se definen dos nuevas funciones: <br>
    .Conectar = Encargado de realizar la conexion con el server que, si es rechazada, se reintenta reestablecer la conexion en 5 segundos <br>
    .enviarsaludo = Envia la peticion al servidor cada 10 segundos <br>

En una terminal, para ejecutar el cliente utilizamos:

    python cliente.py

<h2>Comando para contenedores y gcloud</h2> <br>
Creando contenedor en docker: <br> 
docker build . -t h2 -f H2/h2.dockerfile <br>
docker login <br>
docker tag h2 josuegaticaodato/h2 <br>
docker push josuegaticaodato/h2 <br>

<h2>Comandos ejecutados en la mv de google cloud:</h2><br>
sudo docker login <br>
sudo docker pull josuegaticaodato/h2 <br>

Para visualziar el contenido en consola: sudo docker run -it --rm --name h2 -p 8082:8082 -p 10002:10002 josuegaticaodato/h2 <br>
Para guarda en .txt: sudo docker run --rm --name h2 -p 8082:8082 -p 10002:10002 josuegaticaodato/h2  >> logfileh2.txt 2>&1 & <br>

<h2> Video explicativo </h2>
https://youtu.be/eGd4lLGNlBU