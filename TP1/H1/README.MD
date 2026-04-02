# Hit #1
Elabore un código de servidor TCP para B que espere el saludo de A y lo responda.
Elabore un código de cliente TCP para A que se conecte con B y lo salude.

El archivo server.py representar a el nodo B, mientras que el archivo cliente.py representara al nodo A.
Se levanta el servidor desde la terminal usando docker, utilizando el comando "python server.py", con el host 0.0.0.0 (cualquiera) y el puerto 8081
Se realiza una peticion con el cliente (desde nuestra PC) usando

```bash
python cliente.py
```

donde este enviara el mensaje al servidor y recibira una respuesta.

## Comando para contenedores y gcloud

Creando contenedor en docker: 

```bash
docker build . -t h1 -f H1/h1.dockerfile 
docker login 
docker tag h1 lucaslatessa/h1 
docker push lucaslatessa/h1
```

### Comandos ejecutados en la mv de google cloud

```bash
sudo docker login 
sudo docker pull lucaslatessa/h1 
```

**Para visualizar el contenido en consola:**

```bash
sudo docker run -it --rm --name h1 -p 8081:8081 -p 10001:10001 lucaslatessa/h1 
```

**Para guarda en .txt:**

```bash
sudo docker run --rm --name h1 -p 8081:8081 -p 10001:10001 lucaslatessa/h1 >> logfileh1.txt 2>&1 & 
```

## Video explicativo
https://youtu.be/sz1YGw73vQ0