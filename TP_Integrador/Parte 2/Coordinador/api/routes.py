"""
Módulo de rutas para la app principal

Se definen los endpoints que soportara la API
"""

from flask import jsonify, request
import pika
from Shared.messaging.rabbitmq import crear_conexion, crear_canal
from Coordinador.services.blockchain_service import validar_guardar_bloque
from Coordinador.services.validar_transaccion import validar_transaccion
from Shared.config import ( QUEUE_NAME,
    QUEUE_BLOCKS,
    QUEUE_TASKS,
    REDIS_LIST_KEY_NAME,
    PROCESSING_BLOCK_KEY,
    TipoTransaccion,
)
from Shared.utils.logger import get_logger
import json, time
from uuid import uuid4
from redis.exceptions import RedisError, LockError
from werkzeug.exceptions import BadRequest, UnsupportedMediaType
from Shared.utils.reservas import liberar_reserva
from Coordinador.services.validar_transaccion import (
    validar_transaccion,
    validar_property,
    validar_tx_nft,
)
import os
import secrets

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

WORKER_API_TOKEN = os.getenv("WORKER_API_TOKEN", "").strip()
if not WORKER_API_TOKEN:
    raise RuntimeError("Falta configurar WORKER_API_TOKEN")

logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------


def registrar_rutas(app, redis_client) -> None:
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
            logger.info("Datos recibidos: %s", datos)
        except (BadRequest, UnsupportedMediaType):
            logger.error("Error al recibir la transaccion: Se requiere un objeto JSON válido.")
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
            logger.info("Transaccion encolada tx_id=%s", tx_id)
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
        esquema, _, token = request.headers.get("Authorization", "").partition(" ")

        if ( esquema.lower() != "bearer" or not token
            or not secrets.compare_digest(
                token.encode("utf-8"),
                WORKER_API_TOKEN.encode("utf-8") )
        ):
            return (
                jsonify({"error": "Token de worker inválido o ausente"}),
                401,
                {"WWW-Authenticate": "Bearer"},
            )
        
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "Se requiere un JSON válido."}), 400

        block_id = data.get("id")

        if not isinstance(block_id, str) or not block_id:
            return jsonify({"error": "Falta un id de bloque válido."}), 400

        if data.get("found") is False:
            requeridos = {"id", "found", "start", "end"}
        else:
            requeridos = {
                "id",
                "found",
                "numero",
                "base_string_chain",
                "blockchain_content",
                "hash",
                "prefix",
                "tiempo_proceso",
                "transaccion",
            }

        faltantes = requeridos - set(data)

        if faltantes:
            return jsonify({
                "error": f"Faltan campos: {sorted(faltantes)}"
            }), 400

        lock = redis_client.redis_client.lock(
            f"lock:resultado:{block_id}",
            timeout=30,
            blocking_timeout=3,
        )

        if not lock.acquire():
            return jsonify({
                "mensaje": "Otro resultado de este bloque está siendo procesado."
            }), 409

        try:
            logger.info(f"Bloque recibido ID={block_id}")

            if data["found"] is False:
                registrado = redis_client.registrar_tarea_sin_solucion(
                    block_id=block_id,
                    start=data["start"],
                    end=data["end"],
                    worker_id=data.get("worker_id"),
                )

                if not registrado:
                    return jsonify({
                        "mensaje": "La tarea no coincide con el bloque en proceso"
                    }), 409

                return jsonify({
                    "mensaje": "Tarea registrada sin solución"
                }), 200

            ok, mensaje = validar_guardar_bloque(data, redis_client)

            if ok:
                return jsonify({"mensaje": mensaje}), 201

            return jsonify({"mensaje": mensaje}), 400

        finally:
            try:
                if lock.owned():
                    lock.release()
            except LockError:
                logger.warning(
                    "Se perdió o venció el lock del bloque %s",
                    block_id,
                )
        
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
        checks = {
            "redis": {"status": "error"},
            "rabbitmq": {"status": "error"},
            "block_processor": {"status": "error"},
            "pool_manager": {"status": "error"},
            "workers": {"status": "error", "active": 0},
            "blockchain": {"status": "error"},
        }

        rabbit_connection = None

        # ---------------------------------------------------------------
        # Redis, Block Processor, Pool Manager y blockchain
        # ---------------------------------------------------------------
        try:
            r = redis_client.redis_client

            r.ping()

            # También comprueba que Redis permita escribir.
            if not r.set(
                "health:coordinator",
                str(time.time()),
                ex=30,
            ):
                raise RuntimeError("Redis no permitió escribir")

            checks["redis"] = {
                "status": "ok",
            }

            # El lock ya existe en la implementación actual.
            pool_leader = bool(
                r.exists("lock:pool-manager:leader")
            )

            checks["pool_manager"] = {
                "status": "ok" if pool_leader else "error",
                "leader": pool_leader,
            }

            # Heartbeat del Block Processor.
            processor_raw = r.get("health:block-processor")

            processor_age = None
            processor_ok = False

            if processor_raw:
                processor_timestamp = float(processor_raw)
                processor_age = time.time() - processor_timestamp
                processor_ok = processor_age <= 120

            checks["block_processor"] = {
                "status": "ok" if processor_ok else "error",
                "age_seconds": (
                    round(processor_age, 2)
                    if processor_age is not None
                    else None
                ),
            }

            prefix_raw = r.get("prefix_key")
            prefix = (
                prefix_raw.decode("utf-8")
                if isinstance(prefix_raw, bytes)
                else prefix_raw
            )

            checks["blockchain"] = {
                "status": "ok" if prefix else "error",
                "blocks": r.llen(REDIS_LIST_KEY_NAME),
                "prefix": prefix,
                "processing_block": bool(
                    r.exists(PROCESSING_BLOCK_KEY)
                ),
            }

        except Exception as error:
            checks["redis"] = {
                "status": "error",
                "error": str(error),
            }

            logger.warning(
                "Healthcheck Redis falló: %s",
                error,
            )

        # ---------------------------------------------------------------
        # RabbitMQ, colas y workers
        # ---------------------------------------------------------------
        try:
            rabbit_connection = crear_conexion(
                max_attempts=1,
                wait_seconds=0,
            )

            channel = rabbit_connection.channel()

            queues = {}

            for queue_name in (
                QUEUE_NAME,
                QUEUE_BLOCKS,
                QUEUE_TASKS,
            ):
                result = channel.queue_declare(
                    queue=queue_name,
                    passive=True,
                )

                queues[queue_name] = {
                    "messages": result.method.message_count,
                    "consumers": result.method.consumer_count,
                }

            active_workers = queues[QUEUE_TASKS]["consumers"]

            checks["rabbitmq"] = {
                "status": "ok",
                "queues": queues,
            }

            checks["workers"] = {
                "status": "ok" if active_workers > 0 else "error",
                "active": active_workers,
            }

        except Exception as error:
            checks["rabbitmq"] = {
                "status": "error",
                "error": str(error),
            }

            logger.warning(
                "Healthcheck RabbitMQ falló: %s",
                error,
            )

        finally:
            if (
                rabbit_connection is not None
                and rabbit_connection.is_open
            ):
                rabbit_connection.close()

        # ---------------------------------------------------------------
        # Resultado general
        # ---------------------------------------------------------------
        system_ok = all(
            check["status"] == "ok"
            for check in checks.values()
        )

        payload = {
            "status": "ok" if system_ok else "degraded",
            "checks": checks,
        }

        return jsonify(payload), 200 if system_ok else 503

    @app.route("/status/live", methods=["GET"])
    def status_live():
        """Comprueba únicamente que Flask está atendiendo requests."""
        return jsonify({"status": "alive"}), 200
    
