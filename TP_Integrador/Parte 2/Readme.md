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

1. Levantar docker-compose con servicios (Rabbit y Redis). Ir a la carpeta de Parte 2/Services.

```
docker-compose up
```

2. Levanto el coordinador desde la carpeta del coordinador (Parte 2/Coordinador)

```
python app.py
```

3. Levantar el worker (CPU). Desde Parte 2/Worker-cpu

```
python worker_cpu.py
```

3. Levantar el worker (GPU).

```
python worker_gpu.py
```

## TEST

Correr test de worker cpu (Worker-cpu\test.py)
```
python test.py --start 1 --end 100000000 --prefix 000000 --hash-val apprew --inclusive
```

ssh-keygen -t rsa -b 4096 -m PEM -f ./unlucoin_priv
ssh-keygen -f ./unlucoin_priv.pub -e -m PEM > unlucoin_pub.pem