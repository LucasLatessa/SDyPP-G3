# Hit #4
Refactoriza el código de los programas A y B en un único programa, que funcione simultáneamente como cliente y servidor. Esto significa que al iniciar el programa C, se le deben proporcionar por parámetros la dirección IP y el puerto para escuchar saludos, así como la dirección IP y el puerto de otro nodo C. De esta manera, al tener dos instancias de C en ejecución, cada una configurada con los parámetros del otro, ambas se saludan mutuamente a través de cada canal de comunicación. <br>

En este caso, el cliente y servidor se encuentra unificados en un solo archivo llamado "Serv_Cli.py", que recibe como parametros 4 argumentos: 

    python serv_cli.py IP_SERVIDOR_DESTINO PUERTO_DESTINO IP_CLIENTE PUERTO_CLIENTE

Donde el socket del servidor se conformara por los primeros 2 parametros, esperando solicitudes que puedan llegar <br>
Es necesario ejecutar en la terminal 2 veces el comando con las ips y puertos correspondientes para garantizar la comunicacion en ambos lados. <br>


COMANDOS PARA CORRER DOCKER CON ARGS: corriendo los docker en nuestra maquina <br>
Creando contenedor en docker: <br>
docker build . -t h4 -f H4/h4.dockerfile <br>
docker login <br>
docker tag h4 lucaslatessa/h4 <br>
docker push lucaslatessa/h4 <br>

Comandos ejecutados en la mv de google cloud: <br>
docker login (en ambas maquinas) <br>
docker pull lucaslatessa/h4  (en ambas maquinas) <br>
<br>
VM1 -> sudo docker run --rm --name h4 -p 8084:8080 lucaslatessa/h4 0.0.0.0 8080 35.185.81.236 8084<br>

VM2 -> sudo docker run --rm --name h4 -p 8084:8080 lucaslatessa/h4 0.0.0.0 8080 35.196.99.208 8084