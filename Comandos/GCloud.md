# Comandos Útiles de Google Cloud (gcloud)

Esta guía contiene los comandos necesarios para aprovisionar infraestructura, gestionar redes y administrar Máquinas Virtuales (VMs) en Google Cloud Platform.

## 🔑 1. Autenticación y Configuración Inicial

Antes de empezar, asegurate de estar logueado y apuntando al proyecto correcto.

**Iniciar sesión en Google Cloud:**
```bash
gcloud auth login
```

**Ver la configuración actual (cuenta, proyecto, zona por defecto):**
```bash
gcloud config list
```

**Setear el proyecto de trabajo:**
```bash
gcloud config set project ID_DE_TU_PROYECTO
```

---

## 🌐 2. Redes, Direcciones IP y Firewall

**Crear una dirección IP pública estática:**
*(Ideal para que la IP de tu servidor no cambie si la máquina se reinicia)*
```bash
gcloud compute addresses create instance-public-ip --region=us-east1
```

**Crear reglas de Firewall:**
* `--direction=INGRESS`: Tráfico de entrada.
* `--action=ALLOW`: Permitir el tráfico.
* `--source-ranges=0.0.0.0/0`: Desde cualquier IP de origen.

```bash
# Permitir tráfico HTTP (Puerto 80)
gcloud compute firewall-rules create allow-http --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:80 --source-ranges=0.0.0.0/0

# Permitir conexiones SSH (Puerto 22)
gcloud compute firewall-rules create allow-ssh --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:22 --source-ranges=0.0.0.0/0

# Permitir tráfico para aplicación Node (Puerto 8080)
gcloud compute firewall-rules create appnode --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:8080 --source-ranges=0.0.0.0/0

# Permitir rango de puertos para contenedores Docker (8081 al 9000)
gcloud compute firewall-rules create docker-8081-9000 --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:8081-9000 --source-ranges=0.0.0.0/0
```

---

## 🖥️ 3. Creación y Gestión de Máquinas Virtuales (VMs)

**Listar todas las instancias actuales (para ver sus IPs y estados):**
```bash
gcloud compute instances list
```

**Crear una Máquina Virtual:**
* `--preemptible`: Instancia más barata pero que Google puede apagar si necesita recursos (ideal para pruebas, NO para producción final).
* `--metadata-from-file user-data=...`: Ejecuta un script de inicio (cloud-init) al levantar la VM.
* `--address`: Le asigna la IP estática que creaste antes.

```bash
gcloud compute instances create vm1 \
    --machine-type=e2-micro \
    --preemptible \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --tags=http-server \
    --metadata="ssh-keys=$(cat ./id_rsa_example.pub)" \
    --metadata-from-file user-data=../userdata/scriptvm1.sh \
    --zone="us-east1-b" \
    --address=instance-public-ip
```

**Apagar una instancia (deja de cobrar CPU/RAM, pero cobra disco):**
```bash
gcloud compute instances stop vm1 --zone=us-east1-b
```

**Encender una instancia detenida:**
```bash
gcloud compute instances start vm1 --zone=us-east1-b
```

**Eliminar una instancia permanentemente:**
```bash
gcloud compute instances delete vm1 --zone=us-east1-b
```

---

## 🔌 4. Conexión SSH, Ejecución Remota y Transferencia

**Conectarse por SSH a la VM:**
```bash
gcloud compute ssh vm1 --zone=us-east1-b --ssh-key-file=./id_rsa_example
```

**Ejecutar un comando remoto vía SSH (sin entrar a la consola interactiva):**
*(Útil para automatizar deploys o ver logs rápidos)*
```bash
# Ver logs del script de inicio (cloud-init)
gcloud compute ssh vm1 --zone=us-east1-b --ssh-key-file=./id_rsa_example --command "cat /var/log/cloud-init-output.log"

# Levantar un contenedor de Docker directamente
gcloud compute ssh vm1 --zone=us-east1-b --ssh-key-file=./id_rsa_example --command "sudo docker run --network=prueba --rm --name spweb -v /var/run/docker.sock:/var/run/docker.sock -p 8080:8080 josuegaticaodato/servidorweb"
```

**Copiar archivos desde tu PC a la VM (gcloud SCP):**
*(Muy útil para subir tu código o archivos de configuración)*
```bash
gcloud compute scp ./mi-archivo.txt vm1:~/ --zone=us-east1-b --ssh-key-file=./id_rsa_example
```

---

## 📜 5. Logs y Auditoría

**Habilitar la API de Logging:**
```bash
gcloud services enable logging.googleapis.com
```

**Leer logs específicos de la creación de instancias:**
```bash
gcloud logging read "resource.type=gce_instance AND protoPayload.methodName=beta.compute.instances.insert"
```