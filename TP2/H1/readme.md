# Hit #1
Implemente un servidor que resuelva “tareas genéricas” o “pre-compiladas”. Para ello, hay un conjunto de acciones de diseño y arquitectura que deben respetarse

Se construyo el servidor web utilizando Python con el framework Flask, que permite crear aplicaciones web.
Nuestro servidor tiene el metodo ejecutarTareaRemota(), vinculado al endpoint /getRemoteTask, para recibir las peticiones del cliente.
Este recibe el json enviado por el cliente, separando la imagen de los datos en si de la tarea a realizar, para poder crear el contenedor encargado de realizar la tarea, que sera nuestro tarea.py, encargado de realizar una tarea generica, en nuestro caso, una operacion matematica basica.
Una vez levantado el contenedor y escuchando en el puerto 5000 del contenedor, el servidor le envia la peticion para obtener como resultado la respuesta a la tarea y devolverla al cliente.

## Comando para contenedores y gcloud

Creando contenedor en docker:

``` 
docker build . -t josuegaticaodato/servidorweb -f servidor.dockerfile
```

Pusheando servidor web a docker hub:

``` 
docker push josuegaticaodato/servidorweb
```


## Comandos ejecutados en la mv de google cloud:

Pull al servidor web:

```
docker pull josuegaticaodato/servidorweb
```

Creacion de la red para comunicar los contenedores

```
docker network create --attachable prueba
```

Ejecucion del servidor web

```
docker run --network=prueba --rm --name spweb -v /var/run/docker.sock:/var/run/docker.sock -p 8080:8080 josuegaticaodato/servidorweb
```

Para matar todos los contenedores

```
docker stop $(docker ps -a -q)
```

## Direccion para realizar peticiones:

### 35.196.99.208:8080

Datos JSON a enviar 

```
{
    "imagen":imagen de docker a levantar para realizar la tarea, en nuestro caso "josuegaticaodato/tarea",
    "operador": Simbolo de un operador matematico, puede ser: +, -, * o /,
    "n1":numero entero a operar,
    "n2":numero entero a operar
}
```

Ejemplo:

```
{
    "imagen":"josuegaticaodato/tarea",
    "operador": "*",
    "n1":50,
    "n2":100000
}
```

## Video explicativo
https://youtu.be/_GMM6e_9xYk <br/>
https://youtu.be/e_KLwT-kzpU (actualizado)
