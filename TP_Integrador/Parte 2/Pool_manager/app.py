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
from Shared.utils.dificultad import disminuir_prefijo

import threading
from redis.exceptions import LockError

from kubernetes import client, config
from kubernetes.client.rest import ApiException

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

POOL_MANAGER_LOCK = "lock:pool-manager:leader"
LOCK_TTL = 30
LOCK_RENEW_INTERVAL = 10

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

def procesar_bloque(channel, bloque: Dict[str, Any], redis_client, detener=None) -> bool:
    if detener is not None and detener.is_set():
        return False

    logger.info(f"Bloque recibido ID={bloque['id']}")

    consumidores_activos = contar_workers_activos(channel)
    logger.info(f"La cola tiene {consumidores_activos} consumidores activos.")

    if consumidores_activos <= 0:
        logger.warning("No hay workers activos. Intentando levantar worker CPU...")

        levantar_worker_cpu_si_hace_falta(redis_client)

        consumidores_activos = esperar_workers(channel, timeout=20, detener=detener)

        if detener is not None and detener.is_set():
            return False
        
        if consumidores_activos <= 0:
            redis_client.guardar_bloque_en_proceso(bloque, [])
            redis_client.marcar_reproceso_bloque("NO_WORKERS")
            logger.warning("No se pudo levantar ningun worker. Bloque marcado para reproceso")
            return True

    bloque["prefix"] = redis_client.get_prefijo()

    ultimo = redis_client.get_ultimo()

    if ultimo is None:
        bloque.setdefault("blockchain_content", f"[{time.time()}]")
        bloque["previous_block_hash"] = "None"
    else:
        bloque["blockchain_content"] = ultimo["blockchain_content"]
        bloque["previous_block_hash"] = ultimo["hash"]

    max_random = bloque["max_random"]
    rangos = dividir_rango(max_random, consumidores_activos)

    redis_client.guardar_bloque_en_proceso(bloque, rangos)

    logger.info(f"Generando {len(rangos)} tareas para bloque ID={bloque['id']}")

    for start, end in rangos:
        tarea = crear_tarea(bloque, start, end)
        publicar_tarea(channel, tarea)

    logger.info(f"Tareas publicadas para bloque ID={bloque['id']}")
    return True 


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

def renovar_liderazgo(lock, detener: threading.Event) -> None:
    while not detener.wait(LOCK_RENEW_INTERVAL):
        try:
            lock.extend(LOCK_TTL, replace_ttl=True)
        except Exception:
            logger.exception("Se perdio el liderazgo del Pool Manager.")
            detener.set()
            return


def ejecutar_con_failover() -> None:
    redis_client = RedisUtils()

    while True:
        lock = redis_client.redis_client.lock(
            POOL_MANAGER_LOCK,
            timeout=LOCK_TTL,
            blocking_timeout=0,
            thread_local=False,
        )

        if not lock.acquire(blocking=False):
            logger.info("Pool Manager en espera: otro pod es el líder.")
            time.sleep(5)
            continue

        logger.info("Pool Manager líder adquirido.")
        detener = threading.Event()
        renovador = threading.Thread(
            target=renovar_liderazgo,
            args=(lock, detener),
            daemon=True,
        )
        renovador.start()

        try:
            iniciar_pool_manager(redis_client, detener)
        finally:
            detener.set()
            renovador.join(timeout=2)

            try:
                if lock.owned():
                    lock.release()
            except LockError:
                pass

            logger.info("Pool Manager dejó el liderazgo.")

def iniciar_pool_manager(redis_client, detener: threading.Event) -> None:
    logger.info("Iniciando pool Manager...")

    while not detener.is_set():
        connection = None

        try:
            connection = crear_conexion(max_attempts=1)
            channel = crear_canal(connection)

            channel.queue_declare( queue=QUEUE_BLOCKS, durable=True)
            channel.queue_bind( exchange=EXCHANGE_NAME, queue=QUEUE_BLOCKS, routing_key="blocks")

            channel.queue_declare( queue=QUEUE_TASKS, durable=True)
            channel.basic_qos(prefetch_count=1)

            logger.info(
                "Pool Manager conectado a RabbitMQ"
            )

            while connection.is_open and channel.is_open and not detener.is_set():
                estado = redis_client.get_bloque_en_proceso()

                if estado and estado.get("reprocess"):
                    bloque = estado["block"]

                    logger.info( "Reprocesando bloque ID=%s", bloque["id"])

                    procesar_bloque( channel, bloque, redis_client, detener )

                    time.sleep(2)
                    continue

                if ( estado and estado.get("status") == "PROCESSING" ):
                    if redis_client.marcar_reproceso_si_expirado(
                        WORKER_TIMEOUT
                    ):
                        logger.warning( "Bloque ID=%s expirado", estado["id"])

                    time.sleep(2)
                    continue

                method, _, body = channel.basic_get(
                    queue=QUEUE_BLOCKS,
                    auto_ack=False,
                )

                if method:
                    bloque = json.loads(body)

                    procesado = procesar_bloque( channel, bloque, redis_client, detener )

                    if not procesado:
                        channel.basic_nack( delivery_tag=method.delivery_tag, requeue=True )
                        break

                    channel.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    time.sleep(2)

        except Exception as error:
            logger.error(
                "Conexion RabbitMQ perdida: %s. "
                "Reconectando en 5 segundos...",
                error,
            )

        finally:
            if connection is not None and connection.is_open:
                try:
                    connection.close()
                except Exception:
                    pass

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


