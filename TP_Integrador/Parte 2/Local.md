# Despliegue local de TP_Integrador

El entorno local está compuesto por:

- **Redis Stack**: persistencia de la blockchain y Redis Insight.
- **RabbitMQ**: colas de transacciones y tareas, con interfaz de administración.
- **Coordinador**: API Flask servida con Gunicorn.
- **Pool Manager**: distribución de tareas hacia los workers.
- **Worker CPU**: resolución local de desafíos Proof of Work.
- **Frontend**: aplicación React servida por Nginx.

## 1. Prerrequisitos

Verificar:

```powershell
docker version
docker compose version
```

## 2. Ubicación del proyecto

Todos los comandos principales deben ejecutarse desde `TP_Integrador/Parte 2`:

Validar la configuración de Compose antes de levantarla:

```powershell
docker compose -p tp-integrador config
```

El nombre `tp-integrador` identifica el proyecto Compose. Usarlo siempre evita mezclar esta instalación con otra.

## 3. Construir la imagen del worker CPU

El worker CPU se construye antes de levantar el stack porque el `pool_manager` utiliza la imagen `sdyp-worker-cpu:latest`.

```powershell
docker build `
  --file Worker-cpu/Dockerfile `
  --build-arg RABBIT_USER=grupo03 `
  --build-arg RABBIT_PASS=grupo03 `
  --tag sdyp-worker-cpu:latest `
  .
```

Comprobar que la imagen existe:

```powershell
docker image ls sdyp-worker-cpu
```

## 4. Levantar los servicios principales

Este comando construye las imágenes locales del coordinador, pool manager y frontend, descarga Redis y RabbitMQ si hace falta, crea la red y arranca los contenedores en segundo plano:

```powershell
docker compose -p tp-integrador up --build -d
```

Ver el estado:

```powershell
docker compose -p tp-integrador ps
```

## 5. Levantar el worker CPU

El worker debe estar en la misma red Docker que el coordinador y RabbitMQ. El nombre de la red es `tp-integrador_default` porque el proyecto Compose se llama `tp-integrador`.

```powershell
docker run -d `
  --name worker-cpu-local `
  --network tp-integrador_default `
  -e RABBIT_HOST=rabbitmq `
  -e RABBIT_PORT=5672 `
  -e RABBIT_USER=grupo03 `
  -e RABBIT_PASS=grupo03 `
  -e ENDPOINT_COORDINADOR=http://coordinador:5000/tarea_worker `
  -e COORDINADOR_URL=http://coordinador:5000 `
  -e WORKER_ID=worker-cpu-local `
  sdyp-worker-cpu:latest
```

Comprobar el worker:

```powershell
docker ps --filter "name=worker-cpu-local"
docker logs --tail 40 worker-cpu-local
```

Si el contenedor ya existe y el comando devuelve un conflicto de nombre, iniciarlo con:

```powershell
docker start worker-cpu-local
```

Si se construyó una imagen nueva, eliminar el contenedor anterior y crearlo nuevamente:

```powershell
docker rm -f worker-cpu-local
docker run -d `
  --name worker-cpu-local `
  --network tp-integrador_default `
  -e RABBIT_HOST=rabbitmq `
  -e RABBIT_PORT=5672 `
  -e RABBIT_USER=grupo03 `
  -e RABBIT_PASS=grupo03 `
  -e ENDPOINT_COORDINADOR=http://coordinador:5000/tarea_worker `
  -e COORDINADOR_URL=http://coordinador:5000 `
  -e WORKER_ID=worker-cpu-local `
  sdyp-worker-cpu:latest
```

## 6. URLs locales

| Servicio            | URL                      | Credenciales                                                            |
| ------------------- | ------------------------ | ----------------------------------------------------------------------- |
| Frontend            | <http://localhost:8080>  | No requiere                                                             |
| API del coordinador | <http://localhost:5000>  | No requiere                                                             |
| RabbitMQ Management | <http://localhost:15672> | `grupo03` / `grupo03`                                                   |
| Redis Insight       | <http://localhost:8001>  | Puede requerir configurar la conexión a `redis:6379` o `localhost:6379` |
| Redis               | `localhost:6379`         | Password `grupo03`                                                      |

