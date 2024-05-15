from particionador import particionar_imagen
import sys
import cv2
import requests
import json


def particionar_enviar_imagen(imagenes):
    HOST = "127.0.0.1"
    PORT = 9999

    # Convertir todas las imágenes a una lista de diccionarios JSON
    imagenes_json = [{"imagen": imagen.tolist()} for imagen in imagenes]

    # Crear el objeto JSON para enviar
    json_data = {"imagenes": imagenes_json}

    # Convertir el objeto JSON a una cadena JSON
    json_string = json.dumps(json_data)

    # Especificar los encabezados de la solicitud HTTP
    headers = {'Content-Type': 'application/json'}

    try:
        # Enviar la solicitud POST al servidor
        response = requests.post(f'http://{HOST}:{PORT}/sobel', data=json_string, headers=headers)
        response.raise_for_status()  # Lanzar una excepción si la respuesta indica un error
        print("Solicitud enviada correctamente")
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar la solicitud: {e}")



if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Como usar el programa: python particionador.py (ruta-imagen)")
        sys.exit(1)

    # Obtengo la ruta y cargo la imagen
    ruta_img = sys.argv[1]
    imagen = cv2.imread(ruta_img)

    particiones = particionar_imagen(imagen)

    particionar_enviar_imagen(particiones)
    