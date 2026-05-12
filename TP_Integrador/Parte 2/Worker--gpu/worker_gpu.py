import json
import logging
import os
import threading
import time
from typing import Any

import pika
import requests

import minero_gpu


ENDPOINT_COORDINADOR = os.getenv(
    "ENDPOINT_COORDINADOR",
    "http://localhost:5000/tarea_worker",
)

COORDINADOR_URL = os.getenv("COORDINADOR_URL")
if not COORDINADOR_URL:
    COORDINADOR_URL = ENDPOINT_COORDINADOR.rstrip("/")
    if COORDINADOR_URL.endswith("/tarea_worker"):
        COORDINADOR_URL = COORDINADOR_URL[: -len("/tarea_worker")]

RABBIT_HOST = os.getenv("RABBIT_HOST", "localhost")
RABBIT_PORT = int(os.getenv("RABBIT_PORT", "5672"))
RABBIT_USER = os.getenv("RABBIT_USER", "grupo03")
RABBIT_PASS = os.getenv("RABBIT_PASS", "grupo03")

QUEUE_TASKS = "task_queue"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [WORKER-GPU] %(message)s",
)
logger = logging.getLogger(__name__)


def enviar_resultado(resultado: dict[str, Any]) -> None:
    try:
        response = requests.post(ENDPOINT_COORDINADOR, json=resultado, timeout=5)

        if response.status_code == 201:
            logger.info("Resultado enviado correctamente al coordinador")
        else:
            logger.warning(
                "Error al enviar resultado: status=%s body=%s",
                response.status_code,
                response.text,
            )

    except requests.exceptions.RequestException as e:
        logger.error("Fallo al enviar resultado: %s", e)


def consultar_estado_bloque(block_id: str, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        if stop_event.wait(1):
            break

        try:
            endpoint = f"{COORDINADOR_URL.rstrip('/')}/bloques/{block_id}/estado"
            respuesta = requests.get(endpoint, timeout=5)

            if respuesta.status_code == 200:
                logger.info("El bloque %s ya fue resuelto. Abortando...", block_id)
                stop_event.set()
                break

        except requests.exceptions.RequestException as e:
            logger.warning("Error consultando estado del bloque: %s", e)


def resolver_desafio(task: dict[str, Any]) -> dict[str, Any] | None:
    block_id = task["id"]
    base_string = task["base_string_chain"]
    blockchain_content = task["blockchain_content"]
    prefix = task["prefix"]
    start = int(task["start"])
    end = int(task["end"])

    worker_id = os.getenv("WORKER_ID", "worker-gpu")

    logger.info("Procesando bloque %s rango %s-%s", block_id, start, end)

    stop_event = threading.Event()
    monitor_thread = threading.Thread(
        target=consultar_estado_bloque,
        args=(block_id, stop_event),
        daemon=True,
    )
    monitor_thread.start()

    tiempo_inicial = time.time()

    try:
        resultado_raw = minero_gpu.ejecutar_minero(
            from_val=start,
            to_val=end,
            prefix=prefix,
            hash_val=base_string + blockchain_content,
            stop_event=stop_event,
        )

        tiempo_proceso = time.time() - tiempo_inicial

        if not resultado_raw:
            logger.info("GPU no encontro solucion en rango %s-%s", start, end)
            return {
                "id": block_id,
                "found": False,
                "start": start,
                "end": end,
                "worker_id": worker_id,
                "tiempo_proceso": tiempo_proceso,
            }

        resultado_gpu = json.loads(resultado_raw)

        if not resultado_gpu.get("hash_md5_result"):
            logger.info("GPU no encontro hash valido en rango %s-%s", start, end)
            return {
                "id": block_id,
                "found": False,
                "start": start,
                "end": end,
                "worker_id": worker_id,
                "tiempo_proceso": tiempo_proceso,
            }

        if stop_event.is_set():
            logger.info("Solucion encontrada, pero el bloque ya fue resuelto")
            return None

        nonce = int(resultado_gpu["numero"])
        hash_result = resultado_gpu["hash_md5_result"]

        logger.info(
            "Solucion encontrada bloque=%s nonce=%s hash=%s tiempo=%.4fs",
            block_id,
            nonce,
            hash_result,
            tiempo_proceso,
        )

        return {
            "id": block_id,
            "found": True,
            "transaccion": task["transaccion"],
            "base_string_chain": base_string,
            "prefix": prefix,
            "blockchain_content": blockchain_content,
            "numero": nonce,
            "hash": hash_result,
            "tiempo_proceso": tiempo_proceso,
            "start": start,
            "end": end,
            "worker_id": worker_id,
        }

    finally:
        stop_event.set()


def callback(ch, method, properties, body: bytes) -> None:
    try:
        task = json.loads(body)
        logger.info("Nueva tarea recibida")

        resultado = resolver_desafio(task)

        if resultado:
            enviar_resultado(resultado)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logger.error("Error procesando tarea: %s", e)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def iniciar_worker() -> None:
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
            channel.queue_declare(queue=QUEUE_TASKS, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_TASKS, on_message_callback=callback)

            logger.info("Worker GPU listo. Esperando tareas...")
            channel.start_consuming()

        except Exception as e:
            logger.error("Error de conexion: %s. Reintentando en 5s...", e)
            time.sleep(5)


if __name__ == "__main__":
    iniciar_worker()
