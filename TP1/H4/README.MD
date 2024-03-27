**Hit #4
Refactoriza el código de los programas A y B en un único programa, que funcione simultáneamente como cliente y servidor. Esto significa que al iniciar el programa C, se le deben proporcionar por parámetros la dirección IP y el puerto para escuchar saludos, así como la dirección IP y el puerto de otro nodo C. De esta manera, al tener dos instancias de C en ejecución, cada una configurada con los parámetros del otro, ambas se saludan mutuamente a través de cada canal de comunicación.

En este caso, el cliente y servidor se encuentra unificados en un solo archivo llamado "Serv_Cli.py", que recibe como parametros 4 argumentos:

    python serv_cly.py IP_SERVIDOR_DESTINO PUERTO_DESTINO IP_CLIENTE PUERTO_CLIENTE

Donde el socket del servidor se conformara por los primeros 2 parametros, esperando solicitudes que puedan llegar
Es necesario ejecutar en la terminal 2 veces el comando con las ips y puertos correspondientes para garantizar la comunicacion en ambos lados.


COMANDOS PARA CORRER DOCKER CON ARGS: corriendo los docker en nuestra maquina,
PROBLEMA: no llegan las solicitudes
docker run --rm --name h4b -p 9090:8080 ID_IMAGEN 127.0.0.1 9091 127.0.0.1 9090
docker run --rm --name h4 -p 9091:8080 ID_IMAGEN 127.0.0.1 9090 127.0.0.1 9091

Creando contenedor en docker:
docker build . -t h4 -f H4/h4.dockerfile
docker login
docker tag h4 lucaslatessa/h4
docker push lucaslatessa/h4

Comandos ejecutados en la mv de google cloud:
docker login
docker pull lucaslatessa/h4
docker run --name h4 --rm -p 8080:8080 lucaslatessa/h4
