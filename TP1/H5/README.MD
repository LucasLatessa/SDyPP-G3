Hit #5
Modifique el programa C de manera tal que los mensajes se envíen en formato JSON, serializar y deserializar los mismos al enviar/recibir. 

En este caso, el cliente y servidor tambien se encuentran unificados en un solo archivo llamado "Serv_Cli.py", que recibe como parametros 4 argumentos:

    python serv_cly.py IP_SERVIDOR_DESTINO PUERTO_DESTINO IP_CLIENTE PUERTO_CLIENTE

La diferencia radica fundamentalmente en los mensajes que se van a enviar, ya que estos se enviarán en formato JSON.
Los mensajes se convierten en diccionarios de Python antes de ser serializados en formato JSON usando json.dumps(). Al recibir los mensajes, se decodifican desde JSON a diccionarios de Python utilizando json.loads().

Creando contenedor en docker:
docker build . -t h5 -f H5/h5.dockerfile
docker login
docker tag h5 lucaslatessa/h5
docker push lucaslatessa/h5

Comandos ejecutados en la mv de google cloud:
docker login
docker pull lucaslatessa/h5
docker run --name h5 --rm -p 8080:8080 lucaslatessa/h5

