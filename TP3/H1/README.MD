# Hit #1
Cree una Instancia en la nube. 
Ahora agregue la creación de N instancias, siendo N un valor que se pasa en tiempo de ejecución.

## Instrucciones para comenzar a gestionar la infraestructura de GCloud

1. Inicializamos el directorio de trabajo Terraform con el siguiente comando

```
terraform init
```

2. Creado el estado inicial, creamos el plan de ejecucion. De esta forma, Terraform examina la configuracion en Gcloud con el estado actual para determinar que acciones debe tomar para alcanzar la configuracion deseada.

```
terraform plan
```

3. Por ultimo, ejecutamos apply para para aplicar los cambios propuestos por el plan de ejecucion a la infraestructura

```
terraform apply
```