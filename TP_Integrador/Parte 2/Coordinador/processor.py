from Shared.storage.redis import RedisUtils
from Coordinador.workers.paquete_processor import (
    LiderazgoPerdido,
    procesar_paquetes,
)
from Shared.utils.logger import get_logger
import threading
from redis.exceptions import LockError

logger = get_logger(__name__)

PROCESSOR_LOCK = "lock:block-processor:leader"
LOCK_TTL = 30
LOCK_RENEW_INTERVAL = 10
RETRY_INTERVAL = 5


def renovar_liderazgo(lock, detener, finalizar):
    while not detener.wait(LOCK_RENEW_INTERVAL):
        if finalizar.is_set():
            return

        try:
            lock.extend(LOCK_TTL, replace_ttl=True)
        except Exception:
            logger.exception("Se perdió el liderazgo del procesador")
            detener.set()
            return


def ejecutar_con_failover(finalizar):
    redis_client = RedisUtils()

    while not finalizar.is_set():
        lock = None
        adquirido = False
        detener = threading.Event()
        renovador = None

        try:
            lock = redis_client.redis_client.lock(
                PROCESSOR_LOCK,
                timeout=LOCK_TTL,
                blocking_timeout=0,
                thread_local=False,
            )

            adquirido = lock.acquire(blocking=False)

            if not adquirido:
                logger.info(
                    "Procesador en espera: otro coordinador es líder"
                )
                finalizar.wait(RETRY_INTERVAL)
                continue

            logger.info("Este coordinador es líder del procesador")

            renovador = threading.Thread(
                target=renovar_liderazgo,
                args=(lock, detener, finalizar),
                name="renovador-lock-procesador",
                daemon=True,
            )
            renovador.start()

            procesar_paquetes(redis_client, lock, detener, finalizar)

        except LiderazgoPerdido:
            logger.info(
                "Procesador detenido por pérdida de liderazgo o cierre"
            )

        except Exception:
            logger.exception("Error del procesador; se reintentará")

        finally:
            detener.set()

            if renovador is not None and renovador.is_alive():
                renovador.join(timeout=2)

            if adquirido:
                try:
                    lock.release()
                except LockError:
                    # El lock expiró o pertenece a otra réplica.
                    pass
                except Exception:
                    logger.exception(
                        "No se pudo liberar el lock del procesador"
                    )

        finalizar.wait(RETRY_INTERVAL)


def iniciar_procesador():
    finalizar = threading.Event()

    hilo = threading.Thread(
        target=ejecutar_con_failover,
        args=(finalizar,),
        name="procesador-bloques",
        daemon=True,
    )

    hilo.start()
    return finalizar, hilo


def detener_procesador(control):
    finalizar, hilo = control
    finalizar.set()
    hilo.join(timeout=5)