## 7. Pruebas básicas

### 7.1 Estado del coordinador

```powershell
Invoke-RestMethod http://localhost:5000/status
```

### 7.2 Prefijo de minería

```powershell
Invoke-RestMethod http://localhost:5000/prefijo
```

### 7.3 Blockchain almacenada

```powershell
Invoke-RestMethod http://localhost:5000/blockchain
```

Al comenzar puede devolver una lista vacía o la cadena existente en Redis.

### 7.4 RabbitMQ

Abrir <http://localhost:15672> e ingresar:

```text
Usuario: grupo03
Password: grupo03
```

En la sección de colas se pueden observar las colas creadas por el coordinador, el pool manager y el worker.

### 7.5 Frontend

Abrir <http://localhost:8080> en el navegador.

### 7.6 Prueba de una transacción

El endpoint es:

```text
POST http://localhost:5000/transaccion
```

La transacción debe respetar el formato que valida la aplicación. Para una transacción `TX`, se requieren `data`, `type` y `sign`, y dentro de `data` deben existir `monto`, `origen` y `destino`.

Ejemplo de estructura:

```json
{
  "type": "TX",
  "data": {
    "monto": 10,
    "origen": "CLAVE_PUBLICA_DEL_ORIGEN",
    "destino": "CLAVE_PUBLICA_DEL_DESTINO"
  },
  "sign": "FIRMA_BASE64"
}
```

La aplicación también valida las claves y la firma. Por eso un JSON inventado puede devolver `400`; eso indica que la API recibió la petición pero rechazó la transacción por validación.

Desde PowerShell, usando un archivo `transaccion.json` válido:

```powershell
Invoke-RestMethod `
  -Uri http://localhost:5000/transaccion `
  -Method Post `
  -ContentType "application/json" `
  -Body (Get-Content .\transaccion.json -Raw)
```

Luego observar el flujo en los logs:

```powershell
docker logs -f worker-cpu-local
```

## 8. Logs

Logs de todos los servicios Compose:

```powershell
docker compose -p tp-integrador logs -f
```

Logs de un servicio específico:

```powershell
docker compose -p tp-integrador logs -f coordinador
docker compose -p tp-integrador logs -f pool_manager
docker compose -p tp-integrador logs -f redis
docker compose -p tp-integrador logs -f rabbitmq
docker compose -p tp-integrador logs -f frontend
```

Mostrar solo las últimas líneas:

```powershell
docker compose -p tp-integrador logs --tail 100 coordinador
docker logs --tail 100 worker-cpu-local
```

Ver timestamps:

```powershell
docker compose -p tp-integrador logs -f --timestamps coordinador
```

Salir de la vista de logs sin detener contenedores: presionar `Ctrl+C`.

Para inspeccionar errores recientes:

```powershell
docker ps -a
docker compose -p tp-integrador ps -a
docker inspect worker-cpu-local
```

## 9. Problemas frecuentes

### El puerto ya está ocupado

Ver qué proceso usa un puerto:

```powershell
Get-NetTCPConnection -LocalPort 5000,6379,8080,8001,15672,5672 -ErrorAction SilentlyContinue
```

### El worker no conecta a RabbitMQ

Comprobar que RabbitMQ está activo:

```powershell
docker compose -p tp-integrador ps rabbitmq
docker logs --tail 100 rabbitmq
```

Comprobar que el worker usa la red correcta:

```powershell
docker inspect worker-cpu-local --format '{{json .NetworkSettings.Networks}}'
```

Debe aparecer `tp-integrador_default`. Si aparece otra red, eliminar y recrear el worker con el comando de la sección 5.

### El coordinador reinicia

```powershell
docker compose -p tp-integrador ps coordinador
docker compose -p tp-integrador logs --tail 150 coordinador
```

El coordinador depende de RabbitMQ y Redis. Confirmar que ambos están activos y que las variables apuntan a los nombres Docker `rabbitmq` y `redis`, no a `localhost`.

### El frontend no ve cambios

Reconstruir la imagen:

```powershell
docker compose -p tp-integrador build --no-cache frontend
docker compose -p tp-integrador up -d frontend
```

### El worker ya existe

```powershell
docker rm -f worker-cpu-local
docker run -d `
  --name worker-cpu-local `
  --network tp-integrador_default `
  -e RABBIT_HOST=rabbitmq `
  -e RABBIT_PORT=5672 `
  -e RABBIT_USER=grupo03 `
  -e RABBIT_PASS=grupo03 `
  -e ENDPOINT_COORDINADOR=http://coordinador:5000/tarea_worker `
  -e COORDINADOR_URL=http://coordinador:5000 `
  -e WORKER_ID=worker-cpu-local `
  sdyp-worker-cpu:latest
```

