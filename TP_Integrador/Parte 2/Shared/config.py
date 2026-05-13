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
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "grupo03")

# Tipos de transacciones
from enum import Enum

class TipoTransaccion(Enum):
  TX = "TX"
  PROPERTY = "PROPERTY"
  TX_NFT = "TX_NFT"

# Clave para almacenar el bloque en procesamiento en Redis
PROCESSING_BLOCK_KEY = "processing_block"  

# Configuracion para el procesamiento de paquetes
TAMANO_BLOQUE_PROCESAR = 10
PROCESS_INTERVAL = 60  # Deberia ser cada 60 segundos
RABBIT_TIMEOUT = 10

# 2^32 - 1 para alinearse con el tamanio maximo de un 
# entero sin signo de 32 bits, lo que suelen usar los kernels de CUDA 
# evitando errores de overflow durante el calculo del nonce
MAX_RANDOM = 4294967295 

# 7 ceros para tener un equilibrio de dificultad que
# permita demostrar la superioridad de computo de la GPU 
# sin bloquear la capacidad de los nodos CPU de encontrar soluciones
DIFFICULT_PREFIX = "0000000" 

# cadena de 5 caracteres para minimizar el overhead y el almacenamiento en base de datos
STRING_CHAIN = "sdypp" 

# PARAMETROS DE CONTROL 
# tiempo maximo de espera para la resolucion de un desafio 
# 90 segundos es un umbral optimo para entornos cloud permitiendo reasignar tareas si un nodo falla o se desconecta
WORKER_TIMEOUT = 1.5 * 60 

# ventana de observacion para que el algoritmo de ajuste de dificultad sea reactivo
# si los nodos GPU se desconectan,el sistema reduce la exigencia para asegurar la disponibilidad
BLOQUES_MINIMOS_DISMINUIR_PREFIJO = 3 

# si el tiempo de resolucion supera los 30 segundos, se interpreta como una falta de capacidad de procesamiento, 
# reducimos la dificultad para mantener la fluidez del sistema y evitar bloqueos
MINIMO_PROMEDIO_DISMINUIR_PREFIJO = 30