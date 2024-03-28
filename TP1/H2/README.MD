# Hit #2
Revise el código de A para implementar una funcionalidad que permita la reconexión y el envío del saludo nuevamente en caso de que el proceso B cierre la conexión, como por ejemplo, al ser terminado abruptamente. <br>

El servidor funciona de igual manera que el ejercicio anterior <br>
En el caso del cliente, se definen dos nuevas funciones: <br>
.Conectar = Encargad de realizar la conexion con el server que, si es rechazada, se reintenta reestablecer la conexion en 5 segundos <br>
.enviarsaludo = Envia la peticion al servidor cada 10 segundos <br>

Creando contenedor en docker: <br> 
docker build . -t h2 -f H2/h2.dockerfile <br>
docker login <br>
docker tag h2 lucaslatessa/h2 <br>
docker push lucaslatessa/h2 <br>

Comandos ejecutados en la mv de google cloud: <br>
docker login <br>
docker pull lucaslatessa/h2 <br>
docker run --name h2 --rm -p 8082:8080 lucaslatessa/h2 <br>
