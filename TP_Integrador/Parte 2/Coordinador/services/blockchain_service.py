"""
Módulo para servicios de la Blockchain.

Provee la lógica de negocio para la validación, procesamiento y
almacenamiento de bloques.
"""

import time
from utils.hash import calcular_hash_v2


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

    print("---------------------------")
    print("    ¡BLOQUE RECIBIDO!      ")
    print("---------------------------")
    print(f"Hash recibidos: {data["hash"]}")
    print(f"Hash calculado de forma local: {hash}")

    if data["hash"] != hash_local:
        print("El hash es invalido. Termina la ejecucion!")
        return False, "Hash inválido"

    if redis_client.exists_id(data["id"]):
        print("El bloque esta duplicado. Termina la ejecucion!")
        return False, "Bloque duplicado"

    # Logica del armado del bloque
    print("Los bloques coinciden!")
    print("---------------------------")
    print("Vamos a agregar el bloque a la cadena")
    print(f"Hash:  {data["hash"]}")
    print(f"Contenido del bloque anterior: {data["blockchain_content"]}")

    # Le calculo el hash
    blockchain_data = f"{data["base_string_chain"]}{data["hash"]}"
    blockchain_content = calcular_hash_v2(blockchain_data)

    # Obtengo el bloque anterior para conectar, si no hay quiere decir que este es el origen
    try:
        bloque_previo = redis_client.get_ultimo()
    except:
        bloque_previo = None

    if bloque_previo:
        print(f"Hash del bloque previo:  {bloque_previo["hash"]}")
        data["previous_block"] = bloque_previo["hash"]
    else:
        print(f"Hash del bloque previo: None")
        data["previous_block"] = "None"

    data["timestamp"] = time.time()
    data["blockchain_content"] = blockchain_content

    print("Bloque final")
    print(data)

    redis_client.publicar(data)

    return True, "Bloque agregado"
