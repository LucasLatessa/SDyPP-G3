"""
Modulo para la validacion de los diferentes tipos de transacciones
"""
from Shared.utils.logger import get_logger
from Shared.config import (TipoTransaccion)
from cryptography.hazmat.primitives import serialization

# ----------------------------------------------------------------------
#                         CONFIGURACIONES
# ----------------------------------------------------------------------

logger = get_logger(__name__)

# ----------------------------------------------------------------------
#                            FUNCIONES
# ----------------------------------------------------------------------

def es_clave_publica_valida(clave_publica):
  """
  Validar si la clave publica es valida
  """
  # try:
  #   serialization.load_pem_public_key(clave_publica.encode())
  #   return True
  # except Exception:
  #     return False
  return True

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
  

def validar_property(data):
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
      
  return True, "Data válida"

def validar_tx_nft(data):
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
      
  # Validacion de valores
  if not isinstance(data.get("nft"), str) or not isinstance(data.get("origen"), str) or not isinstance(data.get("destino"), str):
      return False, "Todos los campos (nft, origen, destino) deben ser cadenas de texto."
      
  return True, "Data válida"
      

def validar_transaccion(datos):
  """
  Dada una transaccion, se valida si esta cumple con el formato estipulado
  """
  VALIDADORES = {
    TipoTransaccion.TX.value: validar_tx,
    TipoTransaccion.PROPERTY.value: validar_property,
    TipoTransaccion.TX_NFT.value: validar_tx_nft,
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
      
  # FIRMA



  # Pasan todas las validaciones
  return True, "OK"
