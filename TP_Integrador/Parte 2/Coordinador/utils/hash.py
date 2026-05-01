"""
Funciones utilitarias para cálculo de hashes.

Provee utilidades para calcular valores hash a partir de cadenas de texto,
incluyendo una implementación custom de 32 bits y una versión estándar.
"""
import hashlib

def calcular_hash(data: str) -> int:
    """
    Calcula un hash custom de 32 bits para una cadena de texto dada.

    Utiliza una serie de multiplicaciones por números primos (31, 17) y 
    operaciones a nivel de bits (XOR, desplazamientos lógicos) para generar
    un valor entero pseudoaleatorio basado en los bytes de entrada.

    Args:
        data (str): La cadena de texto a utilizar para el hash.

    Returns:
        int: El valor final del hash (entero de 32 bits sin signo).
    """
    hash_val = 0  # Valor inicial del hash
    for byte in data.encode(
        "utf-8"
    ):  # Convierte la cadena de entrada a bytes en formato UTF-8 y recorre cada byte
        hash_val = (hash_val * 31 + byte) % (
            2**32
        )  # Multiplica el valor del hash por 31 y añade el valor del byte, asegurando que el resultado esté dentro del rango de 32 bits
        hash_val ^= (hash_val << 13) | (
            hash_val >> 19
        )  # Realiza una rotación de bits: desplaza el valor 13 bits a la izquierda o 19 bits a la derecha, y aplica una operación XOR
        hash_val = (hash_val * 17) % (
            2**32
        )  # Multiplica el valor del hash por 17, asegurando que el resultado esté dentro del rango de 32 bits
        hash_val = (
            (hash_val << 5) | (hash_val >> 27)
        ) & 0xFFFFFFFF  # Realiza otra rotación de bits: desplaza el valor 5 bits a la izquierda o 27 bits a la derecha, y aplica una operación AND para asegurar que el resultado esté dentro de 32 bits
    return hash_val  # Retorna el valor final del hash

def calcular_hash_v2(data: str) -> str:
    """
    Calcula el hash MD5 de una cadena de texto.

    Args:
        data (str): La cadena de texto a hashear.

    Returns:
        str: El hash resultante representado como una cadena hexadecimal.
    """
    #hash = hashlib.sha256()
    hash_obj = hashlib.md5()
    hash_obj.update(data.encode('utf-8'))
    return hash_obj.hexdigest()