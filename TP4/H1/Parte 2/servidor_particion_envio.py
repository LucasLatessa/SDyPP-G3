import os
from particionador import particionar_imagen
import sys
import cv2
import requests
import json
import numpy as np
from matplotlib import pyplot as plt

#Encargado de unir todas las imagenes (POR AHORA IMAGENES 2X2)
def unir_particiones(particiones_sobel):
    imagen_unida_horizontalmente = np.hstack(particiones_sobel[:2])
    imagen_unida_verticalmente = np.vstack([imagen_unida_horizontalmente, np.hstack(particiones_sobel[2:])])
    return imagen_unida_verticalmente

#Envia las particiones a los workers para que apliquen el filtro de sobel
def particionar_enviar_imagen(imagenes):
    HOST = "127.0.0.1"
    PORT = 9999

    particiones_sobel = []

    #Por cada porcion de imagen, envio un request al Worker para que le aplique ese filtro
    for imagen_particionada in imagenes:
        number = 0
        
        # Crear el objeto JSON para enviar
        json_data = {
            "id": number,
            "imagenes": imagen_particionada.tolist()
        }

        number += 1

        # Convertir el objeto JSON a una cadena JSON
        json_string = json.dumps(json_data)

        # Especificar los encabezados de la solicitud HTTP
        headers = {'Content-Type': 'application/json'}

        try:
            # Enviar la solicitud POST al Worker
            response = requests.post(f'http://{HOST}:{PORT}/sobel', data=json_string, headers=headers)

            #Obtengo la imagen filtrada y la guardo en un arreglo
            imagen_filtrada = response.json()["imagen"]
            imagen_np = np.array(imagen_filtrada,dtype=np.uint8)
            imagen_np = np.squeeze(imagen_np)
            particiones_sobel.append(imagen_np)

        #Manejo de errores
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")

    return particiones_sobel

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Como usar el programa: python servidor_particion_envio.py (ruta-imagen)")
        sys.exit(1)

    # Obtengo la ruta y cargo la imagen
    ruta_img = sys.argv[1]
    imagen = cv2.imread(ruta_img)

    # Obtener el nombre del archivo sin la extensión
    nombre_archivo = os.path.splitext(os.path.basename(ruta_img))[0]

    #Particiono las imagenes
    particiones = particionar_imagen(imagen)

    #Envio todas las particiones para que los workers apliquen sobel, y la guardo en un arreglo
    particiones_sobel = particionar_enviar_imagen(particiones)

    #Uno las particiones y guardo la imagen
    mi_imagen = unir_particiones(particiones_sobel)

    #Guardo la imagen
    cv2.imwrite(nombre_archivo + "_sobel.jpg", mi_imagen)
    print("Imagen filtrada!")