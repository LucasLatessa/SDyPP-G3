import time
import cv2
from flask import Flask, request, jsonify
import numpy as np
import pika
import base64
import redis

app = Flask(__name__)

r = redis.Redis(host='localhost', port=6379, decode_responses=False)

@app.route(rule="/sobel", methods=["POST"])
def sobelwebServer():

    try:
        # Obtengo la imagen y la paso a numpy
        imagen_file = request.files["imagen"]
        nombreImagen = imagen_file.filename
        imagen_bytes = np.frombuffer(imagen_file.read(), np.uint8)
        imagencv2 = cv2.imdecode(imagen_bytes, cv2.IMREAD_COLOR)
        partX = int(request.form["particion-x"])
        partY = int(request.form["particion-y"])
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    #Realizo las particiones de la imagen, tanto en x e y
    particiones = particionar_imagen(imagencv2, partX, partY)

    #Envio las partes a los workers, usando rabbit
    enviar_partes(nombreImagen,particiones)

    #Consulto a la BD Rabit si ya estan listas las particiones
    cantPartes = partX * partY
    particiones_sobel = recibir_resultados(nombreImagen,cantPartes)

    #Uno la imagen y tengo el resultado
    imagen_resultado = unir_particiones(particiones_sobel)

    #Guardo y devuelvo el json con la imagen (obviamenten no se ve)
    cv2.imwrite(nombreImagen + "_sobel.jpg", imagen_resultado )
    #cv2.imshow("Imagen Sobel", imagen_resultado)
    #cv2.waitKey(0)  # Esperar hasta que se presione una tecla
    #cv2.destroyAllWindows()  # Cerrar todas las ventanas abiertas po

    return jsonify({"imagen": imagen_a_base64(imagen_resultado)})

#Funcion para mostrar la imagen
def imagen_a_base64(imagen):
    # Codificar la imagen en formato base64
    _, buffer = cv2.imencode('.jpg', imagen)
    imagen_base64 = base64.b64encode(buffer).decode('utf-8')
    return imagen_base64

# Encargado de particionar las imagenes en x e y
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
            # cv2.imwrite(f'particion{i}_{j}.jpg', particion)

    # print("Imagen particionada!")
    return particiones

# Encargado de unir todas las imagenes
def unir_particiones(particiones_sobel):
    # Calculo el tamaño (número de particiones en x y en y)
    n = int(len(particiones_sobel) ** 0.5)

    # Uno las particiones horizontales
    particiones_unidas = []
    for i in range(0, len(particiones_sobel), n):
        grupo = particiones_sobel[i : i + n]
        particiones_unidas.append(np.hstack(grupo))

    # Ahora uno de forma vertical
    imagen_unida = np.vstack(particiones_unidas)

    # Devuelvo la imagen completa
    return imagen_unida

# Funcion que envia todas las partes a la cola de Rabbit
def enviar_partes(nombreImagen, particiones, nombre_queue="image_parts", host="localhost"):
    # Me conecto a rabbit
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()

    # Creo la cola en el caso de que no exista
    channel.queue_declare(queue=nombre_queue, durable=True)

    # Por cada particion, envio a la cola para que se procesado por un worker
    for i, parteImagen in enumerate(particiones):
        # Codifico la imagen a bytes
        #print(parteImagen)
        _, buffer = cv2.imencode('.jpg', parteImagen)
        mensaje = buffer.tobytes()
        #print(mensaje)
        #print("-------------------------------------------------------")
        channel.basic_publish(exchange="", routing_key=nombre_queue, body=mensaje,properties=pika.BasicProperties(
            headers={"identificador": str(i), "nombre": nombreImagen}  # Identificador para cada parte
        ))

    #Cierro la conexion
    connection.close()

#Funcion que recibe los resultados de los workers
def recibir_resultados(nombreImagen,cantPartes):
    partes_recibidas = 0
    particiones = [None] * cantPartes
    while partes_recibidas < cantPartes:
        #Recorro todas las partes de la imagen, para buscar en redis
        for i in range(cantPartes):
            #Consulto por nombre de la imagen y parte
            redis_key = f"{nombreImagen}_{i}"
            #Hago get a redis para ver si existe esa parte
            mensaje = r.get(redis_key)
            #Si existe esa parte, la guardo
            if mensaje is not None and particiones[i] is None:
                # Convierto a imagne numpy
                imagen_bytes = np.frombuffer(mensaje, np.uint8)
                imagen_np = cv2.imdecode(imagen_bytes, cv2.IMREAD_COLOR)
                particiones[i] = imagen_np
                partes_recibidas += 1
                print(f"Imagen {nombreImagen} sobel recibida! {partes_recibidas} de {cantPartes}")
            # Borro la imagen de Redis
            r.delete(redis_key)

        # Espero para la proxima consulta a redis
        time.sleep(0.5)
        
    #Devuelvo la lista con todas las particiones
    return particiones

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
