"""
Configuraciones globales del sistema como credenciales, colas y parámetros generales.
"""

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

# Configuración del servidor RabbitMQ
RABBIT_HOST = "localhost"
RABBIT_PORT = 5672
RABBIT_USER = "grupo03"
RABBIT_PASS = "grupo03"

# Configuración de mensajería
QUEUE_NAME = "transacciones"
EXCHANGE_TYPE = "topic"
EXCHANGE_NAME = "block_challenge"
ROUTING_KEY = "blocks"

# Configuracion para el procesamiento de paquetes
TAMANO_BLOQUE_PROCESAR = 10
PROCESS_INTERVAL = 10  # Deberia ser cada 60 segundos
RABBIT_TIMEOUT = 10
MAX_RANDOM = 20000000