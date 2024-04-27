import json
import requests

#Informacion del servidor y la imagen a crear
HOST = "35.196.99.208"
PORT = 8080
IMAGEN = "josuegaticaodato/conversor"
#IMAGEN = "josuegaticaodato/tarea"

#JSON con los datos enviar 
"""datosTarea = {
    "imagen": IMAGEN,
    "operador": "*",
    "n1": 5000000000,
    "n2": 1000
}"""

datosTarea = {
    "imagen": IMAGEN,
    "valor":10,
    "unidad_origen":"pies",
    "unidad_destino":"metros"
}

#Creamos el json y el header de la peticion
json_string = json.dumps(datosTarea)
headers = {'Content-Type': 'application/json'}

#Enviamos la peticion
response = requests.post(f'http://{HOST}:{PORT}/getRemoteTask', data=json_string, headers=headers).json()

#Mostramos el resultado en pantalla
print(response)
