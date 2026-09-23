"""
Módulo de conexión y configuración de RabbitMQ.

Provee utilidades para establecer la conexión con el broker de mensajería
y configurar los canales, colas y exchanges necesarios para el sistema
distribuido de transacciones.
"""

import time

import pika
from Shared.config import (
    RABBIT_HOST,
    RABBIT_PORT,
    RABBIT_USER,
    RABBIT_PASS,
    QUEUE_NAME,
    EXCHANGE_TYPE,
    EXCHANGE_NAME
)
from pika.adapters.blocking_connection import BlockingChannel
from Shared.utils.logger import get_logger

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------

def crear_conexion(
    max_attempts=None,
    wait_seconds=5,
) -> pika.BlockingConnection:
    attempts = 0
    """
    Establece y retorna una conexión con el servidor RabbitMQ. Es necesario tener host, puerto y credenciales definidas.

    Returns:
        pika.BlockingConnection: Objeto de conexión bloqueante hacia RabbitMQ
        configurado con las credenciales por defecto.
    """

    while max_attempts is None or attempts < max_attempts:
        try:
            return pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBIT_HOST,
                    port=RABBIT_PORT,
                    credentials=pika.PlainCredentials(
                        RABBIT_USER,
                        RABBIT_PASS,
                    ),
                    heartbeat=30,
                    blocked_connection_timeout=30,
                    connection_attempts=1,
                    socket_timeout=5,
                )
            )
        except (pika.exceptions.AMQPError, OSError) as error:
            attempts += 1

            logger.warning(
                "No se pudo conectar con RabbitMQ: %s",
                error,
            )

            if max_attempts is not None and attempts >= max_attempts:
                raise

            time.sleep(wait_seconds)

    raise pika.exceptions.AMQPConnectionError(
        "No se pudo conectar con RabbitMQ"
    )


def crear_canal(
    connection: pika.BlockingConnection,
) -> BlockingChannel:
    """
    Crea un canal, declara la cola y configura un exchange de tipo Topic.

    El exchange de tipo 'topic' permite que todos los workers compitan
    para resolver el desafío de forma asíncrona.

    Args:
        connection (pika.BlockingConnection): La conexión activa a RabbitMQ.

    Returns:
        BlockingChannel: El canal configurado y listo para consumir o publicar mensajes.

    Raises:
        pika.exceptions.AMQPConnectionError: Si el servidor de RabbitMQ no está disponible o rechaza la conexión.
    """
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type=EXCHANGE_TYPE,
        durable=True,
    )
    channel.confirm_delivery()
    return channel