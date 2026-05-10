"""
Configuraciones globales del sistema como credenciales, colas y parámetros generales.
"""

import os, sys

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

# Configuración del servidor RabbitMQ
RABBIT_HOST = os.getenv("RABBIT_HOST", "localhost")
RABBIT_PORT = int(os.getenv("RABBIT_PORT", 5672))
RABBIT_USER = os.getenv("RABBIT_USER", "grupo03")
RABBIT_PASS = os.getenv("RABBIT_PASS", "grupo03")

# ------------------ Configuración de mensajería -----------------------

# 1. Cola de transaciones
QUEUE_NAME = "transacciones"

# 2. Cola de bloques
EXCHANGE_TYPE = "topic"
EXCHANGE_NAME = "block_challenge"
ROUTING_KEY = "blocks"
QUEUE_BLOCKS = "block_queue"

# 3. Cola de tareas (Workers)
QUEUE_TASKS = "task_queue"
CHUNK_SIZE = 100000  # Tamaño de cada rango de trabajo

# ----------------------------------------------------------------------

# Configuracion de redis
REDIS_HOST = os.getenv("REDIS_HOST", 'localhost')
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_LIST_KEY_NAME = 'blockchain'

# Tipos de transacciones
from enum import Enum

class TipoTransaccion(Enum):
  TX = "TX"
  PROPERTY = "PROPERTY"
  TX_NFT = "TX_NFT"

# Configuracion para el procesamiento de paquetes
TAMANO_BLOQUE_PROCESAR = 10
PROCESS_INTERVAL = 10  # Deberia ser cada 60 segundos
RABBIT_TIMEOUT = 10
#MAX_RANDOM = 200000000

MAX_RANDOM = sys.maxsize-1 #4294967296
DIFFICULT_PREFIX = "000" #00000000
STRING_CHAIN = "a18b"

WORKER_TIMEOUT = 5 * 60 # 5 minutos
BLOQUES_MINIMOS_DISMINUIR_PREFIJO = 5
MINIMO_PROMEDIO_DISMINUIR_PREFIJO = 1