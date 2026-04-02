# Hit #3
Modifique el código de B para que si el proceso A cierra la conexión (por ejemplo matando el proceso) siga funcionando 

En este caso, el cliente sigue igual que el ejercicio anterior. 
El servidor tiene que mantener abierto luego de terminar la conexion con cualquier nodo A, y esto se realiza aplicando un ciclo infinito para la apertura, peticion y cierre de la conexion 

En una terminal, para ejecutar el cliente utilizamos:

```bash
python cliente.py
```

## Comando para contenedores y gcloud

```bash
docker build . -t h3 -f H3/h3.dockerfile 
docker login 
docker tag h3 josuegaticaodato/h3 
docker push josuegaticaodato/h3 
```

### Comandos ejecutados en la mv de google cloud:

```bash
sudo docker login 
sudo docker pull josuegaticaodato/h3 
```

**Para visualizar el contenido en consola:**

```bash
sudo docker run -it --rm --name h3 -p 8083:8083 -p 10003:10003 josuegaticaodato/h3 
```

**Para guarda en .txt:**

```bash
sudo docker run --rm --name h3 -p 8083:8083 -p 10003:10003 josuegaticaodato/h3  >> logfileh3.txt 2>&1 & 
```

## Video explicativo 
https://youtu.be/FcBMjfBHOfQ