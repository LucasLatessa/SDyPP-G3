"""
Módulo de rutas para la app principal

Se definen los endpoints que soportara la API
"""

from flask import jsonify, request
from Coordinador.services.blockchain_service import validar_guardar_bloque
from Coordinador.services.validar_transaccion import validar_transaccion
from Shared.config import (
    QUEUE_NAME,
    TipoTransaccion
)
from Shared.utils.logger import get_logger
import json, time

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------


def registrar_rutas(app, channel, redis_client) -> None:
    """
    Registra los endpoints en la aplicación Flask.

    Args:
        app: Aplicacion Flask
        channel: Canal RabbitMQ
        redis_client: Cliente Redis

    """

    "-------------------------------------------------------------------"

    @app.route("/transaccion", methods=["POST"])
    def agregar_transaccion():
        """
        Recibe una transacción y la envía a RabbitMQ.

        Tipo de transacciones:
          - TX: Transaciones
          - PROPERTY: Inicializacion NFT
          - TX_NFT: Transferencia NFT

        Es necesario que el origen y el destino envien su clave publica para realizar la transaccion
        """

        datos = request.get_json()

        # JSON valido
        if isinstance(datos, str):
          try:
              datos = json.loads(datos)
          except json.JSONDecodeError:
              return jsonify({"error": "El formato de los datos no es un JSON válido"}), 400

        #logger.info(f"Transacción recibida: {datos}")
        logger.info("Transacción recibida.")

        # ----------- VALIDACIONES ------------------
           
        ok, message = validar_transaccion(datos)
          
        if not ok:
          logger.error(message)
          return (jsonify({"error": message}), 400)
        
        logger.info("Transaccion valida.")

        # -------------------------------------------

        # Agregar el timestamp si la transaccion es Property
        if datos["type"] == TipoTransaccion.PROPERTY.value:
          logger.info(f"Trnasaccion de tipo de PROPERTY, se agrega timestamp")
          datos["timestamp"] = time.time()
        
        # Mando a la cola de Rabbit
        channel.basic_publish(
            exchange="", routing_key=QUEUE_NAME, body=json.dumps(datos)
        )

        logger.info("Transaccion recibida y encolada en Rabbit")
        return "Transaccion recibida y encolada en Rabbit", 200

    "-------------------------------------------------------------------"

    @app.route("/tarea_worker", methods=["POST"])
    def tarea_worker():
        """
        Recibe un bloque resuelto por un worker.
        """
        data = request.get_json()

        logger.info(f"Bloque recibido ID={data.get('id')}")

        ok, mensaje = validar_guardar_bloque(data, redis_client)

        if ok:
            return jsonify({"mensaje": mensaje}), 201
        else:
            return jsonify({"mensaje": mensaje}), 400
        
    "-------------------------------------------------------------------"
    
    @app.route("/bloques/<block_id>/estado", methods=["GET"])
    def consultar_estado_bloque(block_id):
       """
       Endpoint para los workers, cuando si el bloque que estan trabajando es el correcto
       """
        
       if not redis_client.exists_id(block_id):
          print(block_id)
          return jsonify({"error": "Bloque no encontrado"}), 404
       
       return jsonify({
            "ok": "Bloque resuelto",
        }), 200
    
    "-------------------------------------------------------------------"

    @app.route("/blockchain", methods=["GET"])
    def blockchain():
      blockchain = redis_client.get_ultimos_mensajes()
      logger.info(f"Blochckain:{blockchain}")
      return blockchain


    "-------------------------------------------------------------------"

    @app.route("/status", methods=["GET"])
    def status():
        """
        Estado del servidor.
        """
        logger.info("Healthcheck solicitado")
        return jsonify({"status": "funcionando :D"})
    
    
