"""
pool Manager

Este módulo se encarga de:
- Consumir bloques generados por el coordinador
- Dividir el trabajo en rangos (chunks)
- Distribuir tareas a los workers mediante RabbitMQ
"""

import json
import time
from typing import List, Tuple, Dict, Any

from Shared.messaging.rabbitmq import crear_conexion, crear_canal
from Shared.utils.logger import get_logger
from Shared.config import EXCHANGE_NAME, QUEUE_BLOCKS, QUEUE_TASKS, CHUNK_SIZE


# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------


def dividir_rango(max_random: int, channel, chunk_size: int) -> List[Tuple[int, int]]:
    """
    Divide el rango de trabajo total en múltiples subrangos (chunks).

    Args:
        max_random: Valor máximo del rango
        chunk_size: Tamaño de cada chunk
    Return
        Lista de tuplas (inicio, fin)
    """
    rangos = []

    #global canal
    #print(canal)
    canal = channel.queue_declare(queue=QUEUE_TASKS, passive=True)
    consumidores_activos = canal.method.consumer_count
    logger.info(f"La cola tiene {consumidores_activos} consumidores activos.")
    rango = max_random / consumidores_activos
    rango = int(rango)
    for i in range(1,consumidores_activos + 1):
        start = rango * (i - 1)
        end = rango * i
        rangos.append((int(start), int(end)))
    logger.info(f"Rangos {rangos}")
    # for start in range(0, max_random, chunk_size):
    #    end = min(start + chunk_size, max_random)
    #    rangos.append((start, end))

    return rangos


def crear_tarea(bloque: Dict[str, Any], start: int, end: int) -> Dict[str, Any]:
    """
    Crea una tarea a partir de un bloque y un rango.

    Args:
        bloque: Bloque original
        start: Inicio del rango
        end: Fin del rango
    Return
        Diccionario con la tarea
    """
    return {
        "id": bloque["id"],
        "transaccion": bloque["transaccion"],
        "prefix": bloque["prefix"],
        "base_string_chain": bloque["base_string_chain"],
        "blockchain_content": bloque["blockchain_content"],
        "max_random": bloque["max_random"],
        "start": start,
        "end": end
    }


def publicar_tarea(channel, tarea: Dict[str, Any]) -> None:
    """
    Publica una tarea en la cola de workers.

    Args:
        channel: Canal de RabbitMQ
        tarea: Tarea a enviar
    """
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_TASKS,
        body=json.dumps(tarea),
    )

def procesar_bloque(channel, body: bytes) -> None:
    """
    Procesa un bloque recibido desde RabbitMQ.

    Args:
        channel: Canal de RabbitMQ
        body: Mensaje recibido
    """
    bloque = json.loads(body)

    logger.info(f"Bloque recibido ID={bloque['id']}")

    max_random = bloque["max_random"]

    rangos = dividir_rango(max_random, channel, CHUNK_SIZE)

    logger.info(f"Generando {len(rangos)} tareas para bloque ID={bloque['id']}")

    for start, end in rangos:
        tarea = crear_tarea(bloque, start, end)
        publicar_tarea(channel, tarea)

    logger.info(f"Tareas publicadas para bloque ID={bloque['id']}")

def callback(channel, method, properties, body) -> None:
    """
    Callback de consumo de RabbitMQ.

    Args:
        channel: Canal
        method: Método
        properties: Propiedades
        body: Mensaje
    """
    try:
        procesar_bloque(channel, body)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error(f"Error procesando bloque: {e}")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def iniciar_pool_manager() -> None:
    """
    Inicializa el pool Manager y comienza a consumir bloques.
    """
    logger.info("Iniciando pool Manager...")

    connection = crear_conexion()
    channel = crear_canal(connection)

    global canal
    canal = channel.queue_declare(queue=QUEUE_BLOCKS)
    channel.queue_bind(
        exchange=EXCHANGE_NAME,
        queue=QUEUE_BLOCKS,
        routing_key="blocks"
    )

    # Cola de tareas para workers
    channel.queue_declare(queue=QUEUE_TASKS)

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=QUEUE_BLOCKS,
        on_message_callback=callback
    )

    logger.info("pool Manager esperando bloques...")

    channel.start_consuming()

# ----------------------------------------------------------------------
#                            MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":
    iniciar_pool_manager()
