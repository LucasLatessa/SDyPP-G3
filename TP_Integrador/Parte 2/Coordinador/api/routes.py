"""
Módulo de rutas para la app principal

Se definen los endpoints que soportara la API
"""

from flask import json, jsonify, request
from Coordinador.services.blockchain_service import validar_guardar_bloque
from Shared.config import (
    QUEUE_NAME,
)
from Shared.utils.logger import get_logger

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
        """

        data = request.get_json()

        logger.info(f"Transacción recibida: {data}")

        campos_requeridos = ["origen", "destino", "monto"]
        if not all(field in data for field in campos_requeridos):
            logger.error("Faltan campos en la transaccion. Solicitud denegada")
            return (
                jsonify(
                    {
                        "error": "Solicitud denegada. Faltan campos en la transaccion. Los campos deben ser: origen, destino, monto."
                    }
                ),
                400,
            )

        # print(f"Transaccion recibida: {data} ")

        # Mando a la cola de Rabbit
        channel.basic_publish(
            exchange="", routing_key=QUEUE_NAME, body=json.dumps(data)
        )

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
        
       if not redis_client.exists_id(block_id):
          print(block_id)
          return jsonify({"error": "Bloque no encontrado"}), 404
       
       return jsonify({
            "ok": "Bloque resuelto",
        }), 200

    "-------------------------------------------------------------------"

    @app.route("/status", methods=["GET"])
    def status():
        """
        Estado del servidor.
        """
        logger.info("Healthcheck solicitado")
        return jsonify({"status": "funcionando :D"})
    
    
