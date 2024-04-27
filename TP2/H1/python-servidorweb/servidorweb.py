import json
import random
import time
import docker
import requests
from flask import Flask, request 

app = Flask(__name__)

#Ruta que el cliente va a realizar las peticiones
@app.route(rule="/getRemoteTask", methods=["POST"])
def ejecutarTareaRemota():
    #Obtengo la imagen y armo los datos para realizar la tarea
    imagen = request.json["imagen"]

    #Obtengo el nombre de la imagen, que va a ser igual que el endpoint
    partes = imagen.split('/')
    endpoint = partes[-1]

    #Paso a json los datos y agrego encabezados
    request_data = request.json
    json_string = json.dumps(request_data)
    headers = {'Content-Type': 'application/json'}

    #Asigno un puerto random
    numero_puerto = random.randint(5000,6000)
    
    #Usando la API de docker para python, hago un pull de la imagen que me mando el usuario y levanto el contenedor
    client = docker.from_env()
    client.images.pull(imagen)
    container = client.containers.run(
        imagen,
        environment={"PORT": str(numero_puerto)},  # Pasar el número de puerto como variable de entorno
        ports={f'{numero_puerto}/tcp': numero_puerto},
        network='prueba',
        detach=True)

    
    try:
        #Hago una espera de 5 segundos para que el contenedor se levante bien
        time.sleep(5) 

        container_ip=obtener_ip_contenedor(container.id,client,'prueba')
        container_ip=(container_ip[:-3])#truncamos los digitos de la ip
        # Envio POST al servidor de tarea utilizando la dirección IP del contenedor
        
        #res = requests.get('http://0.0.0.0:5000/status')

        #Envio POST al servidor de tarea
        res = requests.post(f'http://{container_ip}:{numero_puerto}/{endpoint}', data=json_string, headers=headers).json()

        # Doy de baja el contenedor
        container.stop()
        container.remove()
    except Exception:
        res = "El servidor no pudo resolver la tarea"

    #Devuelvo el resultado de la tare
    return res

#Ruta para saber el estado del servidor web
@app.route(rule="/status", methods=["GET"])
def status():
    data = {
        "status": "Ok"
    }
    print(data)
    return data

def obtener_ip_contenedor(nombre_cont,client, red):
    info_red=client.networks.get(red).attrs
    return info_red['Containers'][nombre_cont]['IPv4Address']

#Ejecucion

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=8080) 
   