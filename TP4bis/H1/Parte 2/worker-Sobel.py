import cv2  # Biblioteca para el procesamiento de imagenes
import numpy as np  # Biblioteca para la computacion cientifica en Python, que permite realizar operaciones matematicas eficientes en matrices y matrices mutldimiensionales.
from flask import Flask, jsonify, request
import pika


# Funcion que aplica sobel
def aplicar_sobel(imagen):
    # La convierto a nparray para poder aplicarle Sobel
    imagen_bytes = np.frombuffer(imagen, np.uint8)
    imagen_np = cv2.imdecode(imagen_bytes, cv2.IMREAD_COLOR)

    # Le aplico sobel
    imagen_sobel = sobel(imagen_np)

    # Mostrar la imagen resultante
    # cv2.imshow("Imagen Sobel", imagen_sobel)
    # cv2.waitKey(0)  # Esperar hasta que se presione una tecla
    # cv2.destroyAllWindows()  # Cerrar todas las ventanas abiertas por OpenCV

    return imagen_sobel

# Funcion que aplica sobel
def sobel(imagen):
    # print(imagen)
    # Primero convierto la imagen a escala de grises
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # Aplico el operador de Sobel en los ejes X e Y
    sobel_x = cv2.Sobel(gris, cv2.CV_64F, 1, 0, ksize=3)  # Detecta bordes verticales
    sobel_y = cv2.Sobel(gris, cv2.CV_64F, 0, 1, ksize=3)  # Detecta bordes horizontales

    # Calculo la magnitud del gradiente, combinando los resultados de X e Y
    magnitud = np.sqrt(sobel_x**2 + sobel_y**2)

    # Normaliza la magnitud, asi la convierto ea imagen de 8 bits
    magnitud = cv2.normalize(magnitud, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    # De esta forma, los valores estan en el rango de 0 a 255

    # Retorno la imagen con el filtro (bordes resaltados)
    return magnitud

host = "localhost"
nombre_queue = "image_parts"

# Me conecto con rabbit
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
channel = connection.channel()

# Creo la cola en el caso de que no exista
channel.queue_declare(queue=nombre_queue, durable=True)
print(" Esperando mensajes. Toque CTRL+C para salir")

# Funcion que se ejecuta cada vez que recibo un mensaje
def callback(ch, method, properties, body):

    # Decodifico el identificador y el nombre de la imagen
    identificador = properties.headers.get("identificador")
    # Decodifico el identificador del encabezado
    nombre_imagen = properties.headers.get("nombre")
    queues_resultado = nombre_queue + "_result_" + nombre_imagen

    print(f" Imagen recibida! ID:{identificador} ")

    imagen_sobel = aplicar_sobel(body)
    # print(imagen_sobel)

    print(" Filtro aplicado! ")

    # Envío la imagen procesada a la cola de resultados
    # Codifico la imagen a bytes
    _, buffer = cv2.imencode(".jpg", imagen_sobel)
    mensaje = buffer.tobytes()
    channel.queue_declare(queue=queues_resultado, durable=True)
    channel.basic_publish(
        exchange="",
        routing_key=queues_resultado,
        body=mensaje,
        properties=pika.BasicProperties(
            headers={"identificador": identificador}  # Identificador para cada parte
        ),
    )

    ch.basic_ack(
        delivery_tag=method.delivery_tag
    )  # Tengo ACK, de esta forma si se da de baja un workers no pierdo los mensajes.


channel.basic_qos(
    prefetch_count=1
)  # Elimina el problema de RoundRobin y los mensajes sin trabajar mientras espera un worker
channel.basic_consume(queue=nombre_queue, on_message_callback=callback)

# Dejo el consumidor en escucha
channel.start_consuming()
