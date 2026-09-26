"""
Modulo para la validacion de los diferentes tipos de transacciones
"""
from Shared.utils.logger import get_logger
from Shared.config import (TipoTransaccion)
import base64
import textwrap
import json
import re
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_ssh_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from uuid import UUID
import math 

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------


def es_clave_publica_valida(clave_publica):
    """
    Valida la clave pública enviada desde el front. 
    Soporta automáticamente formato PEM crudo (Base64) y formato OpenSSH.
    """
    if not clave_publica or not isinstance(clave_publica, str):
        return False

    try:
        # 1. Limpiamos cualquier espacio o salto de línea residual
        clave_limpia = clave_publica.replace(" ", "").replace("\n", "").replace("\r", "")

        # ---------------------------------------------------------
        # CASO A: El usuario subió el archivo .pub original (OpenSSH)
        # ---------------------------------------------------------
        # Si el frontend comprimió algo como "ssh-rsa AAAA... user@host"
        if "ssh-rsa" in clave_limpia or "AAAA" in clave_limpia[:20]:
            # Rescatamos solo la secuencia Base64 pura usando una expresión regular
            match = re.search(r'(AAAA[A-Za-z0-9+/=]+)', clave_limpia)
            if match:
                b64_puro = match.group(1)
                # Reconstruimos el formato exacto que exige la librería para OpenSSH
                clave_ssh = f"ssh-rsa {b64_puro}"
                try:
                    load_ssh_public_key(clave_ssh.encode('utf-8'))
                    return True
                except ValueError:
                    pass # Si no era OpenSSH, ignoramos el error y probamos como PEM

        # ---------------------------------------------------------
        # CASO B: El usuario subió el archivo .pem (PKCS#1 o PKCS#8)
        # ---------------------------------------------------------
        # Reparamos el padding de Base64 por si se perdió algún "=" en la transferencia
        faltante = len(clave_limpia) % 4
        if faltante != 0:
            clave_limpia += "=" * (4 - faltante)

        # Reconstruimos la estructura PEM (máximo 64 caracteres por línea)
        lineas = textwrap.wrap(clave_limpia, 64)
        cuerpo_pem = "\n".join(lineas)
        
        # Probar formato genérico (PKCS#8)
        try:
            pem_format = f"-----BEGIN PUBLIC KEY-----\n{cuerpo_pem}\n-----END PUBLIC KEY-----"
            load_pem_public_key(pem_format.encode('utf-8'))
            return True
        except ValueError:
            # Probar formato específico de RSA (PKCS#1)
            pem_format_rsa = f"-----BEGIN RSA PUBLIC KEY-----\n{cuerpo_pem}\n-----END RSA PUBLIC KEY-----"
            load_pem_public_key(pem_format_rsa.encode('utf-8'))
            return True
            
    except Exception as e:
        # Cualquier otro fallo crítico (datos corruptos, curva no soportada, etc.)
        # print(f"Error crítico validando: {e}")
        logger.error(f"Error interno validando clave: {e}")
        return False
    
def validar_campos_root(datos):
    if not isinstance(datos, dict):
        return False, "El JSON debe ser un objeto."

    esperados = {"data", "type", "sign"}
    recibidos = set(datos)
    if recibidos != esperados:
        return False, (
            f"Campos faltantes: {sorted(esperados - recibidos)}; "
            f"campos no permitidos: {sorted(recibidos - esperados)}"
        )

    if not isinstance(datos["data"], dict):
        return False, "'data' debe ser un objeto."
    if not isinstance(datos["type"], str):
        return False, "'type' debe ser una cadena."
    if not isinstance(datos["sign"], str) or not datos["sign"].strip():
        return False, "'sign' debe ser una cadena no vacía."

    tx_id = datos["data"].get("tx_id")
    if not isinstance(tx_id, str):
        return False, "'data.tx_id' debe ser un UUID v4."
    try:
        identificador = UUID(tx_id)
    except (ValueError, AttributeError):
        return False, "'data.tx_id' no es un UUID válido."
    if identificador.version != 4 or str(identificador) != tx_id:
        return False, "'data.tx_id' debe ser un UUID v4 en formato canónico."

    return True, "OK"
  
  
