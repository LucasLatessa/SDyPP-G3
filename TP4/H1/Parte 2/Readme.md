# Parte2 - Desarrolle este proceso de manera distribuida donde se debe partir la imagen en n pedazos, y asignar la tarea de aplicar la máscara a N procesos distribuidos. Después deberá unificar los resultados.
# Parte3 - Mejore la aplicación del punto anterior para que, en caso de que un proceso distribuido (al que se le asignó parte de la imagen a procesar - WORKER) se caiga y no responda, el proceso principal detecte esta situación y pida este cálculo a otro proceso.

## Instrucciones para aplicar el filtro de sobel particionando en 4 la imagen

1. Instalar las librerias utilizadsa:

```
pip install opencv-python numpy
```

2. Levantar servidores ( 9991-9994)

```
flask --app servidor-sobel.py run --port "puerto"
```

Ej.

```
flask --app servidor-sobel.py run --port 9991
```

3. Ejecutar cliente

```
python servidor_particion_envio.py "ruta-de-la-imagen"
```

Ej.

```
python servidor_particion_envio.py ./GASPI.png
```