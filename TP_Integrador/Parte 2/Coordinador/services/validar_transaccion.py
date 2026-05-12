"""
Modulo para la validacion de los diferentes tipos de transacciones
"""
from Shared.utils.logger import get_logger
from Shared.config import (TipoTransaccion)
import base64
import textwrap
from cryptography.hazmat.primitives.serialization import load_pem_public_key

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------

import re
import textwrap
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_ssh_public_key

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
  campos_permitidos = {"data", "type", "sign"}

  campos_recibidos = set(datos.keys())

  if campos_recibidos != campos_permitidos:
      extra = campos_recibidos - campos_permitidos
      faltantes = campos_permitidos - campos_recibidos

      if extra:
          return False, f"Campos no permitidos: {list(extra)}"
      if faltantes:
          return False, f"Faltan campos obligatorios: {list(faltantes)}"

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
  claves_esperadas = {"monto", "origen", "destino"}
  claves_recibidas = set(data.keys())

  if claves_recibidas != claves_esperadas:
      return False, f"Para el tipo TX, 'data' debe contener exactamente: {claves_esperadas}"
  
  if not isinstance(data.get("monto"), (int, float)):
      return False, "'monto' debe ser un número."
  if not isinstance(data.get("origen"), str) or not isinstance(data.get("destino"), str):
      return False, "'origen' y 'destino' deben ser cadenas de texto."
      
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
  claves_esperadas = {"nft", "owner"}
  claves_recibidas = set(data.keys())
  
  if claves_recibidas != claves_esperadas:
      return False, f"Para el tipo PROPERTY, 'data' debe contener exactamente: {claves_esperadas}"
      
  if not isinstance(data.get("nft"), str) or not isinstance(data.get("owner"), str):
      return False, "'nft' y 'owner' deben ser cadenas de texto."

  if redis_client is None:
      return False, "No se proporcionó el cliente Redis para validar PROPERTY"

  propietario_actual = obtener_propietario_actual_nft(data["nft"], redis_client)
  if propietario_actual is not None:
      return False, f"El NFT {data['nft']} ya está registrado a nombre de otro usuario"
      
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
  except Exception as e:
      logger.error(f"Error leyendo transacciones de Redis: {e}")
      return None

  propietario_actual = None
  mejor_puntaje = None

  def calcular_puntaje(mensaje, indice_tx):
      numero = mensaje.get("numero")
      timestamp = mensaje.get("timestamp")
      try:
          numero = int(numero) if numero is not None else None
      except (TypeError, ValueError):
          numero = None
      try:
          timestamp = float(timestamp) if timestamp is not None else None
      except (TypeError, ValueError):
          timestamp = None
      return (
          numero if numero is not None else -1,
          timestamp if timestamp is not None else -1.0,
          indice_tx,
      )

  for idx, msg in enumerate(mensajes):
      logger.debug(f"Procesando mensaje {idx}: tipo={type(msg).__name__}")
      if not isinstance(msg, dict):
          logger.debug("Mensaje ignorado: no es un dict")
          continue

      transacciones = msg.get("transaccion")
      if isinstance(transacciones, list):
          logger.debug(f"Mensaje {idx} contiene 'transaccion' con {len(transacciones)} elementos")
          for sub_idx, transaccion in enumerate(transacciones):
              if not isinstance(transaccion, dict):
                  logger.debug(f"Transacción interna {sub_idx} ignorada: no es un dict")
                  continue
              data = transaccion.get("data")
              if not isinstance(data, dict):
                  logger.debug(f"Transacción interna {sub_idx} ignorada: data no es dict")
                  continue
              logger.debug(f"Transacción interna {sub_idx} nft={data.get('nft')} tipo={transaccion.get('type')}")
              if data.get("nft") != nft:
                  continue

              tipo = transaccion.get("type")
              if tipo not in (TipoTransaccion.TX_NFT.value, TipoTransaccion.PROPERTY.value):
                  continue
              owner = data.get("destino") if tipo == TipoTransaccion.TX_NFT.value else data.get("owner")
              puntaje = calcular_puntaje(msg, sub_idx)
              logger.debug(f"Candidato encontrado owner={owner} puntaje={puntaje}")
              if mejor_puntaje is None or puntaje > mejor_puntaje:
                  mejor_puntaje = puntaje
                  propietario_actual = owner
                  logger.debug(f"Propietario actualizado a {owner} desde mensaje {idx} transacción {sub_idx}")

      data = msg.get("data")
      if not isinstance(data, dict):
          logger.debug("Mensaje ignorado: data no es dict")
          continue
      logger.debug(f"Mensaje {idx} root nft={data.get('nft')} tipo={msg.get('type')}")
      if data.get("nft") != nft:
          continue

      tipo = msg.get("type")
      if tipo not in (TipoTransaccion.TX_NFT.value, TipoTransaccion.PROPERTY.value):
          continue
      owner = data.get("destino") if tipo == TipoTransaccion.TX_NFT.value else data.get("owner")
      puntaje = calcular_puntaje(msg, 0)
      logger.debug(f"Candidato root encontrado owner={owner} puntaje={puntaje}")
      if mejor_puntaje is None or puntaje > mejor_puntaje:
          mejor_puntaje = puntaje
          propietario_actual = owner
          logger.debug(f"Propietario actualizado a {owner} desde mensaje {idx} root")

  logger.debug(f"Propietario final para NFT {nft}: {propietario_actual}")
  return propietario_actual


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
  claves_esperadas = {"nft", "origen", "destino"}
  claves_recibidas = set(data.keys())
  if claves_recibidas != claves_esperadas:
      return False, f"Para el tipo TX_NFT, 'data' debe contener exactamente las claves: {claves_esperadas}"
      
  if not isinstance(data.get("nft"), str) or not isinstance(data.get("origen"), str) or not isinstance(data.get("destino"), str):
      return False, "Todos los campos (nft, origen, destino) deben ser cadenas de texto."

  if redis_client is None:
      return False, "No se proporcionó el cliente Redis para validar TX_NFT"

  propietario_actual = obtener_propietario_actual_nft(data["nft"], redis_client)
  if propietario_actual is None:
      return False, "El NFT no existe o no tiene un dueño registrado"
  if propietario_actual != data["origen"]:
      return False, "El origen no es el dueño actual del NFT"
      
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

  # VALIDAR CLAVES (formato valido)
  if "origen" in data:
    if not es_clave_publica_valida(data["origen"]):
        return False, "Clave pública de origen inválida"

  if "destino" in data:
      if not es_clave_publica_valida(data["destino"]):
          return False, "Clave pública de destino inválida"
      



      
  # Pasan todas las validaciones
  return True, "OK"
