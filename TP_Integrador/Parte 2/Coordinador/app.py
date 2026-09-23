"""
Punto de entrada principal del sistema.
Inicializa conexiones, rutas y procesos en background.
"""

from flask import Flask
from flask_cors import CORS
import threading

from Shared.storage.redis import RedisUtils
from Coordinador.api.routes import registrar_rutas
from Coordinador.workers.paquete_processor import procesar_paquetes
from Shared.utils.logger import get_logger

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

app = Flask(__name__)
CORS(app)
logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            INICIALIZACION
# ----------------------------------------------------------------------

logger.info("Inicializando coordinador...")

# Redis
redis_client = RedisUtils()
redis_client.inicializar_prefijo()

thread = threading.Thread(
    target=procesar_paquetes,
    args=(redis_client,),
    daemon=True,
)

registrar_rutas(app, redis_client, thread)

# ----------------------------------------------------------------------
#                            BACKGROUND
# ----------------------------------------------------------------------

thread.start()
logger.info("Thread de procesamiento iniciado")

# ----------------------------------------------------------------------
#                            MAIN
# ----------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Servidor Flask iniciado")
    app.run(host="0.0.0.0", debug=False)

# if __name__ == "__main__":
#     try:
#         app.run(host="0.0.0.0", debug=True)
#     except KeyboardInterrupt:
#         # Definir una bandera para detener el hilo
#         stop_event = threading.Event()
#         # Solicitar detener el hilo
#         stop_event.set()
#         print("Servidor parado")
