# Test de Concurrencia y Carga para el Coordinador (`test_curl_concurrente.py`)

Herramienta de pruebas de carga y concurrencia desarrollada en Python para simular peticiones simultáneas (equivalente a ejecutar múltiples comandos `curl` en paralelo) contra el servicio **Coordinador** (Flask / Gunicorn) de la arquitectura distribuida.

Permite evaluar la capacidad de respuesta, la tasa de éxito, el throughput (RPS), la distribución de latencias (p50, p95, p99) y detectar posibles cuellos de botella o errores (HTTP 500, 503, timeouts o caídas de workers).

---

## 📋 Características Principales

- **Simulación Multi-Hilo (ThreadPoolExecutor):** Lanza peticiones concurrentes configurables simulando usuarios virtuales (VUs).
- **Generación Automática de Criptografía:** Integrado con `crypto_generator.py` para construir y firmar digitalmente transacciones válidas (`TX`) con claves RSA (SHA256 con padding PKCS1v15), cumpliendo las validaciones del Coordinador.
- **Medición Precisa de Latencias:** Utiliza `time.perf_counter()` para medir milisegundo a milisegundo el tiempo de respuesta de cada petición.
- **Métricas y Estadísticas Detalladas:**
  - Throughput (Requests per Second - RPS).
  - Tasa de éxito (códigos `200` / `201`) vs errores (`500`, `503`, timeouts, conexión rechazada).
  - Percentiles de latencia: Mínimo, Promedio, Mediana ($p50$), $p95$, $p99$ y Máximo.
  - Diagnóstico automatizado al finalizar la prueba (`PASSED`, `WARNING`, `FAILED`).
- **Soporte para múltiples tipos de endpoints:** Tanto endpoints transaccionales (POST con payload firmado) como endpoints de consulta o salud (GET `/status`).

---

## 🛠️ Requisitos Previos e Instalación

1. **Python 3.8 o superior**.
2. **Dependencias:** Instalar la librería `cryptography` (necesaria para la generación de claves RSA y firmas digitales):

```bash
pip install cryptography
```

*(Las librerías `urllib`, `concurrent.futures`, `json`, `statistics`, `argparse` forman parte de la biblioteca estándar de Python).*

---

## ⚙️ Parámetros y Opciones de Línea de Comandos

El script cuenta con una interfaz de argumentos mediante `argparse`:

| Parámetro | Flag Corto | Tipo | Valor por Defecto | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `--url` | - | `str` | `http://localhost:5000/transaccion` | URL completa del endpoint a evaluar. |
| `--concurrencia` | `-c` | `int` | `3` | Número de hilos/peticiones concurrentes simultáneas (VUs). |
| `--total` | `-n` | `int` | `10` | Cantidad total de peticiones que se enviarán en la prueba. |
| `--timeout` | `-t` | `float`| `10.0` | Tiempo máximo de espera en segundos por cada petición antes de considerarla timeout. |
| `--tipo` | - | `str` | `transaccion` | Tipo de prueba/payload: `transaccion` (POST con TX firmada), `status` (GET sin payload), `custom` (GET genérico). |

Para ver la ayuda integrada en consola:
```bash
python test_curl_concurrente.py --help
```

---

## 🚀 Formas de Ejecución

### 1. Ejecución Básica (Valores por Defecto)
Ejecuta 10 transacciones con 3 hilos concurrentes contra `http://localhost:5000/transaccion`:
```bash
python test_curl_concurrente.py
```

---

### 2. Prueba de Carga Media / Concurrencia Moderada
Evalúa cómo responde el Coordinador ante 50 peticiones enviadas de a 10 en paralelo:
```bash
python test_curl_concurrente.py -c 10 -n 50
```

---

### 3. Prueba de Estrés y Capacidad Máxima (High Load)
Simula 100 o 200 peticiones con alta concurrencia (ej. 20 a 50 workers concurrentes) para verificar si los workers de Gunicorn o la cola de RabbitMQ se saturan:
```bash
# 100 peticiones con 20 hilos simultáneos
python test_curl_concurrente.py -c 20 -n 100

# 500 peticiones con 50 hilos y timeout de 15 segundos
python test_curl_concurrente.py -c 50 -n 500 -t 15.0
```

