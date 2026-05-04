import hashlib
import json
import os
import random
import time
import pika
import requests
import logging
from typing import Dict, Any

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
QUEUE_TASKS = "task_queue"

LOG_LEVEL: int = logging.INFO

# ----------------------------------------------------------------------
#                             LOGGING
# ----------------------------------------------------------------------

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] [WORKER] %(message)s",
)

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------

def calcular_hash(base_string: str, blockchain_content: str, nonce: int) -> str:
    """
    Calcula el hash MD5 igual que el minero original.

    Args:
        base_string (str): Base del bloque
        blockchain_content (str): Contenido de la blockchain
        nonce (int): Número a probar

    Returns:
        str: Hash generado
    """
    texto: str = f"{nonce}{base_string}{blockchain_content}"
    return hashlib.md5(texto.encode()).hexdigest()


def enviar_resultado(resultado) -> None:
    """
    Envía el resultado válido al coordinador vía HTTP.

    Args:
        resultado (Dict[str, Any]): Resultado del PoW.
    """
    try:
        response = requests.post(url, json=resultado, timeout=5)

        if response.status_code == 200:
            logger.info("Resultado enviado correctamente al coordinador")
        else:
            logger.warning(f"Error al enviar resultado: {response.status_code}")

    except Exception as e:
        logger.error(f"Fallo al enviar resultado: {e}")


# def resolver_desafio(task):
#     """
#     Resuelve el desafío de minería dentro de un rango de nonces.

#     Args:
#         task: Tarea con datos del bloque y rango.

#     Returns:
#         Dict[str, Any]: Resultado con nonce y hash válido, o vacío si no se encuentra.
#     """
#     block_id: str = task["id"]
#     base_string: str = task["base_string_chain"]
#     prefix: str = task["prefix"]
#     start: int = task["start"]
#     end: int = task["end"]

#     logger.info(f"Procesando bloque {block_id} rango {start}-{end}")

#     for nonce in range(start, end):
#         hash_result: str = calcular_hash(base_string)

#         if hash_result.startswith(prefix):
#             logger.info(f"Solución encontrada: nonce={nonce}, hash={hash_result}")

#             return {
#                 "block_id": block_id,
#                 "nonce": nonce,
#                 "hash": hash_result,
#                 "numero": nonce
#             }

#     logger.info(f"No se encontró solución en rango {start}-{end}")
#     return {}


def resolver_desafio(task):
    """
    Resuelve el desafío de minería dentro de un rango de nonces.
    """
    block_id: str = task["id"]
    base_string: str = task["base_string_chain"]
    blockchain_content: str = task["blockchain_content"]
    prefix: str = task["prefix"]
    start: int = task["start"]
    end: int = task["end"]

    logger.info(f"Procesando bloque {block_id} rango {start}-{end}")

    tiempo_inicial = time.time()

    for nonce in range(start, end):
        hash_result: str = calcular_hash(base_string, blockchain_content, nonce)

        if hash_result.startswith(prefix):
            tiempo_proceso = time.time() - tiempo_inicial

            logger.info(f"Solución encontrada: nonce={nonce}, hash={hash_result}")

            return {
                "id": block_id,
                'transaccion': task["transaccion"],
                'base_string_chain': base_string,
                'prefix': prefix,
                'blockchain_content': blockchain_content,
                "numero": nonce, 
                "hash": hash_result,
                "tiempo_proceso": tiempo_proceso,
            }

    logger.info(f"No se encontró solución en rango {start}-{end}")
    return {}


def callback(
    ch: pika.adapters.blocking_connection.BlockingChannel,
    method: pika.spec.Basic.Deliver,
    properties: pika.spec.BasicProperties,
    body: bytes,
) -> None:
    """
    Callback que procesa cada tarea recibida desde RabbitMQ.

    Args:
        ch: Canal de RabbitMQ.
        method: Información de entrega.
        properties: Propiedades del mensaje.
        body (bytes): Mensaje recibido.
    """
    try:
        task = json.loads(body)

        logger.info("Nueva tarea recibida")

        resultado = resolver_desafio(task)

        if resultado:
            enviar_resultado(resultado)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Error procesando tarea: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def iniciar_worker() -> None:
    """
    Inicializa la conexión con RabbitMQ y comienza a consumir tareas.
    """
    while True:
        try:
            logger.info("Conectando a RabbitMQ...")

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBIT_HOST,
                    port=RABBIT_PORT,
                    credentials=pika.PlainCredentials(RABBIT_USER, RABBIT_PASS),
                )
            )

            channel = connection.channel()

            channel.queue_declare(queue=QUEUE_TASKS)

            # fair dispatch, asi el mismo worker no agarra todo
            channel.basic_qos(prefetch_count=1)

            channel.basic_consume(queue=QUEUE_TASKS, on_message_callback=callback)

            logger.info("Worker listo. Esperando tareas...")

            channel.start_consuming()

        except Exception as e:
            logger.error(f"Error de conexión: {e}. Reintentando en 5s...")
            time.sleep(5)


# ----------------------------------------------------------------------
#                                MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":
    iniciar_worker()
