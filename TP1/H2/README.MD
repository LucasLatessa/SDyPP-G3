# Hit #2
Revise el código de A para implementar una funcionalidad que permita la reconexión y el envío del saludo nuevamente en caso de que el proceso B cierre la conexión, como por ejemplo, al ser terminado abruptamente. 

El servidor funciona de igual manera que el ejercicio anterior 
En el caso del cliente, se definen dos nuevas funciones: 
* Conectar = Encargado de realizar la conexion con el server que, si es rechazada, se reintenta reestablecer la conexion en 5 segundos 
* enviarsaludo = Envia la peticion al servidor cada 10 segundos 

En una terminal, para ejecutar el cliente utilizamos:

```bash
python cliente.py
```

## Comando para contenedores y gcloud 

Creando contenedor en docker:  

```bash
docker build . -t h2 -f H2/h2.dockerfile 
docker login 
docker tag h2 josuegaticaodato/h2 
docker push josuegaticaodato/h2 
```

### Comandos ejecutados en la mv de google cloud:

```bash
sudo docker login 
sudo docker pull josuegaticaodato/h2
```


**Para visualizar el contenido en consola:**

```bash
sudo docker run -it --rm --name h2 -p 8082:8082 -p 10002:10002 josuegaticaodato/h2 
Para guarda en .txt: sudo docker run --rm --name h2 -p 8082:8082 -p 10002:10002 josuegaticaodato/h2  >> logfileh2.txt 2>&1 & 
```

**Para guarda en .txt:**

```bash
sudo docker run --rm --name h2 -p 8082:8082 -p 10002:10002 josuegaticaodato/h2  >> logfileh2.txt 2>&1 & 
```

## Video explicativo 
https://youtu.be/eGd4lLGNlBU