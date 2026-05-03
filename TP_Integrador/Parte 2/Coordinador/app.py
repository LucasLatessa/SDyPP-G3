"""
Punto de entrada principal del sistema.
Inicializa conexiones, rutas y procesos en background.
"""

from flask import Flask
import threading

from messaging.rabbitmq import crear_conexion, crear_canal
from storage.redis import RedisUtils
from api.routes import registrar_rutas
from workers.paquete_processor import procesar_paquetes
from utils.logger import get_logger

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

app = Flask(__name__)
logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            INICIALIZACION
# ----------------------------------------------------------------------

logger.info("Inicializando coordinador...")

connection = crear_conexion()
channel = crear_canal(connection)
redis_client = RedisUtils()

registrar_rutas(app, channel, redis_client)

# ----------------------------------------------------------------------
#                            BACKGROUND
# ----------------------------------------------------------------------

thread = threading.Thread(
    target=procesar_paquetes,
    args=(channel, connection, redis_client),
    daemon=True,
)

thread.start()
logger.info("Thread de procesamiento iniciado")

# ----------------------------------------------------------------------
#                            MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Servidor Flask iniciado")
    app.run(host="0.0.0.0", debug=True)

# if __name__ == "__main__":
#     try:
#         app.run(host="0.0.0.0", debug=True)
#     except KeyboardInterrupt:
#         # Definir una bandera para detener el hilo
#         stop_event = threading.Event()
#         # Solicitar detener el hilo
#         stop_event.set()
#         print("Servidor parado")
