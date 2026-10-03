#!/usr/bin/env python3
"""
Test de Concurrencia y Carga para el Coordinador (Flask / Gunicorn).
Simula peticiones concurrentes equivalentes a 'N curl en paralelo' y evalúa
la tasa de éxito, latencias y códigos de estado HTTP (detectando errores 500 / timeouts).
"""

import sys
import os
import time
import argparse
import statistics
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List

# Añadir ruta para importar crypto_generator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crypto_generator import generar_par_claves, crear_transaccion_tx_valida

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass


def realizar_peticion_http(url: str, payload: Dict[str, Any] = None, timeout: float = 10.0) -> Dict[str, Any]:
    """
    Ejecuta una petición HTTP POST o GET y mide el tiempo exacto de respuesta.
    """
    headers = {"Content-Type": "application/json"}
    data_bytes = None
    if payload is not None:
        data_bytes = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url=url,
        data=data_bytes,
        headers=headers,
        method="POST" if data_bytes is not None else "GET"
    )

    t_inicio = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            t_fin = time.perf_counter()
            body = response.read().decode("utf-8")
            return {
                "status_code": response.status,
                "latencia_ms": (t_fin - t_inicio) * 1000,
                "error": None,
                "body": body
            }
    except urllib.error.HTTPError as e:
        t_fin = time.perf_counter()
        body = e.read().decode("utf-8") if e.fp else ""
        return {
            "status_code": e.code,
            "latencia_ms": (t_fin - t_inicio) * 1000,
            "error": f"HTTPError {e.code}: {e.reason}",
            "body": body
        }
    except urllib.error.URLError as e:
        t_fin = time.perf_counter()
        return {
            "status_code": 0,
            "latencia_ms": (t_fin - t_inicio) * 1000,
            "error": f"URLError (Conexión rechazada / Timeout): {e.reason}",
            "body": ""
        }
    except Exception as e:
        t_fin = time.perf_counter()
        return {
            "status_code": -1,
            "latencia_ms": (t_fin - t_inicio) * 1000,
            "error": f"Excepción inesperada: {str(e)}",
            "body": ""
        }


def preparar_transacciones(cantidad: int) -> List[Dict[str, Any]]:
    """Genera pares de claves y transacciones firmadas válidas."""
    print(f"[*] Generando {cantidad} transacciones firmadas con claves RSA...")
    # Generamos un conjunto base de claves para no demorar la inicialización del test
    priv_origen, _, pub_origen = generar_par_claves(bits=1024)
    _, _, pub_destino = generar_par_claves(bits=1024)

    transacciones = []
    for i in range(cantidad):
        tx = crear_transaccion_tx_valida(
            origen_priv=priv_origen,
            origen_pub_clean=pub_origen,
            destino_pub_clean=pub_destino,
            monto=10.0 + (i % 100)
        )
        transacciones.append(tx)
    print("[+] Transacciones preparadas con éxito.\n")
    return transacciones


