import json
import os
import subprocess
import time
from pathlib import Path


OUTPUT_FILE = Path("json_output.txt")
CUDA_SOURCE = "md5.cu"
CUDA_BINARY = "./md5"

BATCH_SIZE = int(os.getenv("GPU_BATCH_SIZE", "50000000"))
POLL_INTERVAL = float(os.getenv("GPU_POLL_INTERVAL", "0.2"))


def compilar_si_hace_falta() -> bool:
    binary = Path("md5")
    source = Path(CUDA_SOURCE)

    if binary.exists() and binary.stat().st_mtime >= source.stat().st_mtime:
        return True

    compile_process = subprocess.run(
        ["nvcc", CUDA_SOURCE, "-o", "md5"],
        capture_output=True,
        text=True,
    )

    if compile_process.returncode != 0:
        print("Error al compilar CUDA:")
        print(compile_process.stderr)
        return False

    return True


def ejecutar_cuda(from_val: int, to_val: int, prefix: str, hash_val: str, stop_event=None) -> bool:
    process = subprocess.Popen(
        [
            CUDA_BINARY,
            str(from_val),
            str(to_val),
            prefix,
            hash_val,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    while process.poll() is None:
        if stop_event is not None and stop_event.is_set():
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
            return False

        time.sleep(POLL_INTERVAL)

    stdout, stderr = process.communicate()

    if stdout:
        print(stdout, end="")

    if process.returncode != 0:
        print("Error ejecutando CUDA:")
        print(stderr)
        return False

    return True


def ejecutar_minero(from_val: int, to_val: int, prefix: str, hash_val: str, stop_event=None) -> str | None:
    from_val = int(from_val)
    to_val = int(to_val)

    if to_val < from_val:
        return None

    if not compilar_si_hace_falta():
        return None

    desde = from_val

    while desde <= to_val:
        if stop_event is not None and stop_event.is_set():
            return None

        hasta = min(desde + BATCH_SIZE - 1, to_val)

        OUTPUT_FILE.write_text(
            json.dumps({"numero": 0, "hash_md5_result": ""}),
            encoding="utf-8",
        )

        print(f"GPU rango: {desde} - {hasta}")

        ok = ejecutar_cuda(desde, hasta, prefix, hash_val, stop_event=stop_event)
        if not ok:
            return None

        try:
            contenido = OUTPUT_FILE.read_text(encoding="utf-8")
            resultado = json.loads(contenido)
        except (OSError, json.JSONDecodeError) as e:
            print("Error leyendo json_output.txt:")
            print(e)
            return None

        if resultado.get("hash_md5_result"):
            return contenido

        desde = hasta + 1

    return json.dumps({"numero": 0, "hash_md5_result": ""})


if __name__ == "__main__":
    resultado = ejecutar_minero(1, 1_000_000, "000000", "apprew")
    print(resultado)
