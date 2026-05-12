# Hoja de trucos

#### Ver lista simple (si dice Running, todo bien)
kubectl get pods

#### Ver en tiempo real (ideal cuando acabas de hacer un deploy)
kubectl get pods -w

#### Ver detalles extra (en qué nodo está corriendo y su IP interna)
kubectl get pods -o wide

#### Ver TODOS los pods del sistema (incluidos los de Google y Nginx)
kubectl get pods -A

#### Ver qué está pasando dentro del contenedor
kubectl logs <NOMBRE-DEL-POD>

#### Ver los logs en vivo (como un tail -f)
kubectl logs -f <NOMBRE-DEL-POD>

#### Ver los logs de la vez anterior (si el pod se reinició y quieres saber por qué murió)
kubectl logs <NOMBRE-DEL-POD> --previous

#### La autopsia completa (muestra eventos de por qué no arranca o por qué no se programa)
kubectl describe pod <NOMBRE-DEL-POD>

#### Ver los servicios internos (ClusterIP)
kubectl get svc

#### Ver las reglas de entrada (Rutas /api, dominios, etc.)
kubectl get ingress

#### Puerta al Mundo (Ingress Controller)
Buscar la EXTERNAL-IP
kubectl get svc -n ingress-nginx

#### Certificados SSL (HTTPS)
#### Ver si el certificado está listo (Busca READY: True)
kubectl get certificate

#### Si falla, ver el estado del desafío (challenge)
kubectl get challenges

#### Ver el emisor del certificado
kubectl get clusterissuer

#### Pro Tip: Ahorra tiempo
Set-Alias -Name k -Value kubectl