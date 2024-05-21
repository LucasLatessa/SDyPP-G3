# HIT 2 

## Sobel con offloading en la nube ;) para construir una base elástica (elástica):

Mismo objetivo de calcular sobel, pero ahora vamos a usar Terraform para construir nodos de trabajo cuando se requiera procesar tareas y eliminarlos al terminar. Recuerde que será necesario:
●	Instalar con #user_data las herramientas necesarias (java, docker, tools, docker).
●	Copiar ejecutable (jar, py, etc) o descargar imagen Docker (hub).
●	Poner a correr la aplicación e integrarse al cluster de trabajo.

El objetivo de este ejercicio es que ustedes puedan construir una arquitectura escalable (tipo 1, inicial) HÍBRIDA. Debe presentar el diagrama de arquitectura y comentar su decisión de desarrollar cada servicio y donde lo “coloca".

## Instrucciones para aplicar el filtro de sobel particionando en N la imagen

1. Instalar las librerias utilizadsa:

```
pip install -r requirements.txt
pip install dda-python-terraform

```

2. Ejecutar cliente

```
python servidor_particion_envio.py "ruta-de-la-imagen" "cantidad_particiones_x" "cantidad_particiones_y"
```

Ej.

```
python servidor_particion_envio.py ./GASPI.png 2 3
```

## Funcionamiento

1. Una vez recibida la imagen y la cantidad de particiones en X e Y a aplicarse, se crean las instancias necesarias usando terraform, encargadas de aplicar el filtro de sobel a cada particion

2. Luego, se realiza la particion de la imagen y se procede a enviarle cada pedazo a un worker, que estaran levantandos corriendo un contenedor Docker que tenga el filtro de sobel (endpoint: /sobel)
    Cada vez que un worker no pudo resolver la solicitud, ya sea porque se vencio el tiempo de espera o esta caido, el ws procede a enviarle la misma peticiom a otro worker

3. Recibidas todas las partes, se procede a unir todos los fragmentos y guardar la imagen en la maquina.
