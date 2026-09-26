"""
Módulo de rutas para la app principal

Se definen los endpoints que soportara la API
"""

from flask import jsonify, request
import pika
from Shared.messaging.rabbitmq import crear_conexion, crear_canal
from Coordinador.services.blockchain_service import validar_guardar_bloque
from Coordinador.services.validar_transaccion import validar_transaccion
from Shared.config import (
    QUEUE_NAME,
    TipoTransaccion
)
from Shared.utils.logger import get_logger
import json, time
from uuid import uuid4
from redis.exceptions import RedisError
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
from Shared.utils.reservas import liberar_reserva
from Coordinador.services.validar_transaccion import (
    validar_transaccion,
    validar_property,
    validar_tx_nft,
)

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------


def registrar_rutas(app, redis_client, processor_thread) -> None:
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

        try:
            datos = request.get_json()
        except (BadRequest, UnsupportedMediaType):
            return jsonify({"error": "Se requiere un objeto JSON válido."}), 400

        r = redis_client.redis_client
        token = str(uuid4())
        reservas = []
        connection = None
        publicacion_iniciada = False
        publicacion_confirmada = False
        rechazo_confirmado = False

        try:
            # Los validadores de la sección 2 sólo leen Redis.
            ok, mensaje = validar_transaccion(datos, redis_client)
            if not ok:
                return jsonify({"error": mensaje}), 400

            tx_id = datos["data"]["tx_id"]
            clave_tx = f"tx:aceptada:{tx_id}"

            # Sin TTL: también debe impedir un replay después del minado.
            if not r.set(clave_tx, token, nx=True):
                return jsonify({
                    "error": "La transacción ya fue recibida o está pendiente.",
                    "tx_id": tx_id,
                }), 409
            reservas.append(clave_tx)

            es_nft = datos["type"] in (
                TipoTransaccion.PROPERTY.value,
                TipoTransaccion.TX_NFT.value,
            )
            if es_nft:
                clave_nft = f"lock:nft:{datos['data']['nft']}"
                if not r.set(clave_nft, token, nx=True, ex=600):
                    return jsonify({"error": "El NFT tiene una operación pendiente."}), 409
                reservas.append(clave_nft)

                # Reconsultar el propietario después de adquirir la reserva.
                validador = (
                    validar_property
                    if datos["type"] == TipoTransaccion.PROPERTY.value
                    else validar_tx_nft
                )
                ok, mensaje = validador(datos["data"], redis_client)
                if not ok:
                    return jsonify({"error": mensaje}), 409

            mensaje = dict(datos)
            if es_nft:
                mensaje["_lock_token"] = token
            if datos["type"] == TipoTransaccion.PROPERTY.value:
                mensaje["timestamp"] = time.time()
            body = json.dumps(mensaje, ensure_ascii=False, allow_nan=False)

            connection = crear_conexion(max_attempts=3, wait_seconds=1)
            channel = crear_canal(connection)
            # crear_canal ya activa confirm_delivery() en este proyecto.
            publicacion_iniciada = True
            channel.basic_publish(
                exchange="",
                routing_key=QUEUE_NAME,
                body=body,
                mandatory=True,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type="application/json",
                    message_id=tx_id,
                ),
            )
            publicacion_confirmada = True
            return jsonify({"mensaje": "Transacción recibida y encolada", "tx_id": tx_id}), 200

        except (pika.exceptions.UnroutableError, pika.exceptions.NackError):
            rechazo_confirmado = True
            logger.exception("RabbitMQ rechazó la publicación")
            return jsonify({"error": "No se pudo encolar la transacción."}), 503
        except (RedisError, pika.exceptions.AMQPError, OSError):
            logger.exception("Fallo de infraestructura al recibir la transacción")
            return jsonify({
                "error": "No se pudo confirmar la operación. Conservá el mismo tx_id para consultar o reintentar."
            }), 503
        except Exception:
            logger.exception("Error inesperado al recibir la transacción")
            return jsonify({"error": "Error interno al procesar la transacción."}), 500
        finally:
            # Liberar sólo si sabemos que el mensaje no quedó publicado.
            # Una desconexión durante basic_publish puede dejar resultado incierto.
            if not publicacion_confirmada and (
                not publicacion_iniciada or rechazo_confirmado
            ):
                for clave in reversed(reservas):
                    try:
                        liberar_reserva(r, clave, token)
                    except RedisError:
                        logger.exception("No se pudo liberar la reserva %s", clave)
            if connection is not None and connection.is_open:
                try:
                    connection.close()
                except Exception:
                    logger.exception("No se pudo cerrar la conexión RabbitMQ")

    "-------------------------------------------------------------------"

    @app.route("/tarea_worker", methods=["POST"])
    def tarea_worker():
        """
        Recibe un bloque resuelto por un worker.
        """
        data = request.get_json()

        logger.info(f"Bloque recibido ID={data.get('id')}")

        if data.get("found") is False:
            registrado = redis_client.registrar_tarea_sin_solucion(
                block_id=data["id"],
                start=data["start"],
                end=data["end"],
                worker_id=data.get("worker_id"),
            )

            if not registrado:
                return jsonify({"mensaje": "La tarea no coincide con el bloque en proceso"}), 409

            return jsonify({"mensaje": "Tarea registrada sin solucion"}), 200


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
          #print(block_id)
          redis_client.actualizar_updated_at(block_id)
          logger.info("Bloque no resuelto. Actualizando updated_at")
          return jsonify({"error": "Bloque no encontrado"}), 404
       
       return jsonify({
            "ok": "Bloque resuelto",
        }), 200
    
    "-------------------------------------------------------------------"

    @app.route("/blockchain", methods=["GET"])
    def blockchain():
      blockchain = redis_client.get_ultimos_mensajes()
      #logger.info(f"Blochckain:{blockchain}")
      return blockchain
  
    "-------------------------------------------------------------------"

    @app.route("/prefijo", methods=["GET"])
    def prefijo():
      prefijo = redis_client.get_prefijo()

      #logger.info(f"Blochckain:{blockchain}")
      return prefijo


    "-------------------------------------------------------------------"

    @app.route("/status", methods=["GET"])
    def status():
        """
        Estado completo del servicio y sus dependencias críticas.
        """
        dependencies = {}

        try:
            redis_client.redis_client.ping()
            dependencies["redis"] = "ok"
        except Exception as e:
            dependencies["redis"] = "error"
            logger.warning("Healthcheck Redis falló: %s", e)

        rabbit_connection = None

        try:
            rabbit_connection = crear_conexion(
                max_attempts=1,
                wait_seconds=0,
            )
            rabbit_ok = rabbit_connection.is_open

        except Exception as error:
            rabbit_ok = False
            logger.warning(
                "Healthcheck RabbitMQ fallo: %s",
                error,
            )

        finally:
            if (
                rabbit_connection is not None
                and rabbit_connection.is_open
            ):
                rabbit_connection.close()

        dependencies["rabbitmq"] = (
            "ok" if rabbit_ok else "error"
        )

        dependencies["processor"] = (
            "running" if processor_thread.is_alive() else "stopped"
        )

        healthy = (
            dependencies["redis"] == "ok"
            and dependencies["rabbitmq"] == "ok"
            and dependencies["processor"] == "running"
        )
        payload = {
            "status": "ok" if healthy else "degraded",
            "dependencies": dependencies,
        }

        logger.info(
            "Healthcheck completo: status=%s dependencies=%s",
            payload["status"],
            dependencies,
        )
        return jsonify(payload), 200 if healthy else 503

    @app.route("/status/live", methods=["GET"])
    def status_live():
        """Comprueba únicamente que Flask está atendiendo requests."""
        return jsonify({"status": "alive"}), 200
    
