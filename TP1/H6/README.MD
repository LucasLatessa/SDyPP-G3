# Hit #6
Cree un programa D, el cual, actuará como un “Registro de contactos”. Para ello, en un array en ram, inicialmente vacío, este nodo D llevará un registro de los programas C que estén en ejecución.  <br>

Modifique el programa C de manera tal que reciba por parámetros únicamente la ip y el puerto del programa D. C debe iniciar la escucha en un puerto aleatorio y debe comunicarse con D para informarle su ip y su puerto aleatorio donde está escuchando. D le debe responder con las ips y puertos de los otros nodos C que estén corriendo, haga que C se conecte a cada uno de ellos y envíe el saludo. <br>

Es decir, el objetivo de este HIT es incorporar un nuevo tipo de nodo (D) que actúe como registro de contactos para que al iniciar cada nodo C no tenga que indicar las ips de sus pares. Esto debe funcionar con múltiples instancias de C, no solo con 2. <br>

El Nodo C tiene: <br>
    .Un servidor, corriendo en un puerto aleatorio <br>
    .Un cliente, encargado de realizar peticiones cada vez que reciba una lista de contactos

Cada vez que el Nodo C envia una peticion a el Nodo D (que se encuentra en escucha, en un ip y puerto conocido por C), este pasa como JSON su socket para recibir futuras conexiones con otros nodos de su misma clase. En respuesta, el nodo D devuelve la lista de contactos que tiene, y agrega un nuevo contacto con los datos recibidos. <br>

Por cada contacto que haya recibido C, este realiza una peticion, este caido o no el servidor <br>

<h2>Creando contenedor en docker  </h2> <br>
(Serv_Cly): <br>
docker build . -t h6 -f H6/h6.dockerfile <br>
docker login <br>
docker tag h6 lucaslatessa/h6 <br>
docker push lucaslatessa/h6 <br>

(RegistroContactos): <br>
docker build . -t h6contactos -f H6/h6contactos.dockerfile <br>
docker login <br>
docker tag h6contactos lucaslatessa/h6contactos <br>
docker push lucaslatessa/h6contactos <br>

<h2>Comandos ejecutados en la mv de google cloud:  </h2> <br>
sudo docker login (en ambas maquinas) <br>
sudo docker pull lucaslatessa/h6  (en ambas maquinas) <br>
sudo docker pull lucaslatessa/h6contactos  (en V1) <br>

VM1:<br>
Contactos:<br>
sudo docker run -it --rm --name h6contactos -p 8088:8088 -p 10008:10008 lucaslatessa/h6contactos >> logfileh6r.txt 2>&1 &<br>

VM1 y VM2 <br>
Serv_Cli.py:<br>
export PUERTO_EXT=$(shuf -i 8087-8095 -n 1)
sudo docker run -it --rm --name h6 -p $PUERTO_EXT:$PUERTO_EXT -p 10006:10006 -e PUERTO_EXT=$PUERTO_EXT lucaslatessa/h6 35.196.99.208 8088 >> logfileh6.txt 2>&1 &<br>
<br>

En el caso de no querer crear puertos aleatorios se modifica la variable de entorno $PUERTO_EXT por un puerto determinado <br>