def levantar_worker_cpu_si_hace_falta(redis_client) -> bool:
    # if os.getenv("AUTO_START_WORKER_CPU", "false").lower() != "true":
    #     return False
    
    image = os.getenv("WORKER_CPU_IMAGE", "josuegaticaodato/sdyp-worker-cpu:latest")
    name = os.getenv("AUTO_WORKER_CPU_NAME", "worker-cpu-auto")

    try:
        # Credenciales del Pod
        config.load_incluster_config()
        v1 = client.CoreV1Api()
        namespace = "default"

        # Disminuir prefijo
        disminuir_prefijo(redis_client, max_ceros=5)
        
        # Verificar si el pod ya existe
        try:
            pod = v1.read_namespaced_pod(name=name, namespace=namespace)
            if pod.status.phase == "Running":
                logger.info("El worker CPU ya está activo.")
                return True
            else:
                logger.warning(f"Worker CPU existe pero está en estado: {pod.status.phase}")
                return True
        
        except ApiException as e:
            if e.status != 404:
                raise e
      
        logger.warning("Levantando worker CPU automatico en Kubernetes...")

        # Definimos las variables de entorno
        env_vars = [
            client.V1EnvVar(name="RABBIT_HOST", value="rabbitmq"),
            client.V1EnvVar(name="RABBIT_PORT", value="5672"),
            client.V1EnvVar(
                name="RABBIT_USER",
                value_from=client.V1EnvVarSource(
                    secret_key_ref=client.V1SecretKeySelector(
                        name="app-secrets",
                        key="RABBIT_USER"
                    )
                )
            ),
            client.V1EnvVar(
                name="RABBIT_PASS",
                value_from=client.V1EnvVarSource(
                    secret_key_ref=client.V1SecretKeySelector(
                        name="app-secrets",
                        key="RABBIT_PASS"
                    )
                )
            ),
            client.V1EnvVar(name="ENDPOINT_COORDINADOR", value="http://coordinador:5000/tarea_worker"),
            client.V1EnvVar(name="COORDINADOR_URL", value="http://coordinador:5000"),
            client.V1EnvVar(name="WORKER_ID", value=name),
            client.V1EnvVar(
                name="WORKER_API_TOKEN",
                value_from=client.V1EnvVarSource(
                    secret_key_ref=client.V1SecretKeySelector(
                        name="app-secrets",
                        key="WORKER_API_TOKEN",
                    )
                ),
            ),
        ]

        # Definimos el contenedor
        container = client.V1Container(
            name="worker",
            image=image,
            image_pull_policy="Always", 
            env=env_vars
        )

        # Definimos el Pod
        pod_spec = client.V1PodSpec(restart_policy="Never", containers=[container])
        pod_manifest = client.V1Pod(
            metadata=client.V1ObjectMeta(name=name, labels={"app": "worker-cpu"}),
            spec=pod_spec
        )
      
        # K8s que cree el Pod
        v1.create_namespaced_pod(namespace=namespace, body=pod_manifest)
        logger.info("Orden de creación enviada a Kubernetes. El clúster hará el pull automáticamente.")
        
        return True

    except Exception as e:
        logger.error(f"No se pudo levantar worker CPU en Kubernetes: {e}")
        return False

def esperar_workers(channel, timeout=20, intervalo=1, detener=None) -> int:
    limite = time.monotonic() + timeout

    while time.monotonic() < limite:
        if detener is not None and detener.is_set():
            return 0

        consumidores = contar_workers_activos(channel)

        if consumidores > 0:
            logger.info( "Worker detectado. Cantidad de consumidores: %s", consumidores)
            return consumidores

        if detener is not None:
            detener.wait(intervalo)
        else:
            time.sleep(intervalo)

    return 0


# ----------------------------------------------------------------------
#                            MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":
    ejecutar_con_failover()