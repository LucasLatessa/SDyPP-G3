# Parte 2 - Integracion con Plataforma SDyPP Blockchain Distribuida

## Objetivo de la construcción de la blockchain.

Manejar transferencias entre usuarios (usuario A ; usuario B ; monto) de forma segura y asegurando que el contenido de la blockchain no puede ser alterado

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