---

### 4. Prueba de Endpoints GET / Monitoreo de Estado (`/status`)
Permite probar endpoints de lectura o health check sin generar payloads criptográficos POST:
```bash
python test_curl_concurrente.py --url http://localhost:5000/status --tipo status -c 10 -n 100
```

---

### 5. Prueba contra Entornos Distribuidos (Docker / Kubernetes / Ingress / Servidor Remoto)
Si el coordinador se encuentra corriendo en un cluster, una IP de red o un NodePort/Ingress específico:
```bash
# Ejemplo contra contenedor Docker expuesto o IP de red local
python test_curl_concurrente.py --url http://192.168.1.50:5000/transaccion -c 15 -n 100
python test_curl_concurrente.py --url http://unlucoin.info/api/transaccion -c 15 -n 100


# Ejemplo contra Ingress o servicio de Kubernetes
python test_curl_concurrente.py --url http://coordinador.local/transaccion -c 25 -n 200
```

---

### 6. Prueba con Timeout Ajustado (Detección de Cuellos de Botella)
Si querés verificar si alguna petición supera un umbral estricto (ej. 2 segundos):
```bash
python test_curl_concurrente.py -c 10 -n 50 -t 2.0
```

---

### 7. Uso Programático como Módulo de Python
Podés importar la función `ejecutar_test_concurrencia` en otros scripts de testing o suites de integración continua:

```python
from test_curl_concurrente import ejecutar_test_concurrencia

resultado = ejecutar_test_concurrencia(
    url="http://localhost:5000/transaccion",
    concurrencia=5,
    total_requests=25,
    timeout=5.0,
    endpoint_tipo="transaccion"
)

print(f"RPS Obtenido: {resultado['rps']:.2f}")
print(f"Tasa de Éxito: {resultado['tasa_exito']:.2f}%")
print(f"Latencia p95: {resultado['latencias']['p95']:.2f} ms")
```

---

## 📊 Ejemplo de Salida en Consola

Al finalizar la ejecución, el script imprime un reporte completo en la terminal:

```text
======================================================================
 EJECUTANDO TEST DE CONCURRENCIA (TRANSACCION)
 URL Destino:        http://localhost:5000/transaccion
 Concurrencia (VUs): 10 peticiones en paralelo
 Total Peticiones:   50
 Timeout por req:    10.0 s
======================================================================
[*] Generando 50 transacciones firmadas con claves RSA...
[+] Transacciones preparadas con éxito.

----------------------------------------------------------------------
 RESULTADOS DEL TEST
----------------------------------------------------------------------
 Tiempo Total de Ejecución:  1.42 segundos
 Throughput (RPS):           35.21 req/s
 Peticiones Exitosas (2xx):  50/50 (100.00%)
 Errores 500 (Internal Err): 0/50 (0.00%)
 Errores 503 (Infra/Rabbit): 0/50
 Errores de Red / Timeout:   0/50

 Distribución de Códigos HTTP:
   HTTP 200: 50 peticiones (OK)

 Métricas de Latencia (ms):
   Mínima:        18.45 ms
   Promedio:      45.12 ms
   Mediana (p50): 41.30 ms
   p95:           78.90 ms
   p99:           95.20 ms
   Máxima:        102.15 ms
----------------------------------------------------------------------
 [PASSED] El coordinador soporta la concurrencia solicitada satisfactoriamente.
======================================================================
```

---

## 🔍 Interpretación de Resultados y Diagnóstico

- **`[PASSED]` (Tasa de éxito $\ge 99\%$):** El servidor manejó adecuadamente la carga concurrente sin degradación ni pérdida de peticiones.
- **`[FAILED]` (Presencia de HTTP 500):** Se presentaron excepciones internas no controladas en el Coordinador. Puede indicar bloqueos de I/O en workers síncronos, problemas de concurrencia en la conexión a Redis/RabbitMQ, o falta de workers en Gunicorn.
- **Errores `503` o Errores de Red / Timeout (`status_code <= 0`):** La cola de peticiones de Gunicorn/Nginx se saturó, el backlog de sockets rechazó conexiones, o RabbitMQ no respondió dentro del límite de tiempo.
