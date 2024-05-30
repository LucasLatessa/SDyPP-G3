# Parte 2
Desarrolle este proceso de manera distribuida donde se debe partir la imagen en n pedazos, y asignar la tarea de aplicar la máscara a N procesos distribuidos. Después deberá unificar los resultados.

## Instrucciones 

1. Correr docker-compose.yaml (me tengo que posicioanr primero en la carpeta donde esta ubicado):

```
docker-compose up
```

Para dar de baja todo

```
docker-compose down
```

3. Realizar una peticion al Web server, siguiendo esta estructura:

```
POST localhost:5000/sobel
{
    "imagen": Imagen a aplicar el filtro
    "particion-x": Cantidad de particiones en X
    "particion-y": Cantidad de particiones en Y
}
```

Ejemplo

```
POST localhost:5000/sobel
{
    "imagen": Mirtha.jpg
    "particion-x": 3
    "particion-y": 3
}
```

Enviada la peticion, el servidor web devolvera un ID para consultar por el estado de la imagen

```
{
    "id": "bf6ad473-cf76-49c5-adcd-9ed134af0749",
    "message": "ID para consultar por la imagen"
}
```

Utilizaremos este ID para consultar al mismo servidor si la imagen ya fue procesada

```
POST localhost:5000/imagen/bf6ad473-cf76-49c5-adcd-9ed134af0749
```

# Parte 3
Mejore la aplicación del punto anterior para que, en caso de que un proceso distribuido (al que se le asignó parte de la imagen a procesar - WORKER) se caiga y no responda, el proceso principal detecte esta situación y pida este cálculo a otro proceso.

Esta situacion se soluciona modificando uno de los parametros del worker a la hora de suscribirse a las colas (ya esta agregado en la parte 2). Esa configuracion es la siguiente:

```
    ch.basic_ack(
        delivery_tag=method.delivery_tag
    )  # Tengo ACK, de esta forma si se da de baja un workers no pierdo los mensajes.
```

Si un worker toma una parte de la imagen de la cola pero no envia el ack, esto me dice que el worker no pudo aplicar el filtro/no esta en funcionando, entonces otro worker se encarga de realizar ese trabajo.
