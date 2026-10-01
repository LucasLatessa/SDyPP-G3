"""
Módulo para servicios de la Blockchain.

Provee la lógica de negocio para la validación, procesamiento y
almacenamiento de bloques.
"""

import time
from Shared.utils.hash import calcular_hash_v2
from Shared.utils.logger import get_logger
from Shared.config import WORKER_TIMEOUT, BLOQUES_MINIMOS_DISMINUIR_PREFIJO, MINIMO_PROMEDIO_DISMINUIR_PREFIJO
from Shared.config import (TipoTransaccion)
from Shared.utils.reservas import liberar_reserva
from Shared.utils.dificultad import disminuir_prefijo
# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------

def aumentar_prefijo(redis_client):
    prefijo = redis_client.get_prefijo()
    
    prefijo = prefijo + "0"
    redis_client.set_prefijo(prefijo)
    logger.info(f"Prefijo AUMENTADO actualizado: {prefijo}")

def obtener_tiempo_promedio_ultimos(redis_client, tiempo_bloque_resuelto_actual): 
    bloques = redis_client.get_ultimos_mensajes(count=BLOQUES_MINIMOS_DISMINUIR_PREFIJO)

    if len(bloques) < BLOQUES_MINIMOS_DISMINUIR_PREFIJO:
      return False
  
    sum = tiempo_bloque_resuelto_actual
    for bloque in bloques:
      sum = sum + bloque["tiempo_proceso"]

    tiempo = sum / (BLOQUES_MINIMOS_DISMINUIR_PREFIJO + 1)


    return tiempo < MINIMO_PROMEDIO_DISMINUIR_PREFIJO


def validar_guardar_bloque(data, redis_client) -> tuple[bool, str]:
    """
    Valida la integridad de un bloque recibida por un worker y lo persiste en la base de datos Redis.

    Concatena los componentes del bloque para recrear su cadena base y calcula
    el hash MD5 local. Este hash local debe usarse para validar la integridad
    de los datos antes de proceder a guardarlos.

    Args:
        data: Diccionario con la información del bloque. Debe
            contener obligatoriamente las claves 'numero', 'base_string_chain'
            y 'blockchain_content'.
        redis (Redis): Instancia de conexión activa a la base de datos Redis.

    Returns:
        bool: True si el bloque fue validado y guardado exitosamente,
        False en caso contrario.
        str:  Mensaje con el resultado
    """

    datos = f"{data['numero']}{data['base_string_chain']}{data['blockchain_content']}"

    hash_local = calcular_hash_v2(datos)

    logger.info(f"Bloque recibido. Validando bloque ID={data['id']}")

    if data["hash"] != hash_local:
        #print("El hash es invalido. Termina la ejecucion!")
        logger.warning(f"Hash inválido para bloque ID={data['id']}. Bloque descartado")
        return False, "Hash inválido. Bloque descartado"

    if redis_client.exists_id(data["id"]):
        #print("El bloque esta duplicado. Termina la ejecucion!")
        logger.warning(f"Bloque duplicado ID={data['id']}. Bloque descartado")
        return False, "Bloque duplicado. Bloque descartado"

    if not data["hash"].startswith(data["prefix"]):
        return False, "El hash no cumple la dificultad del bloque"

    estado = redis_client.get_bloque_en_proceso()
    if not estado or estado.get("id") != data["id"]:
        return False, "El bloque no es el que está en proceso"

    desafio = estado.get("block") or {}

    for campo in (
        "transaccion",
        "prefix",
        "base_string_chain",
        "blockchain_content",
    ):
        if data.get(campo) != desafio.get(campo):
            return False, f"El campo {campo} no coincide con el desafío"

    ultimo = redis_client.get_ultimo()
    hash_previo_actual = ultimo["hash"] if ultimo else "None"

    if desafio.get("previous_block_hash") != hash_previo_actual:
        redis_client.marcar_reproceso_bloque("STALE_HEAD")
        return False, "La punta cambió; hay que volver a minar el bloque"

    if ultimo and data["blockchain_content"] != ultimo["blockchain_content"]:
        redis_client.marcar_reproceso_bloque("STALE_HEAD")
        return False, "El bloque fue minado sobre una punta anterior"

    # Si el worker paso el tiempo maximo estipulado, disminuimos el prefijo para los bloques siguientes
    if data["tiempo_proceso"] > WORKER_TIMEOUT:
        disminuir_prefijo(redis_client)

    # Aumenta el prefijo si de los 5 bloques anteriores y el actual fue inferior al promedio (5 min)
    elif obtener_tiempo_promedio_ultimos(redis_client, data["tiempo_proceso"]):
        aumentar_prefijo(redis_client)

    # Le calculo el hash
    #blockchain_data = f'{data["base_string_chain"]}{data["hash"]}'
    blockchain_data = f"{data['base_string_chain']}{data['hash']}"
    blockchain_content = calcular_hash_v2(blockchain_data)

    # Obtengo el bloque anterior para conectar, si no hay quiere decir que este es el origen
    data["previous_block"] = hash_previo_actual
    logger.info("Hash bloque previo %s", hash_previo_actual)

    data["timestamp"] = time.time()
    data["blockchain_content"] = blockchain_content

    #print("Bloque final")
    #print(data)
    logger.info(f"Bloque agregado correctamente ID={data['id']}")

    redis_client.publicar(data)
    redis_client.limpiar_bloque_en_proceso(data["id"])

    # LIBERACION DE LOCKS
    transacciones = data.get("transaccion", [])
    for tx in transacciones:
        # Si la transaccion era de tipo PROPERTY
        if tx.get("type") in (TipoTransaccion.PROPERTY.value, TipoTransaccion.TX_NFT.value):
            nft_id = tx["data"]["nft"]
            token = tx.get("_lock_token")
            if token:
                liberar_reserva(redis_client.redis_client,f"lock:nft:{nft_id}",token,)

    return True, "Bloque agregado"
