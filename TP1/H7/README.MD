# Hit #7
Modifique el programa C y D, de manera tal de implementar un “sistema de inscripciones”, esto es, se define una ventana de tiempo fija de 1 MIN, coordinada por D, y los nodos C deben registrarse para participar de esa ventana, cuando un nodo C se registra a las 11:28:34 en D, el registro se hace efectivo para la próxima ventana de tiempo que corresponde a las 11:29. Cuando se alcanza las 11:29:00 el nodo D cierra las inscripciones y todo nodo C que se registre será anotado para la ventana de las 11:30, los nodos C que consulten las inscripciones activas solo pueden ver las inscripciones de la ventana actual, es decir, los nodos C no saben a priori cuales son sus pares para la próxima ventana de tiempo, solo saben los que están activos actualmente. Recuerde almacenar las inscripciones en un archivo de texto con formato JSON. Esto facilitará el seguimiento ordenado de las ejecuciones y asegurará la verificación de los resultados esperados.
Para simplificar el problema, imagine que D lleva dos registros, un listado de los nodos C activos en la ventana actual, y un registro de nodos C registrados para la siguiente ventana. Cada 60 segundos el nodo D mueve los registros de las inscripciones futuras a la presente y comienza a inscribir para la siguiente ronda. <br1>

Al igual que el Hit anterior, se tiene un Nodo D con registro de contactos, pero la unica diferencia es que se definen ventanas de tiempo para que los nodos C puedan registrarse.<br<
Para este ejercicio, obtamos por definir dos arreglos:<br>
    .Actuales = Este es el que se le pasa a los nodos para comunicarse<br>
    .Siguinete = Guarda los nodos que vaya entrando en la ventana<br>
Pasalo los 60 segundos que establece la ventana, el arreglo de actuales pasa a ser el de siguientes, mientras en este ultimo se borra su contenido para comenzar a agregar a los nuevos nodos C<br>

<h2>Creando contenedor en docker  </h2> <br>
(Serv_Cly): <br>
docker build . -t h7 -f H7/h7.dockerfile <br>
docker login <br>
docker tag h7 josuegaticaodato/h7 <br>
docker push josuegaticaodato/h7 <br>

(RegistroContactos): <br>
docker build . -t h7contactos -f h7/h7contactos.dockerfile <br>
docker login <br>
docker tag h7contactos josuegaticaodato/h7contactos <br>
docker push josuegaticaodato/h7contactos <br>

<h2>Comandos ejecutados en la mv de google cloud:  </h2> <br>
sudo docker login (en ambas maquinas) <br>
sudo docker pull josuegaticaodato/h7  (en todas las maquinas) <br>
sudo docker pull josuegaticaodato/h7contactos  (en V1) <br>

VM1:<br>
Contactos:<br>
sudo docker run -it --rm --name h7contactos -p 8089:8089 -p 10009:10009 josuegaticaodato/h7contactos >> logfileh7r.txt 2>&1 &<br>

VM1,VM2 y VM3 <br>
Serv_Cli.py:<br>
export PUERTO_EXT=$(shuf -i 8087-8095 -n 1)
sudo docker run -it --rm --name h7 -p $PUERTO_EXT:$PUERTO_EXT -p 10007:10007 -e PUERTO_EXT=$PUERTO_EXT josuegaticaodato/h7 35.196.99.208 8089 >> logfileh7.txt 2>&1 &<br>
<br>

En el caso de no querer crear puertos aleatorios se modifica la variable de entorno $PUERTO_EXT por un puerto determinado <br>

<h2> Video explicativo </h2>
https://youtu.be/d-Gujuci2q4