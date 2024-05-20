# HIT 3

## Sobel contenerizado asincrónico y escalable (BASE DE TP FINAL)

A diferencia del clúster anterior, la idea es que construya una infraestructura basada en la nube pero ahora con un enfoque diferente. 

Para ello, será necesario:

1.	Desplegar con terraform un cluster de Kubernetes (GKE). Este será el manejador de todos los recursos que vayamos a desplegar. Es decir, va a alojar tanto los servicios de infraestructura (rabbitMQ y Redis) como los componentes de las aplicaciones que vamos a correr (frontend, backend, split, joiner, etc). Este clúster tiene que tener la siguiente configuración mínima
    + a.Un nodegroup para alojar los servicios de infraestructura (rabbitmq, redis, otros)
    + b.Un nodegroup compartido para las aplicaciones del sistema (front, back, split, joiner)
    + c.Máquinas virtuales (fuera del cluster)  que se encarguen de las tareas de procesamiento / cómputo intensivo. 

2. Construir los pipelines de despliegue de todos los servicios.
    + Pipeline 1: El que construye el Kubernetes. 
    + Pipeline 1.1: El que despliega los servicios (base datos - Redis, sistema de colas - RabbitMQ)
    + Pipeline 1.2-1.N: De cada aplicación desarrollada (frontend, backend, split, join)
    + Pipeline 2: Despliegue de máquinas virtuales para construir los workers. Objetivo deseable: Que estas máquinas sean “dinámicas”.  
