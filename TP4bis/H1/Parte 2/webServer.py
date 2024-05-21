import cv2
from flask import Flask, request,jsonify
import numpy as np

app = Flask(__name__)

@app.route(rule="/sobel",methods=["POST"])
def sobelwebServer():
    #Verifico que exista un archivo en la solicitud
    if 'imagen' not in request.files:
        return jsonify({"error": "No hay archivo para convertir"}), 400
    
    #Obtengo la imagen y la divido
    imagen_file = request.files['imagen']
    imagen_bytes = np.frombuffer(imagen_file.read(), np.uint8)
    imagencv2 = cv2.imdecode(imagen_bytes, cv2.IMREAD_COLOR)

    if imagencv2 is None:
        return jsonify({"error": "Error al leer la imagen"}), 400
    
    try:
        partX = int(request.form["particion-x"])
        partY = int(request.form["particion-y"])
    except KeyError as e:
        return jsonify({"error": f"Falta la clave de partición: {str(e)}"}), 400
    except ValueError:
        return jsonify({"error": "Los valores de las particiones deben ser enteros"}), 400
    
    particiones = particionar_imagen(imagencv2, partX, partY)
    print(particiones)
    
    return jsonify({"ok": "ok"})

#Encargado de particionar las imagenes en x e y
def particionar_imagen(image, num_particiones_x, num_particiones_y):
    # Obtén las dimensiones de la imagen
    height, width, _ = image.shape

    # Calcula el tamaño de cada partición
    part_height = height // num_particiones_y
    part_width = width // num_particiones_x

    # Lista para almacenar las particiones
    particiones = []

    # Particiona la imagen
    for i in range(num_particiones_y):
        for j in range(num_particiones_x):
            # Calcula los límites de cada partición
            y_start = i * part_height
            y_end = y_start + part_height
            x_start = j * part_width
            x_end = x_start + part_width

            # Extrae la partición
            particion = image[y_start:y_end, x_start:x_end]
            particiones.append(particion)

            # Solo para mostrar como quedan las particiones
            #cv2.imwrite(f'particion{i}_{j}.jpg', particion)

    #print("Imagen particionada!")
    return particiones

#Encargado de unir todas las imagenes
def unir_particiones(particiones_sobel):
    # Calculo el tamaño (número de particiones en x y en y)
    n = int(len(particiones_sobel) ** 0.5)

    # Uno las particiones horizontales
    particiones_unidas = []
    for i in range(0, len(particiones_sobel), n):
        grupo = particiones_sobel[i:i+n]
        particiones_unidas.append(np.hstack(grupo))

    # Ahora uno de forma vertical
    imagen_unida = np.vstack(particiones_unidas)

    #Devuelvo la imagen completa
    return imagen_unida

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')