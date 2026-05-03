"""
Procesamiento en segundo plano de paquetes de transacciones.
"""

import json
import random
import time
from config import (
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
from utils.logger import get_logger

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------


def procesar_paquetes(channel, connection, redis_client) -> None:
    """
    Procesa paquetes de transacciones y los envia a RabbitMQ

    Args:
        channel: Canal de RabbitMQ
        connection: Conexion con RabbitMQ
        redis_client: Cliente Redis
    """
    while True:
        try:
            paquete = []  # Almacenar los mensajes del paquete actual

            # Procesa en bloques
            for _ in range(TAMANO_BLOQUE_PROCESAR):

                # Obtener un mensaje de la cola 'transactions' de RabbitMQ
                method_frame, header_frame, body = channel.basic_get(
                    queue=QUEUE_NAME, auto_ack=False
                )

                if method_frame:

                    # Añadir el mensaje al paquete
                    paquete.append(json.loads(body))

                    # Confirmar que el mensaje ha sido recibido y procesado (acknowledge)
                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                else:
                    break  # No hay más mensajes disponibles, salir del bucle

            """ 
            TO-DO:
         
            AGREGAR MANEJO DE PAQUETES NO PROCESADOS!!!!!!!!!!!!!! -> SI NO SE PROCESO EL PAQUETE ENTONCES REENVIO, 
            EL COORDINADOR NO LE IMPORTA LA CANTIDAD DE WORKERS QUE HAY CONSUMIENDO!
            """

            if paquete:
                logger.info(f"Procesando paquete de {len(paquete)} transacciones")
                # Añadir metadatos al paquete del bloque

                # Obtener los últimos mensajes de Redis
                tail_elements = (redis_client.get_ultimos_mensajes()) 

                # Obtener el último elemento de la lista en Redis
                last_element = (redis_client.get_ultimo())

                bloque = {
                    "id": str(random.randint(0, MAX_RANDOM)),
                    "transaccion": paquete,
                    "prefix": DIFFICULT_PREFIX,  # Dificulta de tres 0 -> Buscar el quiebre
                    "base_string_chain": STRING_CHAIN,  # Es lo que concateno para el hash, que tiene que arrancar con el prefijo
                    "blockchain_content": (
                        last_element["blockchain_content"] if last_element else "[]"
                    ),  # Contenido de la cadena de bloques hasta el bloque anterior
                    "max_random": MAX_RANDOM,  # Random usado en la prueba de trabajo
                }

                # Mando el bloque al Topic de Rabbit
                channel.basic_publish(
                    exchange=EXCHANGE_NAME,
                    routing_key=ROUTING_KEY,
                    body=json.dumps(bloque),
                    mandatory=True,
                )

                logger.info(f"Bloque enviado ID={bloque['id']}")

                # TO-DO: Manejo de workers caidos
                # global message_returned
                # message_returned = False
                # # Manejo de paquetes devueltos

                start = time.time()
                while time.time() - start < RABBIT_TIMEOUT:
                    connection.process_data_events()
                    time.sleep(1)

            #print(f"Pasaron {PROCESS_INTERVAL} segundos, procesamiento de paquetes")
            logger.info(f"Pasaron {PROCESS_INTERVAL} segundos, procesamiento de paquetes")
            time.sleep(PROCESS_INTERVAL)
        except Exception as e:
            logger.error(f"Error en procesamiento de paquetes: {e}")
            time.sleep(5)
            #print(f"Error en procesamiento: {e}")