def validar_tx(data):
    """
    Valida si la transaccion TX es valida

    Formato TX:
        "data": {  
        "monto"  : 2480,
        "origen" : "pub_key_a",
        "destino": "pub_key_b",
        },

    Args:
        data: Valores en el apartado data
    """
    esperadas = {"tx_id", "monto", "origen", "destino"}
    if not isinstance(data, dict) or set(data) != esperadas:
        return False, f"Para TX, 'data' debe contener: {sorted(esperadas)}"

    monto = data["monto"]
    
    if type(monto) not in (int, float):
        return False, "'monto' debe ser un número, no un booleano."
    if isinstance(monto, float) and not math.isfinite(monto):
        return False, "'monto' debe ser finito."
    if monto <= 0:
        return False, "'monto' debe ser mayor que cero."
    if not isinstance(data["origen"], str) or not isinstance(data["destino"], str):
        return False, "'origen' y 'destino' deben ser cadenas."

    return True, "Data válida"
  

def validar_property(data, redis_client=None):
    """
    Valida si la transaccion Property es valida

    Formato Property:
        "data": {  
        "nft"  : "00000000000...",
        "owner": "pub_key_a"
        },

    Args:
        data: Valores en el apartado data
    """
    esperadas = {"tx_id", "nft", "owner"}
    if not isinstance(data, dict) or set(data) != esperadas:
        return False, f"Para PROPERTY, 'data' debe contener: {sorted(esperadas)}"
    if not all(isinstance(data[k], str) and data[k] for k in ("nft", "owner")):
        return False, "'nft' y 'owner' deben ser cadenas no vacías."
    if redis_client is None:
        return False, "No se proporcionó Redis."
    if obtener_propietario_actual_nft(data["nft"], redis_client) is not None:
        return False, "El NFT ya existe en la blockchain."
    return True, "Data válida"

def obtener_propietario_actual_nft(nft, redis_client):
  """
  Devuelve el dueño actual de un NFT consultando la cadena de bloques guardada en Redis
  """
  if redis_client is None:
      logger.debug("Redis client no proporcionado en obtener_propietario_actual_nft")
      return None

  try:
      mensajes = redis_client.getAllTransactions()
      logger.debug(f"Recuperadas {len(mensajes)} transacciones de Redis para nft={nft}")
  except Exception:
      logger.exception("Error leyendo la blockchain para consultar el NFT")
      raise

  def obtener_owner_desde_transaccion(transaccion):
      if not isinstance(transaccion, dict):
          return None

      data = transaccion.get("data")
      if not isinstance(data, dict) or data.get("nft") != nft:
          return None

      tipo = transaccion.get("type")
      if tipo == TipoTransaccion.PROPERTY.value:
          return data.get("owner")

      if tipo == TipoTransaccion.TX_NFT.value:
          return data.get("destino")

      return None

  for idx, msg in enumerate(mensajes):
      logger.debug(f"Procesando mensaje {idx}: tipo={type(msg).__name__}")
      if not isinstance(msg, dict):
          logger.debug("Mensaje ignorado: no es un dict")
          continue

      transacciones = msg.get("transaccion")
      if isinstance(transacciones, list):
          logger.debug(f"Mensaje {idx} contiene 'transaccion' con {len(transacciones)} elementos")
          for sub_idx, transaccion in reversed(list(enumerate(transacciones))):
              owner = obtener_owner_desde_transaccion(transaccion)
              if owner is not None:
                  logger.debug(
                      f"Propietario actual de NFT {nft}: {owner} "
                      f"desde bloque Redis idx={idx}, transaccion idx={sub_idx}"
                  )
                  return owner

      owner = obtener_owner_desde_transaccion(msg)
      if owner is not None:
          logger.debug(f"Propietario actual de NFT {nft}: {owner} desde mensaje root idx={idx}")
          return owner

  logger.debug(f"No se encontro propietario para NFT {nft}")
  return None

