# Parte 2 - Integracion con Plataforma SDyPP Blockchain Distribuida

## Objetivo de la construcción de la blockchain.

Manejar transferencias entre usuarios de forma segura y asegurando que el contenido de la blockchain no puede ser alterado

## [Documentacion](https://docs.google.com/document/d/1-SNHJAbgMf1UBWImzGXjx7LE27BzxWo0tj-dMkY2ZgA/edit?usp=sharing)

## [Diagrama](https://miro.com/welcomeonboard/T3FBeFNHSDZ3ajRaSlNDQ3lmOHJxMHY5cTlPV3F5aGZjUlYrR0d0UkFnMVFvZVhvT1hNQmF3R3cwMW9DbnJJK2FRMjBrcWVtU2JOdGlGY2doYTl1dG4zOHVtN0x0ZmJBbm9oYWV6MkNxWTkxSFlDdStLYnFIejdFbURFZWNLUS90R2lncW1vRmFBVnlLcVJzTmdFdlNRPT0hdjE=?share_link_id=119593625078)

## Estructura del Repositorio

```text
📦 Parte 2
 ┣ 📂 Coordinador
 ┣ 📂 K8s
 ┣ 📂 Services
 ┣ 📂 Terraform
 ┣ 📂 Worker--gpu
 ┣ 📂 Worker-cpu
 ┗ 📜 README.md
```

## Levantar en local

1. Ubicarse en la carpeta de Parte 2.

```powershell
cd "TP_Integrador\Parte 2"
```

2. Construir la imagen del worker CPU. El pool manager usa Kubernetes en producción, por lo que en local el worker se inicia manualmente.

```powershell
docker build `
	--file Worker-cpu/Dockerfile `
	--build-arg RABBIT_USER=grupo03 `
	--build-arg RABBIT_PASS=grupo03 `
	--tag sdyp-worker-cpu:latest `
	.
```

3. Levantar Redis, RabbitMQ, el coordinador, el pool manager y el frontend:

```powershell
docker compose -p tp-integrador up --build -d
```

4. Levantar el worker CPU en la misma red Docker:

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

Servicios disponibles:

| Servicio            | URL                    |
| ------------------- | ---------------------- |
| Frontend            | http://localhost:8080  |
| API del coordinador | http://localhost:5000  |
| RabbitMQ Management | http://localhost:15672 |
| Redis Insight       | http://localhost:8001  |

Credenciales locales de RabbitMQ:

```text
Usuario: grupo03
Password: grupo03
```

Verificar el coordinador:

```powershell
Invoke-RestMethod http://localhost:5000/status
```

Ver logs:

```powershell
docker compose -p tp-integrador logs -f coordinador
docker compose -p tp-integrador logs -f pool_manager
docker logs -f worker-cpu-local
```

Para detener el entorno:

```powershell
docker rm -f worker-cpu-local
docker compose -p tp-integrador down
```

### Alternativa: worker CPU con Python

También se puede ejecutar el worker desde el host. Desde `Parte 2/Worker-cpu`, instalar `pika`, `requests` y `python-dotenv`, configurar `RABBIT_HOST=localhost`, `RABBIT_USER=grupo03`, `RABBIT_PASS=grupo03` y `COORDINADOR_URL=http://localhost:5000`, y ejecutar:

```powershell
python worker_cpu.py
```

## TEST

Correr test de worker cpu (Worker-cpu\test.py)

```
python test.py --start 1 --end 100000000 --prefix 000000 --hash-val apprew --inclusive
```

ssh-keygen -t rsa -b 4096 -m PEM -f ./unlucoin
ssh-keygen -f ./unlucoin_priv.pub -e -m PEM > unlucoin_pub.pem