## 10. Detener temporalmente

Para detener los servicios sin eliminar los contenedores:

```powershell
docker compose -p tp-integrador stop
docker stop worker-cpu-local
```

Para iniciarlos nuevamente:

```powershell
docker compose -p tp-integrador start
docker start worker-cpu-local
```

## 11. Dar de baja el entorno

Para detener y eliminar los contenedores Compose y la red del proyecto:

```powershell
docker rm -f worker-cpu-local 2>$null
docker compose -p tp-integrador down
```

Comprobar que no queden contenedores del proyecto:

```powershell
docker ps -a --filter "name=worker-cpu-local"
docker compose -p tp-integrador ps -a
```

## 12. Eliminar imágenes

Las imágenes son independientes de los contenedores. Se pueden conservar para levantar más rápido o eliminar para liberar espacio.

Listar imágenes relevantes:

```powershell
docker image ls
```

Listar las imágenes administradas por Compose:

```powershell
docker compose -p tp-integrador images
```

Eliminar la imagen del worker:

```powershell
docker image rm sdyp-worker-cpu:latest
```

Eliminar las imágenes construidas por Compose, usando los nombres que muestre `docker compose images`:

```powershell
docker image rm <imagen-coordinador>:latest
docker image rm <imagen-pool-manager>:latest
docker image rm <imagen-frontend>:latest
```

Si existen contenedores detenidos que todavía usan esas imágenes, eliminarlos primero:

```powershell
docker compose -p tp-integrador down --remove-orphans
docker rm -f worker-cpu-local 2>$null
```

Limpiar únicamente imágenes sin etiqueta o no referenciadas:

```powershell
docker image prune
```

Limpiar todas las imágenes que no estén siendo usadas por ningún contenedor:

```powershell
docker image prune -a
```

`docker image prune -a` puede eliminar imágenes de Redis, RabbitMQ u otros proyectos. Ejecutarlo solo si se desea una limpieza general de Docker.

## 13. Limpieza completa del proyecto

Este procedimiento elimina el worker, contenedores, red e imágenes construidas del stack. Primero listar las imágenes para verificar sus nombres:

```powershell
docker rm -f worker-cpu-local 2>$null
docker compose -p tp-integrador down --remove-orphans
docker compose -p tp-integrador images
```

Después eliminar las imágenes que aparezcan en la lista, incluyendo `sdyp-worker-cpu:latest` si ya no se necesita:

```powershell
docker image rm sdyp-worker-cpu:latest
```

Para volver a desplegar desde cero:

```powershell
docker compose -p tp-integrador build --no-cache
docker compose -p tp-integrador up -d
```

Luego recrear el worker CPU con el comando de la sección 5.

## 14. Comandos de referencia rápida

```powershell
# Ir al proyecto TP_Integrador\Parte 2"

# Levantar todo
 docker compose -p tp-integrador up --build -d

# Levantar worker
 docker start worker-cpu-local

# Estado
 docker compose -p tp-integrador ps
 docker ps

# Logs
 docker compose -p tp-integrador logs -f
 docker logs -f worker-cpu-local

# API
 Invoke-RestMethod http://localhost:5000/status

# Detener
 docker stop worker-cpu-local
 docker compose -p tp-integrador stop

# Eliminar contenedores y red
 docker rm -f worker-cpu-local 2>$null
 docker compose -p tp-integrador down
```
