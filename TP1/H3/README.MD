# Hit #3
Modifique el código de B para que si el proceso A cierra la conexión (por ejemplo matando el proceso) siga funcionando

En este caso, el cliente sigue igual que el ejercicio anterior.
El servidor tiene que mantener abierto luego de terminar la conexion con cualquier nodo A, y esto se realiza aplicando un ciclo infinito para la apertura, peticion y cierre de la conexion

Creando contenedor en docker:
docker build . -t h3 -f H3/h3.dockerfile
docker login
docker tag h3 lucaslatessa/sdpp/h3
docker push lucaslatessa/sdpp/h3

Comandos ejecutados en la mv de google cloud:
docker login
docker pull lucaslatessa/h3
docker run --name h3 --rm -p 8080:8080 lucaslatessa/h3
