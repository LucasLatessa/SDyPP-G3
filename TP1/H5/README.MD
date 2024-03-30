# Hit #5
Modifique el programa C de manera tal que los mensajes se envíen en formato JSON, serializar y deserializar los mismos al enviar/recibir. <br>

En este caso, el cliente y servidor tambien se encuentran unificados en un solo archivo llamado "Serv_Cli.py", que recibe como parametros 4 argumentos:

    python serv_cli.py IP_SERVIDOR_DESTINO PUERTO_DESTINO IP_CLIENTE PUERTO_CLIENTE

La diferencia radica fundamentalmente en los mensajes que se van a enviar, ya que estos se enviarán en formato JSON. <br>
Los mensajes se convierten en diccionarios de Python antes de ser serializados en formato JSON usando json.dumps(). Al recibir los mensajes, se decodifican desde JSON a diccionarios de Python utilizando json.loads(). <br>

COMANDOS PARA CORRER DOCKER CON ARGS: corriendo los docker en nuestra maquina <br>
<h2>Creando contenedor en docker: </h2> <br>
docker build . -t h5 -f H5/h5.dockerfile <br>
docker login <br>
docker tag h5 lucaslatessa/h5 <br>
docker push lucaslatessa/h5 <br>

<h2>Comandos ejecutados en la mv de google cloud:  </h2> <br>
sudo docker login (en ambas maquinas) <br>
sudo docker pull lucaslatessa/h5  (en ambas maquinas) <br>

VM1 -> sudo docker run -it --rm --name h5 -p 8085:8085 -p 10005:10005 lucaslatessa/h5 0.0.0.0 8085 35.185.81.236 8085 <br>

VM2 -> sudo docker run -it --rm --name h5 -p 8085:8085 -p 10005:10005 lucaslatessa/h5 0.0.0.0 8085 35.196.99.208 8085

