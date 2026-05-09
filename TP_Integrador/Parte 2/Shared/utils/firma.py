#pip install cryptography

import base64
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def json_canonico(data: dict) -> bytes:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def cargar_clave_privada(path: str):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
        )


def cargar_clave_publica(path: str):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def firmar_json(data: dict, private_key_path: str) -> str:
    private_key = cargar_clave_privada(private_key_path)
    payload = json_canonico(data)

    firma = private_key.sign(
        payload,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )

    return base64.b64encode(firma).decode("utf-8")


def verificar_firma(data: dict, firma_b64: str, public_key_path: str) -> bool:
    public_key = cargar_clave_publica(public_key_path)
    payload = json_canonico(data)
    firma = base64.b64decode(firma_b64)

    try:
        public_key.verify(
            firma,
            payload,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False
