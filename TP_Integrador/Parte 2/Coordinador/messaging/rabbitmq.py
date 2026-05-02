"""
Módulo de conexión y configuración de RabbitMQ.

Provee utilidades para establecer la conexión con el broker de mensajería
y configurar los canales, colas y exchanges necesarios para el sistema
distribuido de transacciones.
"""

import pika
from config import (
    RABBIT_HOST,
    RABBIT_PORT,
    RABBIT_USER,
    RABBIT_PASS,
    QUEUE_NAME,
    EXCHANGE_TYPE,
    EXCHANGE_NAME
)
from pika.adapters.blocking_connection import BlockingChannel

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------

def crear_conexion() -> pika.BlockingConnection:
    """
    Establece y retorna una conexión con el servidor RabbitMQ. Es necesario tener host, puerto y credenciales definidas.

    Returns:
        pika.BlockingConnection: Objeto de conexión bloqueante hacia RabbitMQ
        configurado con las credenciales por defecto.
    """

    try:
      return pika.BlockingConnection(
          pika.ConnectionParameters(
              host=RABBIT_HOST,
              port=RABBIT_PORT,
              credentials=pika.PlainCredentials(RABBIT_USER, RABBIT_PASS),
          )
      )
    except Exception as e:
       print(e)


def crear_canal(connection: pika.BlockingConnection) -> BlockingChannel:
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
        exchange=EXCHANGE_NAME, exchange_type=EXCHANGE_TYPE, durable=True
    )
    return channel