import hashlib
import json
import os
import random
import time
import pika
import requests

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

url = os.getenv("ENDPOINT_COORDINADOR", "http://localhost:5000/tarea_worker")

# Configuración del servidor RabbitMQ
RABBIT_HOST = os.getenv("RABBIT_HOST", "localhost")
RABBIT_PORT = int(os.getenv("RABBIT_PORT", 5672))
RABBIT_USER = os.getenv("RABBIT_USER", "grupo03")
RABBIT_PASS = os.getenv("RABBIT_PASS", "grupo03")

# Configuración de mensajería
QUEUE_NAME = "transacciones"
EXCHANGE_TYPE = "topic"
EXCHANGE_NAME = "block_challenge"
ROUTING_KEY = "blocks"

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------


# Encargada de hacer el hash dado un texto
def calcular_md5(texto):
    hash = hashlib.md5()
    hash.update(texto.encode("utf-8"))
    return hash.hexdigest()


# Enviar el resultado al coordinador para verificar que el resultado es correcto
def enviar_resultado(data):
    try:
        response = requests.post(url, json=data)
        print("Resolucion enviada al Coordinador!")
    except Exception as e:
        print("Fallo al enviar el post:", e)


# Minero: Encargado de realizar el desafio
def minero(ch, method, properties, body):
    data = json.loads(body)
    print(f"Bloque {data} recibido")

    encontrado = False
    tiempo_inicial = time.time()

    print("Minero comenzado!")
    start_time_total = time.time()
    # Hasta que no encuentra un hash que comienze con el prefijo no para
    while not encontrado:
        # Tomo un numero aleatorio y le calculo el hash a: El aleatorio + la base del bloque + contenido de la cadena de bloues"
        aleatorio = str(random.randint(0, data["max_random"]))
        hash = calcular_md5(
            aleatorio + data["base_string_chain"] + data["blockchain_content"]
        )
        # Si el hash arranca con el prefijo
        if hash.startswith(data["prefix"]):
            # Corto el bucle y envio el resultado al coordinador
            encontrado = True
            tiempo_proceso = time.time() - tiempo_inicial

            print(f"Valor encontrado: {aleatorio}")
            data["tiempo_proceso"] = tiempo_proceso
            data["hash"] = hash
            data["numero"] = aleatorio

            enviar_resultado(data)
    # Confirmo con un ACK que lo resolvi
    end_time_total = time.time()
    execution_time_total = end_time_total - start_time_total

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(
        f"Resultado encontrado y enviado con el ID Bloque {data['id']} en {tiempo_proceso:.2f} segundos"
    )
    print("Tiempo de ejecucion:", execution_time_total)


# Conexion con rabbit al topico y comienza a ser consumidor
def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBIT_HOST,
            port=RABBIT_PORT,
            credentials=pika.PlainCredentials(RABBIT_USER, RABBIT_PASS),
        )
    )
    channel = connection.channel()
    channel.exchange_declare(
        exchange=EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, durable=True
    )
    result = channel.queue_declare("", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(
        exchange=EXCHANGE_NAME, queue=queue_name, routing_key=ROUTING_KEY
    )
    channel.basic_consume(queue=queue_name, on_message_callback=minero, auto_ack=False)
    print("Esperando mensajes. Para salir pulse CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        connection.close()
        print("Conexion cerrada")


# ----------------------------------------------------------------------
#                            MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":
    main()
