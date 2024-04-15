import json
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

    datosTarea = {
        "operador" : request.json["operador"],
        "n1" : int(request.json["n1"]),
        "n2" : int(request.json["n2"])
    }

    #Paso a json los datos y agrego encabezados
    json_string = json.dumps(datosTarea)
    headers = {'Content-Type': 'application/json'}
    
    #Usando la API de docker para python, hago un pull de la imagen que me mando el usuario y levanto el contenedor
    client = docker.from_env()
    client.images.pull(imagen)
    container = client.containers.run(
        imagen,
        ports={'5000/tcp': 5000},
        network='prueba',
        detach=True)

    #Hago una espera de 5 segundos para que el contenedor se levante bien
    time.sleep(5) 

    container_ip=obtener_ip_contenedor(container.id,client,'prueba')
    container_ip=(container_ip[:-3])#truncamos los digitos de la ip
    # Envio POST al servidor de tarea utilizando la dirección IP del contenedor
    
    #res = requests.get('http://0.0.0.0:5000/status')

    #Envio POST al servidor de tarea
    res = requests.post(f'http://{container_ip}:5000/ejecutarTarea', data=json_string, headers=headers).json()

    # Doy de baja el contenedor
    container.stop()
    container.remove()

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
   