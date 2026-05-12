# Comandos Útiles de Kubernetes (kubectl)

Esta guía contiene los comandos fundamentales para desplegar, administrar y diagnosticar aplicaciones distribuidas en un clúster de Kubernetes.

## 🚀 1. Despliegue y Gestión de Recursos (Declarativo)

**Aplicar o actualizar una configuración desde un archivo YAML:**
*(Se usa para Deployments, Services, ConfigMaps, etc.)*
```bash
kubectl apply -f deployment.yaml
kubectl apply -f services.yaml
```

**Eliminar recursos definidos en un archivo YAML:**
```bash
kubectl delete -f services.yaml
```

**Eliminar un recurso específico por su nombre:**
```bash
kubectl delete pod NOMBRE_DEL_POD
kubectl delete deployment NOMBRE_DEL_DEPLOYMENT
```

---

## 🔍 2. Exploración y Monitoreo de Recursos

**Listar los Nodos del clúster (las máquinas físicas/virtuales):**
```bash
kubectl get nodes
```

**Listar los Pods (instancias de los contenedores):**
* `-w`: (Watch) Deja la consola abierta viendo los cambios en tiempo real.
* `-o wide`: Muestra más detalles, como la IP interna del Pod y en qué Nodo está corriendo.
```bash
kubectl get pods
kubectl get pods -o wide
```

**Listar los Deployments y Servicios:**
```bash
kubectl get deployment
kubectl get services
```

**Listar TODOS los recursos en el namespace actual (Pods, Services, Deployments, ReplicaSets):**
```bash
kubectl get all
```

---

## 🛠️ 3. Debugging y Diagnóstico (Crucial para Sistemas Distribuidos)

**Ver los detalles completos y eventos de un recurso:**
*(Útil cuando un Pod se queda en estado "Pending" o "CrashLoopBackOff")*
```bash
kubectl describe pod NOMBRE_DEL_POD
kubectl describe service NOMBRE_DEL_SERVICIO
kubectl describe deployment NOMBRE_DEL_DEPLOYMENT
```

**Ver los logs de un Pod específico:**
* `-f`: (Follow) Sigue mostrando los logs en vivo a medida que se generan.
```bash
kubectl logs NOMBRE_DEL_POD
kubectl logs -f NOMBRE_DEL_POD
```

**Abrir una terminal interactiva DENTRO de un Pod:**
*(El equivalente a `docker exec`. Ideal para probar conexión a bases de datos o ver variables de entorno)*
```bash
kubectl exec -it NOMBRE_DEL_POD -- /bin/sh
# O usar /bin/bash dependiendo de la imagen base
```

---

## 🌐 4. Redes y Exposición Local (Port Forwarding)

**Redirigir tráfico de tu máquina local a un Servicio en el clúster:**
*(Formato: PUERTO_LOCAL:PUERTO_CONTENEDOR)*
```bash
kubectl port-forward service/h3parte1-services 8080:5000
```

**Redirigir tráfico en un Namespace específico (ej. kube-system):**
* `-n`: Especifica el namespace.
```bash
kubectl port-forward service/h3parte1-services 8080:5000 -n kube-system
```

**Redirigir tráfico directamente a un Pod (para pruebas rápidas sin pasar por el Service):**
```bash
kubectl port-forward pod/NOMBRE_DEL_POD 8080:5000
```

---

## 📈 5. Escalamiento y Actualizaciones (Extras para Prácticas)

**Escalar manualmente la cantidad de réplicas de un Deployment:**
*(Ideal para probar balanceo de carga entre múltiples Pods)*
```bash
kubectl scale deployment NOMBRE_DEL_DEPLOYMENT --replicas=3
```

**Forzar el reinicio de todos los Pods de un Deployment:**
*(Útil si actualizaste una imagen en Docker Hub con el mismo tag "latest" y querés que K8s la vuelva a descargar)*
```bash
kubectl rollout restart deployment NOMBRE_DEL_DEPLOYMENT
```

Certificados
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.15.0/cert-manager.yaml
```