def validar_tx_nft(data, redis_client=None):
    """
    Valida si la transaccion TX_NFT es valida

    Formato TX_NFT:
        "data": {  
        "nft"  : "00000000000...",
        "origen" : "pub_key_a",
        "destino": "pub_key_b",
        },

    Args:
        data: Valores en el apartado data
    """
    esperadas = {"tx_id", "nft", "origen", "destino"}
    if not isinstance(data, dict) or set(data) != esperadas:
        return False, f"Para TX_NFT, 'data' debe contener: {sorted(esperadas)}"
    if not all(isinstance(data[k], str) and data[k] for k in ("nft", "origen", "destino")):
        return False, "'nft', 'origen' y 'destino' deben ser cadenas no vacías."
    if redis_client is None:
        return False, "No se proporcionó Redis."

    propietario = obtener_propietario_actual_nft(data["nft"], redis_client)
    if propietario is None:
        return False, "El NFT no existe o todavía no se confirmó."
    if propietario != data["origen"]:
        return False, "El origen no es el dueño actual del NFT."
    return True, "Data válida"
      

def validar_transaccion(datos, redis_client=None):
  """
  Dada una transaccion, se valida si esta cumple con el formato estipulado
  """
  VALIDADORES = {
    TipoTransaccion.TX.value: validar_tx,
    TipoTransaccion.PROPERTY.value: lambda payload: validar_property(payload, redis_client),
    TipoTransaccion.TX_NFT.value: lambda payload: validar_tx_nft(payload, redis_client),
  }

  # VALIDAR DATOS VALIDOS
  ok, msg = validar_campos_root(datos)
  if not ok:
      return False, msg
  
  data = datos["data"]
  type = datos["type"]

  # VALIDAR EL FORMATO
  funcion_validadora = VALIDADORES.get(type)
  if not funcion_validadora:
    return False, "Tipo de transacción no soportado"

  ok, msg = funcion_validadora(data)
  if not ok:
      return False, msg

    # VALIDAR CLAVES PUBLICAS
  if "owner" in data:
    if not es_clave_publica_valida(data["owner"]):
        return False, "Clave publica de owner invalida"

  if "origen" in data:
    if not es_clave_publica_valida(data["origen"]):
        return False, "Clave publica de origen invalida"

  if "destino" in data:
      if not es_clave_publica_valida(data["destino"]):
          return False, "Clave publica de destino invalida"

  # VALIDAR FIRMA CONTRA LA CLAVE DEL EMISOR
  clave_firmante = obtener_clave_firmante(datos)

  if not clave_firmante:
      return False, "No se encontro clave publica firmante"

  if not verificar_firma(data, datos["sign"], clave_firmante):
      return False, "Firma invalida"

  return True, "OK"

def cargar_clave_publica(clave_publica):
    if not clave_publica or not isinstance(clave_publica, str):
        raise ValueError("Clave publica vacia")

    clave_limpia = clave_publica.replace(" ", "").replace("\n", "").replace("\r", "")

    if "ssh-rsa" in clave_limpia or "AAAA" in clave_limpia[:20]:
        match = re.search(r"(AAAA[A-Za-z0-9+/=]+)", clave_limpia)
        if match:
            return load_ssh_public_key(f"ssh-rsa {match.group(1)}".encode("utf-8"))

    faltante = len(clave_limpia) % 4
    if faltante != 0:
        clave_limpia += "=" * (4 - faltante)

    cuerpo_pem = "\n".join(textwrap.wrap(clave_limpia, 64))

    try:
        pem_format = f"-----BEGIN PUBLIC KEY-----\n{cuerpo_pem}\n-----END PUBLIC KEY-----"
        return load_pem_public_key(pem_format.encode("utf-8"))
    except ValueError:
        pem_format_rsa = f"-----BEGIN RSA PUBLIC KEY-----\n{cuerpo_pem}\n-----END RSA PUBLIC KEY-----"
        return load_pem_public_key(pem_format_rsa.encode("utf-8"))


def serializar_data_para_firma(data):
    data_ordenada = {key: data[key] for key in sorted(data.keys())}
    return json.dumps(data_ordenada, separators=(",", ":"), ensure_ascii=False)


def verificar_firma(data, firma_base64, clave_publica):
    try:
        public_key = cargar_clave_publica(clave_publica)
        firma = base64.b64decode(firma_base64)
        mensaje = serializar_data_para_firma(data).encode("utf-8")

        public_key.verify(
            firma,
            mensaje,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )

        return True
    except Exception as e:
        logger.warning(f"Firma invalida: {e}")
        return False


def obtener_clave_firmante(datos):
    data = datos["data"]
    tipo = datos["type"]

    if tipo == TipoTransaccion.PROPERTY.value:
        return data.get("owner")

    return data.get("origen")
