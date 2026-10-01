"""
Punto de entrada principal del sistema.
Inicializa conexiones, rutas y procesos en background.
"""

from flask import Flask
from flask_cors import CORS

from Shared.storage.redis import RedisUtils
from Coordinador.api.routes import registrar_rutas
from Shared.utils.logger import get_logger
from Coordinador.processor import iniciar_procesador, detener_procesador

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

registrar_rutas(app, redis_client)


# ----------------------------------------------------------------------
#                            MAIN
# ----------------------------------------------------------------------
if __name__ == "__main__":
    control = iniciar_procesador()

    try:
        logger.info("Servidor Flask iniciado")
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=False,
            use_reloader=False,
        )
    finally:
        detener_procesador(control)

