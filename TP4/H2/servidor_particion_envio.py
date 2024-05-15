import os
from funciones import particionar_imagen, unir_particiones
import sys
import cv2
import requests
import json
import numpy as np

#Envia las particiones a los workers para que apliquen el filtro de sobel
def particionar_enviar_imagen(imagenes):
    HOST = "127.0.0.1"
    PORT = [9991,9992,9993,9994] #Puertos donde estaran los workers

    #Aqui se guardan las particiones que envien los workers
    particiones_sobel = []

    #Manejo de workers en circulo, en el caso de que un worker este caido va a la siguinete
    puerto_worker = 0

    #Por cada porcion de imagen, envio un request al Worker para que le aplique ese filtro
    for i in range(0,len(imagenes)):
        # Crear el objeto JSON para enviar
        json_data = {
            "id": i, #Identificador de la imagen
            "imagenes": imagenes[i].tolist()
        }

        # Convertir el objeto JSON a una cadena JSON
        json_string = json.dumps(json_data)

        # Especificar los encabezados de la solicitud HTTP
        headers = {'Content-Type': 'application/json'}

        #Este While true es para pasarle una parte de la iamgen a un worker si o si
        while True:
            try:
                # Enviar la solicitud POST al Worker
                response = requests.post(f'http://{HOST}:{PORT[puerto_worker]}/sobel', data=json_string, headers=headers)

                #Obtengo la imagen filtrada y la guardo en un arreglo
                imagen_filtrada = response.json()["imagen"]
                imagen_np = np.array(imagen_filtrada,dtype=np.uint8)
                imagen_np = np.squeeze(imagen_np)
                particiones_sobel.append(imagen_np)

                #Si se le aplico el filtro, salgo del bucle
                if response.status_code == 200:
                    puerto_worker = ( puerto_worker + 1) % len(PORT) #Voy al worker siguiente, ya que el actual estara trabajando
                    break

            #Si el worker esta caido
            except requests.exceptions.RequestException as e:
                puerto_worker = ( puerto_worker + 1) % len(PORT) #Voy al worker siguiente
                #print(f"Error al enviar la solicitud: {e}")

    #Devuelvo el arreglo de particiones
    return particiones_sobel

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Como usar el programa: python servidor_particion_envio.py (ruta-imagen) (cantidad_particiones_x) (cantidad_particiones_y)")
        sys.exit(1)

    # Obtengo la ruta y cargo la imagen
    ruta_img = sys.argv[1]
    imagen = cv2.imread(ruta_img)

    cantidad_particiones_x = int(sys.argv[2])
    cantidad_particiones_y = int(sys.argv[3])

    # Obtener el nombre del archivo sin la extensión
    nombre_archivo = os.path.splitext(os.path.basename(ruta_img))[0]

    #Particiono las imagenes
    particiones = particionar_imagen(imagen, cantidad_particiones_x, cantidad_particiones_y) #Cantidad de particiones en X y Y

    #Envio todas las particiones para que los workers apliquen sobel, y la guardo en un arreglo
    particiones_sobel = particionar_enviar_imagen(particiones)

    #Uno las particiones y guardo la imagen
    mi_imagen = unir_particiones(particiones_sobel)

    #Guardo la imagen
    cv2.imwrite(nombre_archivo + "_sobel.jpg", mi_imagen)
    print("Imagen filtrada con exito!")