# HIT 2 - Sobel con offloading en la nube ;) para construir una base elástica (elástica):
Mismo objetivo de calcular sobel, pero ahora vamos a usar Terraform para construir nodos de trabajo cuando se requiera procesar tareas y eliminarlos al terminar. Recuerde que será necesario:
●	Instalar con #user_data las herramientas necesarias (java, docker, tools, docker).
●	Copiar ejecutable (jar, py, etc) o descargar imagen Docker (hub).
●	Poner a correr la aplicación e integrarse al cluster de trabajo.

El objetivo de este ejercicio es que ustedes puedan construir una arquitectura escalable (tipo 1, inicial) HÍBRIDA. Debe presentar el diagrama de arquitectura y comentar su decisión de desarrollar cada servicio y donde lo “coloca”.

## Instrucciones 

1. Correr el terraform correspondiente a la app (tendra Redis, Rabbit, Joiner, Spliter y WS)

```
terraform init
terraform plan
terraform apply -auto-aprove
```

Cuando se levanta la maquina, esta hara el docker compose de todos los servicios

2. Con la direccion IP que tienen la maquina app, se levanta los workers utilizando el terraform de Infra

```
terraform init
terraform plan
terraform apply -auto-aprove
```

Es necesario que el worker tenga esa direccion IP para que pueda suscribirse a la cola de mensajes de rabbit y conectarse a redis

3. En el caso de querer tener tu worker local, ejecuta worker.py, que esta en testWorkerLocal

```
python worker.py [IP-APP]
```

4. Realizar peticiones a la direccon IP para aplicar el filtro sobel

```
POST [IP-APP]:5000/sobel
{
    "imagen": Imagen a aplicar el filtro
    "particion-x": Cantidad de particiones en X
    "particion-y": Cantidad de particiones en Y
}
```

Ejemplo

```
POST [IP-APP]:5000/sobel
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
POST [IP-APP]:5000/imagen/bf6ad473-cf76-49c5-adcd-9ed134af0749
```