"""
Configuraciones globales del sistema como credenciales, colas y parámetros generales.
"""

import os

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

# Configuración del servidor RabbitMQ
RABBIT_HOST = os.getenv("RABBIT_HOST", "localhost")
RABBIT_PORT = int(os.getenv("RABBIT_PORT", 5672))
RABBIT_USER = os.getenv("RABBIT_USER", "grupo03")
RABBIT_PASS = os.getenv("RABBIT_PASS", "grupo03")

# Configuración de mensajería
QUEUE_NAME = "transacciones"
EXCHANGE_TYPE = "topic"
EXCHANGE_NAME = "block_challenge"
ROUTING_KEY = "blocks"

# Configuracion de redis
REDIS_HOST = os.getenv("REDIS_HOST", 'localhost')
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_LIST_KEY_NAME = 'blockchain'

# Configuracion para el procesamiento de paquetes
TAMANO_BLOQUE_PROCESAR = 10
PROCESS_INTERVAL = 10  # Deberia ser cada 60 segundos
RABBIT_TIMEOUT = 10
MAX_RANDOM = 20000000
DIFFICULT_PREFIX = "0"
STRING_CHAIN = "papa"