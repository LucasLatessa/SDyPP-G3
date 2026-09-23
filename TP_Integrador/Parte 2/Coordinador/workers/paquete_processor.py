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

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------


def procesar_paquetes(redis_client) -> None:
    while True:
        connection = None

        try:
            connection = crear_conexion(max_attempts=1)
            channel = crear_canal(connection)

            logger.info(
                "Procesador conectado a RabbitMQ"
            )

            while connection.is_open and channel.is_open:
                paquete = []
                delivery_tags = []

                for _ in range(TAMANO_BLOQUE_PROCESAR):
                    method_frame, _, body = channel.basic_get(
                        queue=QUEUE_NAME,
                        auto_ack=False,
                    )

                    if not method_frame:
                        break

                    paquete.append(json.loads(body))
                    delivery_tags.append(
                        method_frame.delivery_tag
                    )

                if paquete:
                    logger.info(
                        "Procesando paquete de %s transacciones",
                        len(paquete),
                    )

                    last_element = redis_client.get_ultimo()
                    prefijo = redis_client.get_prefijo()

                    bloque = {
                        "id": str(uuid.uuid4()),
                        "transaccion": paquete,
                        "prefix": prefijo,
                        "base_string_chain": STRING_CHAIN,
                        "blockchain_content": (
                            last_element["blockchain_content"]
                            if last_element
                            else "[" + str(time.time()) + "]"
                        ),
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
                        channel.basic_ack(
                            delivery_tag=delivery_tag
                        )

                    logger.info(
                        "Bloque enviado ID=%s",
                        bloque["id"],
                    )

                logger.info(
                    "Pasaron %s segundos, procesamiento de paquetes",
                    PROCESS_INTERVAL,
                )
                time.sleep(PROCESS_INTERVAL)

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
