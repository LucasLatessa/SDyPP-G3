# Hit #3
Modifique el código de B para que si el proceso A cierra la conexión (por ejemplo matando el proceso) siga funcionando <br>

En este caso, el cliente sigue igual que el ejercicio anterior. <br>
El servidor tiene que mantener abierto luego de terminar la conexion con cualquier nodo A, y esto se realiza aplicando un ciclo infinito para la apertura, peticion y cierre de la conexion <br>

En una terminal, para ejecutar el cliente utilizamos:

    python cliente.py

<h2>Comando para contenedores y gcloud</h2>
docker build . -t h3 -f H3/h3.dockerfile <br>
docker login <br>
docker tag h3 josuegaticaodato/h3 <br>
docker push josuegaticaodato/h3 <br>

<h2>Comandos ejecutados en la mv de google cloud:</h2><br>
sudo docker login <br>
sudo docker pull josuegaticaodato/h3 <br>

Para visualziar el contenido en consola: sudo docker run -it --rm --name h3 -p 8083:8083 -p 10003:10003 josuegaticaodato/h3 <br>
Para guarda en .txt: sudo docker run --rm --name h3 -p 8083:8083 -p 10003:10003 josuegaticaodato/h3  >> logfileh3.txt 2>&1 & <br>

<h2> Video explicativo </h2>
https://youtu.be/FcBMjfBHOfQ