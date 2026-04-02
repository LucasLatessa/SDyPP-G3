# Hit #5
Modifique el programa C de manera tal que los mensajes se envíen en formato JSON, serializar y deserializar los mismos al enviar/recibir. 

En este caso, el cliente y servidor tambien se encuentran unificados en un solo archivo llamado "Serv_Cli.py", que recibe como parametros 4 argumentos:

```bash
python serv_cli.py IP_SERVIDOR_DESTINO PUERTO_DESTINO IP_CLIENTE PUERTO_CLIENTE
```

La diferencia radica fundamentalmente en los mensajes que se van a enviar, ya que estos se enviarán en formato JSON. 
Los mensajes se convierten en diccionarios de Python antes de ser serializados en formato JSON usando json.dumps(). Al recibir los mensajes, se decodifican desde JSON a diccionarios de Python utilizando json.loads(). 

COMANDOS PARA CORRER DOCKER CON ARGS: corriendo los docker en nuestra maquina 

## Creando contenedor en docker:

```bash
docker build . -t h5 -f H5/h5.dockerfile 
docker login 
docker tag h5 lucaslatessa/h5 
docker push lucaslatessa/h5 
```

## Comandos ejecutados en la mv de google cloud:  

```bash
sudo docker login (en ambas maquinas) 
sudo docker pull lucaslatessa/h5  (en ambas maquinas) 
```

#### VM1
```bash
sudo docker run -it --rm --name h5 -p 8085:8085 -p 10005:10005 lucaslatessa/h5 0.0.0.0 8085 35.185.81.236 8085 
```

#### VM2
```bash
sudo docker run -it --rm --name h5 -p 8085:8085 -p 10005:10005 lucaslatessa/h5 0.0.0.0 8085 35.196.99.208 8085
```

## Video explicativo 
https://youtu.be/Yzc09GvONBk