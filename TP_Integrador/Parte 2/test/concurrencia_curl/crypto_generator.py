"""
Generador de billeteras (claves RSA) y transacciones firmadas válidas para pruebas.
Compatible con la validación de cryptography de Coordinador/services/validar_transaccion.py.
"""

import json
import base64
import uuid
import textwrap
from typing import Dict, Any, Tuple
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization


def generar_par_claves(bits: int = 2048) -> Tuple[rsa.RSAPrivateKey, str, str]:
    """
    Genera un par de claves RSA y devuelve (private_key_obj, private_key_pem, public_key_pem_clean).
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=bits
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    # Clave pública limpia (sin headers) como espera el validador
    public_clean = public_pem.replace("-----BEGIN PUBLIC KEY-----", "")\
                             .replace("-----END PUBLIC KEY-----", "")\
                             .replace("\n", "").replace("\r", "").strip()

    return private_key, private_pem, public_clean


def serializar_data_para_firma(data: Dict[str, Any]) -> str:
    """Serializa las claves del diccionario en orden determinista."""
    data_ordenada = {key: data[key] for key in sorted(data.keys())}
    return json.dumps(data_ordenada, separators=(",", ":"), ensure_ascii=False)


def firmar_data(data: Dict[str, Any], private_key: rsa.RSAPrivateKey) -> str:
    """Firma digitalmente con SHA256 y PKCS1v15."""
    mensaje = serializar_data_para_firma(data).encode("utf-8")
    firma = private_key.sign(
        mensaje,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(firma).decode("utf-8")


def crear_transaccion_tx_valida(
    origen_priv: rsa.RSAPrivateKey,
    origen_pub_clean: str,
    destino_pub_clean: str,
    monto: float = 100.0,
    tx_id: str = None
) -> Dict[str, Any]:
    """Crea un payload de tipo 'TX' listo para enviar a POST /transaccion."""
    if tx_id is None:
        tx_id = str(uuid.uuid4())

    data = {
        "tx_id": tx_id,
        "monto": float(monto),
        "origen": origen_pub_clean,
        "destino": destino_pub_clean
    }

    sign = firmar_data(data, origen_priv)

    return {
        "data": data,
        "type": "TX",
        "sign": sign
    }


def crear_transaccion_property_valida(
    owner_priv: rsa.RSAPrivateKey,
    owner_pub_clean: str,
    nft_id: str = None,
    tx_id: str = None
) -> Dict[str, Any]:
    """Crea un payload de tipo 'PROPERTY' listo para enviar a POST /transaccion."""
    if tx_id is None:
        tx_id = str(uuid.uuid4())
    if nft_id is None:
        nft_id = f"nft_{uuid.uuid4().hex[:16]}"

    data = {
        "tx_id": tx_id,
        "nft": nft_id,
        "owner": owner_pub_clean
    }

    sign = firmar_data(data, owner_priv)

    return {
        "data": data,
        "type": "PROPERTY",
        "sign": sign
    }


if __name__ == "__main__":
    priv, priv_pem, pub_clean = generar_par_claves(1024)
    _, _, dest_clean = generar_par_claves(1024)
    tx = crear_transaccion_tx_valida(priv, pub_clean, dest_clean, monto=50)
    print("Ejemplo de transacción generada:")
    print(json.dumps(tx, indent=2))
