# Parte 2-3 
Desarrolle este proceso de manera distribuida donde se debe partir la imagen en n pedazos, y asignar la tarea de aplicar la máscara a N procesos distribuidos. Después deberá unificar los resultados.
Mejore la aplicación del punto anterior para que, en caso de que un proceso distribuido (al que se le asignó parte de la imagen a procesar - WORKER) se caiga y no responda, el proceso principal detecte esta situación y pida este cálculo a otro proceso.

## Instrucciones para aplicar el filtro de sobel

1. Instalar las librerias utilizadsa:

```
pip install opencv-python numpy flask redis pika
```

2. Correr Rabbit

```
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management
```

3. Correr Redis

```
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

4. Levantar los workers

```
python worker-Sobel.py
```

5. Levantar Web Server

```
python webServer.py
```

6. Realizar una peticion al Web server, siguiendo esta estructura:

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