import cv2
from flask import Flask, request, jsonify
import numpy as np
import pika
import base64

app = Flask(__name__)


@app.route(rule="/sobel", methods=["POST"])
def sobelwebServer():
    # Verifico que exista un archivo en la solicitud
    if "imagen" not in request.files:
        return jsonify({"error": "No hay archivo para convertir"}), 400

    # Obtengo la imagen y la divido
    imagen_file = request.files["imagen"]
    nombreImagen = imagen_file.filename
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
        return (
            jsonify({"error": "Los valores de las particiones deben ser enteros"}),
            400,
        )

    #Realizo las particiones de la imagen, tanto en x e y
    particiones = particionar_imagen(imagencv2, partX, partY)

    #print(particiones)

    #Envio las partes a los workers, usando rabbit
    enviar_partes(nombreImagen,particiones)

    #Habilito la cola para recibir resultados
    cantPartes = partX * partY
    particiones_sobel = recibir_resultados(nombreImagen,cantPartes)

    #Uno la imagen y tengo el resultado
    imagen_resultado = unir_particiones(particiones_sobel)
    #print(imagen_resultado)

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
def recibir_resultados(nombreImagen,cantPartes, host="localhost"):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()
    nombre_queue = "image_parts_result_" + nombreImagen

    cant_imagenes_procesadas = 0

    channel.queue_declare(queue=nombre_queue, durable=True)

    particiones = [None] * cantPartes
    
    def callback(ch, method, properties, body):
        nonlocal  cant_imagenes_procesadas

        #Paso de bites a formato mi formato
        imagen_bytes = np.frombuffer(body, np.uint8)
        imagen_np = cv2.imdecode(imagen_bytes, cv2.IMREAD_COLOR)

        # Decodifico el identificador del encabezado
        identificador = properties.headers.get("identificador")

        #print(imagen_np)

        #Guardo la particion
        particiones[int(identificador)] = imagen_np
        #particiones.append(imagen_np)

        # Incremento el contador de imágenes procesadas
        cant_imagenes_procesadas += 1
        print(f"Imagen sobel recibida! {cant_imagenes_procesadas} de {cantPartes}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

        # Si hemos procesado 4 imágenes, dejamos de consumir mensajes
        if cant_imagenes_procesadas == cantPartes:
            print("Se han procesado todas las imágenes. Dejando de consumir mensajes.")
            channel.stop_consuming()

    # Cada vez que hay algo en la cola, lo proceso en callback
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=nombre_queue, on_message_callback=callback)

    # Dejo el consumidor en escucha
    channel.start_consuming()

    #Devuelvo la lista con todas las particiones
    return particiones

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
