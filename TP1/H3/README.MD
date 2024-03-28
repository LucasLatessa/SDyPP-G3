# Hit #3
Modifique el código de B para que si el proceso A cierra la conexión (por ejemplo matando el proceso) siga funcionando <br>

En este caso, el cliente sigue igual que el ejercicio anterior. <br>
El servidor tiene que mantener abierto luego de terminar la conexion con cualquier nodo A, y esto se realiza aplicando un ciclo infinito para la apertura, peticion y cierre de la conexion <br>

Creando contenedor en docker: <br>
docker build . -t h3 -f H3/h3.dockerfile <br>
docker login <br>
docker tag h3 lucaslatessa/sdpp/h3 <br>
docker push lucaslatessa/sdpp/h3 <br>

Comandos ejecutados en la mv de google cloud: <br>
docker login <br>
docker pull lucaslatessa/h3 <br>
docker run --name h3 --rm -p 8083:8080 lucaslatessa/h3 <br>
