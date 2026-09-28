from Shared.storage.redis import RedisUtils
from Coordinador.workers.paquete_processor import procesar_paquetes
from Shared.utils.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    logger.info("Iniciando procesador de bloques...")

    redis_client = RedisUtils()
    redis_client.inicializar_prefijo()

    procesar_paquetes(redis_client)