# Hit #4
Refactoriza el código de los programas A y B en un único programa, que funcione simultáneamente como cliente y servidor. Esto significa que al iniciar el programa C, se le deben proporcionar por parámetros la dirección IP y el puerto para escuchar saludos, así como la dirección IP y el puerto de otro nodo C. De esta manera, al tener dos instancias de C en ejecución, cada una configurada con los parámetros del otro, ambas se saludan mutuamente a través de cada canal de comunicación. 

En este caso, el cliente y servidor se encuentra unificados en un solo archivo llamado "Serv_Cli.py", que recibe como parametros 4 argumentos: 

```bash
python serv_cli.py IP_SERVIDOR_DESTINO PUERTO_DESTINO IP_CLIENTE PUERTO_CLIENTE
```

Donde el socket del servidor se conformara por los primeros 2 parametros, esperando solicitudes que puedan llegar 
Es necesario ejecutar en la terminal 2 veces el comando con las ips y puertos correspondientes para garantizar la comunicacion en ambos lados. 


COMANDOS PARA CORRER DOCKER CON ARGS: corriendo los docker en nuestra maquina 

## Creando contenedor en docker:  

```bash
docker build . -t h4 -f H4/h4.dockerfile 
docker login 
docker tag h4 josuegaticaodato/h4 
docker push josuegaticaodato/h4 
```

### Comandos ejecutados en la mv de google cloud:   

```bash
sudo docker login (en ambas maquinas) 
sudo docker pull josuegaticaodato/h4  (en ambas maquinas) 
```

#### VM1
```bash
sudo docker run -it --rm --name h4 -p 8084:8084 -p 10004:10004 josuegaticaodato/h4 0.0.0.0 8084 35.185.81.236 8084 
```

#### VM2
```bash
sudo docker run -it --rm --name h4 -p 8084:8084 -p 10004:10004 josuegaticaodato/h4 0.0.0.0 8084 35.196.99.208 8084
```


##  Video explicativo 
https://youtu.be/ZDkjU9cPaZY