"""
Procesamiento en segundo plano de paquetes de transacciones.
"""
import pika
from Shared.messaging.rabbitmq import crear_conexion, crear_canal
import json
import random
import time
import uuid
from Shared.config import (
    TAMANO_BLOQUE_PROCESAR,
    QUEUE_NAME,
    PROCESS_INTERVAL,
    MAX_RANDOM,
    EXCHANGE_NAME,
    ROUTING_KEY,
    RABBIT_TIMEOUT,
    DIFFICULT_PREFIX,
    STRING_CHAIN
)
from Shared.utils.logger import get_logger

logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------

PROCESSOR_HEARTBEAT_KEY = "health:block-processor"
PROCESSOR_HEARTBEAT_TTL = 120

class LiderazgoPerdido(Exception):
    pass


def verificar_liderazgo(lock, detener, finalizar):
    if detener.is_set() or finalizar.is_set() or not lock.owned():
        raise LiderazgoPerdido("El coordinador dejó de ser líder")

def procesar_paquetes(redis_client, lock, detener, finalizar) -> None:
    while not detener.is_set() and not finalizar.is_set():
        connection = None

        try:
            verificar_liderazgo(lock, detener, finalizar)
            connection = crear_conexion(max_attempts=1)
            channel = crear_canal(connection)

            logger.info( "Procesador conectado a RabbitMQ" )

            while connection.is_open and channel.is_open:
                verificar_liderazgo(lock, detener, finalizar)
                redis_client.redis_client.set( PROCESSOR_HEARTBEAT_KEY, str(time.time()), ex=PROCESSOR_HEARTBEAT_TTL )

                paquete = []
                delivery_tags = []

                for _ in range(TAMANO_BLOQUE_PROCESAR):
                    verificar_liderazgo(lock, detener, finalizar)
                    method_frame, _, body = channel.basic_get( queue=QUEUE_NAME, auto_ack=False)

                    if not method_frame:
                        break

                    paquete.append(json.loads(body))
                    delivery_tags.append( method_frame.delivery_tag )

                if paquete:
                    verificar_liderazgo(lock, detener, finalizar)
                    logger.info(
                        "Procesando paquete de %s transacciones",
                        len(paquete),
                    )

                    bloque = {
                        "id": str(uuid.uuid4()),
                        "transaccion": paquete,
                        "base_string_chain": STRING_CHAIN,
                        "max_random": MAX_RANDOM,
                    }

                    channel.basic_publish(
                        exchange=EXCHANGE_NAME,
                        routing_key=ROUTING_KEY,
                        body=json.dumps(bloque),
                        mandatory=True,
                        properties=pika.BasicProperties(
                            delivery_mode=2,
                            content_type="application/json",
                        ),
                    )

                    # Se confirman las transacciones solamente después
                    # de publicar correctamente el bloque.
                    for delivery_tag in delivery_tags:
                        channel.basic_ack( delivery_tag=delivery_tag )

                    logger.info(
                        "Bloque enviado ID=%s",
                        bloque["id"],
                    )

                logger.info(
                    "Pasaron %s segundos, procesamiento de paquetes",
                    PROCESS_INTERVAL,
                )

                limite = time.monotonic() + PROCESS_INTERVAL

                while time.monotonic() < limite:
                    verificar_liderazgo(lock, detener, finalizar)

                    connection.process_data_events(
                        time_limit=max( 0, min(1, limite - time.monotonic())),
                    )

        except LiderazgoPerdido:
            raise

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

        limite_reintento = time.monotonic() + 5

        while time.monotonic() < limite_reintento:
            if detener.is_set() or finalizar.wait(0.5):
                return
