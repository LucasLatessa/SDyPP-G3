"""
pool Manager

Este módulo se encarga de:
- Consumir bloques generados por el coordinador
- Dividir el trabajo en rangos (chunks)
- Distribuir tareas a los workers mediante RabbitMQ
"""

import json
import time
import os
from typing import List, Tuple, Dict, Any

from Shared.messaging.rabbitmq import crear_conexion, crear_canal
from Shared.storage.redis import RedisUtils
from Shared.utils.logger import get_logger
from Shared.config import EXCHANGE_NAME, QUEUE_BLOCKS, QUEUE_TASKS, WORKER_TIMEOUT


# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------


def contar_workers_activos(channel) -> int:
    canal = channel.queue_declare(queue=QUEUE_TASKS, passive=True)
    return canal.method.consumer_count


def dividir_rango(max_random: int, consumidores_activos: int) -> List[Tuple[int, int]]:
    if consumidores_activos <= 0:
        return []

    total = max_random + 1
    base = total // consumidores_activos
    resto = total % consumidores_activos

    rangos = []
    start = 0

    for i in range(consumidores_activos):
        size = base + (1 if i < resto else 0)
        end = start + size - 1
        rangos.append((start, end))
        start = end + 1

    logger.info(f"Rangos {rangos}")
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

def procesar_bloque(channel, bloque: Dict[str, Any], redis_client) -> None:
    logger.info(f"Bloque recibido ID={bloque['id']}")

    consumidores_activos = contar_workers_activos(channel)
    logger.info(f"La cola tiene {consumidores_activos} consumidores activos.")

    if consumidores_activos <= 0:
        logger.warning("No hay workers activos. Intentando levantar worker CPU...")

        levantar_worker_cpu_si_hace_falta()

        consumidores_activos = esperar_workers(channel, timeout=20)

        if consumidores_activos <= 0:
            redis_client.guardar_bloque_en_proceso(bloque, [])
            redis_client.marcar_reproceso_bloque("NO_WORKERS")
            logger.warning("No se pudo levantar ningun worker. Bloque marcado para reproceso")
            return


    max_random = bloque["max_random"]
    rangos = dividir_rango(max_random, consumidores_activos)

    redis_client.guardar_bloque_en_proceso(bloque, rangos)

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

    redis_client = RedisUtils()
    
    connection = crear_conexion()
    channel = crear_canal(connection)

    channel.queue_declare(queue=QUEUE_BLOCKS, durable=True)
    channel.queue_bind(
        exchange=EXCHANGE_NAME,
        queue=QUEUE_BLOCKS,
        routing_key="blocks"
    )

    channel.queue_declare(queue=QUEUE_TASKS, durable=True)
    channel.basic_qos(prefetch_count=1)

    logger.info("pool Manager esperando bloques...")

    while True:
        try:
            estado = redis_client.get_bloque_en_proceso()

            if estado and estado.get("reprocess"):
                bloque = estado["block"]
                logger.info(f"Reprocesando bloque ID={bloque['id']}")
                procesar_bloque(channel, bloque, redis_client)
                time.sleep(2)
                continue

            if estado and estado.get("status") == "PROCESSING":
                if redis_client.marcar_reproceso_si_expirado(WORKER_TIMEOUT):
                    logger.warning(f"Bloque ID={estado['id']} expirado. Marcado para reproceso")

                time.sleep(2)
                continue

            method, properties, body = channel.basic_get(
                queue=QUEUE_BLOCKS,
                auto_ack=False,
            )

            if method:
                bloque = json.loads(body)
                procesar_bloque(channel, bloque, redis_client)
                channel.basic_ack(delivery_tag=method.delivery_tag)
            else:
                time.sleep(2)

        except Exception as e:
            logger.error(f"Error en pool Manager: {e}")
            time.sleep(5)

def obtener_red_actual(client):
    network_env = os.getenv("DOCKER_NETWORK")
    if network_env:
        return network_env

    container_id = os.getenv("HOSTNAME")
    if not container_id:
        return None

    container = client.containers.get(container_id)
    networks = container.attrs["NetworkSettings"]["Networks"]

    for name in networks:
        if name != "bridge":
            return name

    return None


def levantar_worker_cpu_si_hace_falta() -> bool:
    if os.getenv("AUTO_START_WORKER_CPU", "false").lower() != "true":
        return False

    try:
        import docker

        image = os.getenv("WORKER_CPU_IMAGE", "sdyp-worker-cpu:latest")
        name = os.getenv("AUTO_WORKER_CPU_NAME", "worker_cpu_auto")

        client = docker.from_env()

        try:
            container = client.containers.get(name)

            if container.status != "running":
                logger.warning("Worker CPU existe pero esta detenido. Iniciando...")
                container.start()
                return True

            logger.info("Worker CPU automatico ya esta corriendo")
            return True

        except docker.errors.NotFound:
            network_name = obtener_red_actual(client)

            logger.warning("Levantando worker CPU automatico...")

            kwargs = {
                "image": image,
                "name": name,
                "detach": True,
                "environment": {
                    "RABBIT_HOST": "rabbitmq",
                    "RABBIT_PORT": "5672",
                    "RABBIT_USER": "grupo03",
                    "RABBIT_PASS": "grupo03",
                    "ENDPOINT_COORDINADOR": "http://coordinador:5000/tarea_worker",
                    "COORDINADOR_URL": "http://coordinador:5000",
                    "WORKER_ID": name,
                },
            }

            if network_name:
                kwargs["network"] = network_name

            client.containers.run(**kwargs)
            return True

    except Exception as e:
        logger.error(f"No se pudo levantar worker CPU automatico: {e}")
        return False


def esperar_workers(channel, timeout=20, intervalo=1) -> int:
    deadline = time.time() + timeout

    while time.time() < deadline:
        consumidores = contar_workers_activos(channel)

        if consumidores > 0:
            return consumidores

        time.sleep(intervalo)

    return 0


# ----------------------------------------------------------------------
#                            MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":
    iniciar_pool_manager()