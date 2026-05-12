# Despliegue

## 0. Prerrequisitos
 - Tener Docker Desktop abierto.
 - Tener tus imágenes subidas a Docker Hub (v2).
 - Tener todos tus archivos YAML corregidos en la carpeta k8s.

## 1. Levantar todo con terraform

```
terraform init
terraform plan
terraform apply
```

## 2. Coneccion al cluster

```
gcloud container clusters get-credentials primary --region us-east4-b
```

## 3. Instalar cimientos (Ingress + Cert Manager)

```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml
```

## 4. Firewall (si no esta armada)

```
gcloud container clusters describe primary --region us-east4-a --format="value(privateClusterConfig.masterIpv4CidrBlock)"
```

Ve a Google Cloud Console:
* Navega a Red de VPC > Firewall.
* Busca la regla que creamos (ej: allow-master-to-webhook o crea una nueva).
* Edítala:
* Rangos de origen: Pega la IP que copiaste en el punto 1.
* Protocolos/Puertos: tcp:8443,9443,443,10250.
* Guarda.


##  5. Despliegue con kubernetes

###  5.1. Configurar el emisor de certificados
```
kubectl apply -f certificate.yaml
```

###  5.2. RabbitMQ y Redis
```
kubectl apply -f rabbit-services.yaml
kubectl apply -f redis-services.yaml
```

###  5.3. Coordinador
```
kubectl apply -f coordinador-services.yaml
```

###  5-4. Pool Manager
```
kubectl apply -f pool-manager-services.yaml
```

###  5.5. Levantar el Frontend (React/Vite)
```
kubectl apply -f front-services.yaml
```

###  5.6. Acceso externo
```
kubectl apply -f ingress.yaml
```

##  6. DNS (Squarespace)

```
kubectl get svc -n ingress-nginx
```

(Copiar la EXTERNAL-IP del ingress-nginx-controller).

En Squarespace:
* Cambia el registro @ (A) -> Pega la Nueva IP.
* Cambia el registro www (A) -> Pega la Nueva IP.

## 7. Verificacion

```
kubectl get certificate
```

Si dice READY: True, abre tu navegador en https://unlucoin.info
