# Hit #2
Revise el código de A para implementar una funcionalidad que permita la reconexión y el envío del saludo nuevamente en caso de que el proceso B cierre la conexión, como por ejemplo, al ser terminado abruptamente.

El servidor funciona de igual manera que el ejercicio anterior
En el caso del cliente, se definen dos nuevas funciones:
.Conectar = Encargad de realizar la conexion con el server que, si es rechazada, se reintenta reestablecer la conexion en 5 segundos
.enviarsaludo = Envia la peticion al servidor cada 10 segundos

Creando contenedor en docker:
docker build . -t h2 -f H2/h2.dockerfile
docker login
docker tag h2 lucaslatessa/h2
docker push lucaslatessa/h2

Comandos ejecutados en la mv de google cloud:
docker login
docker pull lucaslatessa/h2
docker run --name h2 --rm -p 8080:8080 lucaslatessa/h2
