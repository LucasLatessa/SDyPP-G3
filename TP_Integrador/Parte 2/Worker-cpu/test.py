import argparse
import hashlib
import json
import time


def calcular_hash(hash_val: str, nonce: int) -> str:
    texto = f"{nonce}{hash_val}"
    return hashlib.md5(texto.encode()).hexdigest()


def resolver_desafio(start: int, end: int, prefix: str, hash_val: str, inclusive: bool):
    tiempo_inicial = time.perf_counter()

    end_range = end + 1 if inclusive else end
    intentos = 0

    for nonce in range(start, end_range):
        intentos += 1
        hash_result = calcular_hash(hash_val, nonce)

        if hash_result.startswith(prefix):
            tiempo_proceso = time.perf_counter() - tiempo_inicial

            return {
                "encontrado": True,
                "numero": nonce,
                "hash": hash_result,
                "prefix": prefix,
                "hash_val": hash_val,
                "start": start,
                "end": end,
                "inclusive": inclusive,
                "intentos": intentos,
                "tiempo_segundos": tiempo_proceso,
                "hashes_por_segundo": intentos / tiempo_proceso if tiempo_proceso > 0 else None,
            }

    tiempo_proceso = time.perf_counter() - tiempo_inicial

    return {
        "encontrado": False,
        "numero": None,
        "hash": None,
        "prefix": prefix,
        "hash_val": hash_val,
        "start": start,
        "end": end,
        "inclusive": inclusive,
        "intentos": intentos,
        "tiempo_segundos": tiempo_proceso,
        "hashes_por_segundo": intentos / tiempo_proceso if tiempo_proceso > 0 else None,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Prueba local CPU equivalente a MD5(nonce + hash_val)"
    )

    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--hash-val", required=True)
    parser.add_argument(
        "--inclusive",
        action="store_true",
        help="Hace que end sea inclusivo, igual que ./md5 from to prefix input",
    )

    args = parser.parse_args()

    resultado = resolver_desafio(
        start=args.start,
        end=args.end,
        prefix=args.prefix,
        hash_val=args.hash_val,
        inclusive=args.inclusive,
    )

    print(json.dumps(resultado, indent=2))


if __name__ == "__main__":
    main()
