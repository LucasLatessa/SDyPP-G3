import cv2
from flask import Flask, request
import numpy as np
import pika
import redis

app = Flask(__name__)

# Configuracion Reddis
host_redis = "localhost"
r = redis.Redis(host=host_redis, port=6379, decode_responses=False)


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


# Manda a encolar en rabbitMQ todas las particiones
def encolar(
    nombreImagen, particiones, id, nombre_queue="image_parts", host="localhost"
):
    # Me conecto a rabbit
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()

    # Creo la cola en el caso de que no exista
    channel.queue_declare(queue=nombre_queue, durable=True)

    # Por cada particion, envio a la cola para que se procesado por un worker
    for i, parteImagen in enumerate(particiones):
        # Codifico la imagen a bytes
        # print(parteImagen)
        _, buffer = cv2.imencode(".jpg", parteImagen)
        mensaje = buffer.tobytes()
        # print(mensaje)
        # print("-------------------------------------------------------")
        channel.basic_publish(
            exchange="",
            routing_key=nombre_queue,
            body=mensaje,
            properties=pika.BasicProperties(
                headers={"id": id, "parte": str(i)}  # Identificador para cada parte
            ),
        )

    # Cierro la conexion
    connection.close()


def subirCantidadPartes(id, cantPartes):
    # Envío la imagen procesada a Redis
    redis_key = f"{id}"
    r.set(redis_key, cantPartes)


# Encargado de partir la imagen en n pedazos y mandarla a la cola de Rabbit
@app.route("/split", methods=["POST"])
def splitImagen():
    imagen = request.files["imagen"]
    partX = int(request.form["particion-x"])
    partY = int(request.form["particion-y"])
    id = request.form["id"]

    # Paso a numpy para que pueda ser trabajada
    imagen_bytes = np.frombuffer(imagen.read(), np.uint8)
    imagencv2 = cv2.imdecode(imagen_bytes, cv2.IMREAD_COLOR)

    # Realizo las particiones de la imagen, tanto en x e y
    particiones = particionar_imagen(imagencv2, partX, partY)

    # Envio las partes a los workers, usando rabbit
    encolar(imagen.filename, particiones, id)

    # Envio a redis la cantidad de partes que tengo de mi imagen
    cantidadPartes = partX * partY
    subirCantidadPartes(id, cantidadPartes)

    return "Imagen particionada y encolada en rabbit", 200

#Endpoint de estado del servidor
@app.route(rule="/status", methods=["GET"])
def status():
    data = {
        "Status": "En funcionamiento :)"
    }
    print(data)
    return data


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
