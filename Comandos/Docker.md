# Comandos Útiles de Docker

Esta guía contiene los comandos fundamentales para la construcción de imágenes, manejo de contenedores y publicación en Docker Hub.

## 🔐 Autenticación y Repositorios

**Iniciar sesión en Docker Hub:**
```bash
docker login
```

**Etiquetar una imagen existente (para subirla a un repo):**
```bash
docker tag ETIQUETA_ACTUAL NOMBRE_REPO/ETIQUETA_A_ASIGNAR
```

**Enviar una imagen al repositorio de Docker Hub:**
```bash
docker push NOMBRE_REPO/ETIQUETA_DENTRO_DE_REPO
```

---

## 🏗️ Construcción de Imágenes

**Construir una imagen a partir de un Dockerfile:**
*(El `.` al final indica que el contexto de construcción es el directorio actual)*
```bash
docker build . -t NOMBRE_TAG -f ARCHIVO_DOCKER.dockerfile
```

**Listar todas las imágenes locales:**
```bash
docker images
```

---

## 📦 Ejecución y Gestión de Contenedores

**Ejecutar una imagen y crear un contenedor:**
* `--rm`: Elimina el contenedor automáticamente al detenerlo.
* `--name`: Le asigna un nombre personalizado al contenedor.
* `-p`: Mapea los puertos (`PUERTO_HOST:PUERTO_CONTENEDOR`).
* `-d`: (Opcional) Ejecuta el contenedor en segundo plano (detached mode).
```bash
docker run --rm --name NOMBRE_CONTENEDOR -p PUERTO_HOST:PUERTO_DOCKER REPO/IMAGEN
```

**Listar los contenedores en ejecución:**
```bash
docker ps
```

**Listar TODOS los contenedores (incluso los detenidos):**
```bash
docker ps -a
```

**Conectarse a la terminal de un contenedor en ejecución:**
```bash
docker exec -it NOMBRE_CONTENEDOR /bin/sh
```
*(Nota: Si la imagen está basada en Ubuntu/Debian, podés usar `/bin/bash` en lugar de `/bin/sh`)*

---

## 🛑 Detención, Limpieza y Debugging (Extras)

**Detener un contenedor en ejecución:**
```bash
docker stop NOMBRE_CONTENEDOR
```

**Forzar la eliminación de un contenedor:**
```bash
docker rm -f NOMBRE_CONTENEDOR
```

**Eliminar una imagen local:**
```bash
docker rmi NOMBRE_IMAGEN_O_ID
```

**Ver los logs de un contenedor (ideal para debugear):**
```bash
docker logs NOMBRE_CONTENEDOR
```

**Limpieza total (System Prune):**
Elimina todos los contenedores detenidos, redes no utilizadas, imágenes colgantes (dangling) y cachés de construcción. ¡Útil para liberar espacio!
```bash
docker system prune
```

---

## 💡 Ejemplos Prácticos de Flujo de Trabajo

**1. Construir y subir una imagen:**
```bash
docker build . -t lucaslatessa/h3 -f h3/h3.dockerfile
docker push lucaslatessa/h3
```

**2. Levantar el contenedor y entrar a su consola:**
```bash
# Primero ejecutamos la imagen dándole un nombre al contenedor ("mi_contenedor_h2")
docker run -d --name mi_contenedor_h2 lucaslatessa/h2

# Luego nos conectamos al contenedor usando ese nombre
docker exec -it mi_contenedor_h2 /bin/sh
```