def ejecutar_test_concurrencia(
    url: str,
    concurrencia: int,
    total_requests: int,
    timeout: float = 10.0,
    endpoint_tipo: str = "transaccion"
) -> Dict[str, Any]:
    """
    Lanza 'total_requests' peticiones usando 'concurrencia' hilos simultáneos.
    """
    print("=" * 70)
    print(f" EJECUTANDO TEST DE CONCURRENCIA ({endpoint_tipo.upper()})")
    print(f" URL Destino:      {url}")
    print(f" Concurrencia (VUs): {concurrencia} peticiones en paralelo")
    print(f" Total Peticiones: {total_requests}")
    print(f" Timeout por req:  {timeout} s")
    print("=" * 70)

    payloads = None
    if endpoint_tipo == "transaccion":
        payloads = preparar_transacciones(total_requests)

    resultados = []
    t_global_inicio = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concurrencia) as executor:
        futuros = []
        for i in range(total_requests):
            payload = payloads[i] if payloads else None
            futuros.append(
                executor.submit(realizar_peticion_http, url, payload, timeout)
            )

        for futuro in as_completed(futuros):
            resultados.append(futuro.result())

    t_global_fin = time.perf_counter()
    duracion_total = t_global_fin - t_global_inicio

    # Análisis de resultados
    codigos_status = {}
    latencias = []
    exitos = 0
    errores_500 = 0
    errores_503 = 0
    errores_red = 0

    for r in resultados:
        st = r["status_code"]
        codigos_status[st] = codigos_status.get(st, 0) + 1
        latencias.append(r["latencia_ms"])

        if st in (200, 201):
            exitos += 1
        elif st == 500:
            errores_500 += 1
        elif st == 503:
            errores_503 += 1
        elif st <= 0:
            errores_red += 1

    tasa_exito = (exitos / total_requests) * 100
    tasa_500 = (errores_500 / total_requests) * 100
    rps = total_requests / duracion_total if duracion_total > 0 else 0

    lat_min = min(latencias) if latencias else 0
    lat_max = max(latencias) if latencias else 0
    lat_avg = statistics.mean(latencias) if latencias else 0
    lat_p50 = statistics.median(latencias) if latencias else 0
    lat_p95 = statistics.quantiles(latencias, n=20)[18] if len(latencias) >= 20 else lat_max
    lat_p99 = statistics.quantiles(latencias, n=100)[98] if len(latencias) >= 100 else lat_max

    # Mostrar reporte
    print("\n" + "-" * 70)
    print(" RESULTADOS DEL TEST")
    print("-" * 70)
    print(f" Tiempo Total de Ejecución:  {duracion_total:.2f} segundos")
    print(f" Throughput (RPS):           {rps:.2f} req/s")
    print(f" Peticiones Exitosas (2xx):  {exitos}/{total_requests} ({tasa_exito:.2f}%)")
    print(f" Errores 500 (Internal Err): {errores_500}/{total_requests} ({tasa_500:.2f}%)")
    print(f" Errores 503 (Infra/Rabbit): {errores_503}/{total_requests}")
    print(f" Errores de Red / Timeout:   {errores_red}/{total_requests}")
    print("\n Distribución de Códigos HTTP:")
    for code, count in sorted(codigos_status.items()):
        label = "OK" if code in (200, 201) else "Error/Otro"
        print(f"   HTTP {code}: {count} peticiones ({label})")

    print("\n Métricas de Latencia (ms):")
    print(f"   Mínima:  {lat_min:.2f} ms")
    print(f"   Promedio:{lat_avg:.2f} ms")
    print(f"   Mediana (p50): {lat_p50:.2f} ms")
    print(f"   p95:     {lat_p95:.2f} ms")
    print(f"   p99:     {lat_p99:.2f} ms")
    print(f"   Máxima:  {lat_max:.2f} ms")
    print("-" * 70)

    return {
        "concurrencia": concurrencia,
        "total_requests": total_requests,
        "duracion_total": duracion_total,
        "rps": rps,
        "exitos": exitos,
        "tasa_exito": tasa_exito,
        "errores_500": errores_500,
        "tasa_500": tasa_500,
        "errores_503": errores_503,
        "errores_red": errores_red,
        "codigos_status": codigos_status,
        "latencias": {
            "min": lat_min,
            "avg": lat_avg,
            "p50": lat_p50,
            "p95": lat_p95,
            "p99": lat_p99,
            "max": lat_max
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Test de Concurrencia para Coordinador")
    parser.add_argument("--url", default="http://localhost:5000/transaccion", help="Endpoint a testear")
    parser.add_argument("-c", "--concurrencia", type=int, default=3, help="Número de peticiones concurrentes (VUs)")
    parser.add_argument("-n", "--total", type=int, default=10, help="Total de peticiones a enviar")
    parser.add_argument("-t", "--timeout", type=float, default=10.0, help="Timeout en segundos por petición")
    parser.add_argument("--tipo", choices=["transaccion", "status", "custom"], default="transaccion", help="Tipo de payload a enviar")

    args = parser.parse_args()

    ejecutar_test_concurrencia(
        url=args.url,
        concurrencia=args.concurrencia,
        total_requests=args.total,
        timeout=args.timeout,
        endpoint_tipo=args.tipo
    )


if __name__ == "__main__":
    main()
