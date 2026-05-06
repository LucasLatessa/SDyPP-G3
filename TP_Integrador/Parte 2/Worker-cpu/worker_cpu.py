import hashlib
import json
import os
import random
import threading
import time
import pika
import requests
import logging
from typing import Dict, Any

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

url_tarea = os.getenv("ENDPOINT_COORDINADOR", "http://localhost:5000/tarea_worker")
url = "http://localhost:5000"

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
        response = requests.post(url_tarea, json=resultado, timeout=5)

        if response.status_code == 201:
            logger.info("Resultado enviado correctamente al coordinador")
        else:
            logger.warning(f"Error al enviar resultado: {response.status_code}")

    except Exception as e:
        logger.error(f"Fallo al enviar resultado: {e}")

def consultar_estado_bloque(block_id: str, stop_event: threading.Event):
    """
    Hilo secundario: Consulta la API cada 10 segundos. 
    Si el bloque ya fue resuelto, levanta la bandera (stop_event) para detener el for.
    """
    while not stop_event.is_set():
        # wait(10) pausa este hilo por 10 segundos. 
        # La ventaja sobre time.sleep(10) es que si el minero encuentra la 
        # solución antes, el wait() se interrumpe al instante y el hilo se cierra.
        termino_antes = stop_event.wait(1) 
        
        if termino_antes:
            break # El minero encontró el hash, terminamos el monitoreo.
            
        try:
            # Reemplaza esta URL con tu endpoint real
            endpoint = f"{url}/bloques/{block_id}/estado"
            respuesta = requests.get(endpoint, timeout=5)
            
            if respuesta.status_code == 200:
              logger.info(f"El bloque {block_id} ya fue resuelto por otro agente. Abortando...")
              stop_event.set() # Levantamos la bandera para detener el for
              break
                    
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error consultando la API: {e}")

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


    stop_event = threading.Event()
    monitor_thread = threading.Thread(
        target=consultar_estado_bloque, 
        args=(block_id, stop_event),
        daemon=True # Garantiza que el hilo muera si el script principal se detiene
    )
    monitor_thread.start()

    resultado = None
    tiempo_inicial = time.time()
    
    for nonce in range(start, end):
        
        if nonce % 10000 == 0 and stop_event.is_set():
            logger.info("Ciclo for detenido externamente.")
            break
        
        hash_result: str = calcular_hash(base_string, blockchain_content, nonce)

        if hash_result.startswith(prefix):
            tiempo_proceso = time.time() - tiempo_inicial

            logger.info(f"Solución encontrada: nonce={nonce}, hash={hash_result}")

            resultado = {
                "id": block_id,
                'transaccion': task["transaccion"],
                'base_string_chain': base_string,
                'prefix': prefix,
                'blockchain_content': blockchain_content,
                "numero": nonce, 
                "hash": hash_result,
                "tiempo_proceso": tiempo_proceso
            }
            stop_event.set()
            break
    
    stop_event.set()
    #logger.info(f"No se encontró solución en rango {start}-{end}")
    return resultado
    #return {}


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
