# HIT 3 - Sobel contenerizado asincrónico y escalable (BASE DE TP FINAL) 

A diferencia del clúster anterior, la idea es que construya una infraestructura basada en la nube pero ahora con un enfoque diferente. 

Para ello, será necesario:
1.	Desplegar con terraform un cluster de Kubernetes (GKE). Este será el manejador de todos los recursos que vayamos a desplegar. Es decir, va a alojar tanto los servicios de infraestructura (rabbitMQ y Redis) como los componentes de las aplicaciones que vamos a correr (frontend, backend, split, joiner, etc). Este clúster tiene que tener la siguiente configuración mínima
a.	Un nodegroup para alojar los servicios de infraestructura (rabbitmq, redis, otros)
b.	Un nodegroup compartido para las aplicaciones del sistema (front, back, split, joiner)
c.	Máquinas virtuales (fuera del cluster)  que se encarguen de las tareas de procesamiento / cómputo intensivo. 

2.	Construir los pipelines de despliegue de todos los servicios.
    ●	Pipeline 1: El que construye el Kubernetes. 
    ○	Pipeline 1.1: El que despliega los servicios (base datos - Redis, sistema de colas - RabbitMQ)
    ○	Pipeline 1.2-1.N: De cada aplicación desarrollada (frontend, backend, split, join)
    ●	Pipeline 2: Despliegue de máquinas virtuales para construir los workers. Objetivo deseable: Que estas máquinas sean “dinámicas”.  

## Instrucciones usando Github Actions 

1. Para levantar toda la infraestructura de trabajo, puede hacerse a traves de un commit comenzando con la palabra '(go)' para que comienzen a correr los github actions, encarngados de levantar la infraestructura, kubernetes, las aplicaciones y los workers.

```
git add .
git commit -m "(go) [cualquier texto]"
git push
```

## Diagrama y explicacion de funcionamiento

![DiagramaSDyPP drawio](https://github.com/LucasLatessa/SDyPP-G3/assets/63746351/fc63ccdb-1e8b-46ad-b8e1-048417848650)

Siguiendo la misma ciclo de peticion/respuesta que el TP, pero entra el juego el uso de kubernetes para el manejo de los contenedores y la construccion del cluster.
Se realiza la peticion a un Web Server que sera del tipo Load Balancer, que recibira los parametros y la imagen para enviarsela al spliter, encargado de dividir las imagenes y enviarlas a la cola de RabbitMQ.

Los workers, que estan fuera del clusters de Kubernetes, estaran conectados a Rabbit y Redis (por eso es necesario que ambos sean LoadBalancer) para aplicar el filtro de sobel a las partes que estan en la cola y enviarlo a la base de datos.

El cliente realizara otra peticion al web server consultado por el estado de la imagen, haciendo que el joiner realice la union de todas las partes de la imagen que se le hayan aplicado sobel, para poder devolverselo al cliente.

## Peticiones para aplicar el filtro de sobel (IP Actual: 34.48.79.150)

```
POST [IP Actual]:5000/sobel
{
    "imagen": Imagen a aplicar el filtro
    "particion-x": Cantidad de particiones en X
    "particion-y": Cantidad de particiones en Y
}
```

Ejemplo

```
POST [IP Actual]:5000/sobel
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
POST [IP Actual]:5000/imagen/bf6ad473-cf76-49c5-adcd-9ed134af0749
```