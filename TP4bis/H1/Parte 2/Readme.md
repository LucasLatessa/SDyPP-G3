# Parte 1 
Desarrollar un proceso centralizado que tome una imagen, aplique la máscara, y genere un nuevo archivo con el resultado. 

## Instrucciones para aplicar el filtro de sobel

1. Instalar las librerias utilizadsa:

```
pip install opencv-python numpy
```

2. Rabbit

```
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.13-management
```

3. Redis

```
docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
```

2. Ejecutar el programa

```
python sobel-Parte1.py "ruta-de-la-imagen"
```

Ej.

```
python sobel.py Mirtha.jpg
```
