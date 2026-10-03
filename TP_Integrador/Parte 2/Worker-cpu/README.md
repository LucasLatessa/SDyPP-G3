# Worker CPU - Script de Prueba y Benchmark Local (`test.py`)

Script en Python para realizar pruebas locales, depuración y benchmarking del algoritmo de resolución de desafíos de Prueba de Trabajo (Proof of Work - PoW) en CPU.

Simula el cálculo de hashes MD5 en el formato `MD5(nonce + hash_val)` buscando un nonce en un rango numérico determinado cuyo hash resultante comience con el prefijo (`prefix`) de dificultad especificado.

---

## 📋 ¿Qué hace `test.py`?

1. **Iteración de Nonce:** Recorre un rango de números enteros desde `--start` hasta `--end`.
2. **Cálculo de Hash MD5:** Por cada nonce, computa `MD5(str(nonce) + hash_val)`.
3. **Verificación de Dificultad:** Comprueba si el hash hexadecimal resultante inicia con la cadena `--prefix` requerida.
4. **Métricas de Rendimiento:** Mide el tiempo total transcurrido con `time.perf_counter()`, cuenta la cantidad de intentos realizados y calcula la velocidad de procesamiento en **hashes por segundo (H/s)**.
5. **Salida en JSON:** Imprime el resultado en formato JSON estructurado para facilitar la lectura o integración con otras herramientas.

---

## ⚙️ Parámetros de Ejecución

| Parámetro | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `--start` | `int` | **Sí** | Valor inicial del nonce (cota inferior del rango). |
| `--end` | `int` | **Sí** | Valor final del nonce (cota superior del rango). |
| `--prefix` | `str` | **Sí** | Prefijo objetivo que debe tener el hash resultante (ej. `000`, `0000`, `a1b`). |
| `--hash-val` | `str` | **Sí** | Hash base o identificador del bloque/transacción sobre el cual se concatena el nonce. |
| `--inclusive` | `flag` | No | Si se incluye, el rango evalúa hasta `end` inclusive (`[start, end]`). Por defecto es exclusivo (`[start, end)`). |

---

## 🚀 Ejemplos de Ejecución

### 1. Prueba Básica con Dificultad Baja (3 ceros)
Busca un nonce en el rango `[0, 100000)` para un hash base:
```bash
python test.py --start 0 --end 100000 --prefix "000" --hash-val "abc123def456"
```

---

### 2. Prueba con Rango Inclusivo (`--inclusive`)
Equivalente al comportamiento de ejecutables binarios tipo `./md5 from to prefix input`:
```bash
python test.py --start 1000 --end 50000 --prefix "00" --hash-val "bloque_genesis_hash" --inclusive
```

---

### 3. Prueba de Mayor Dificultad / Benchmark de CPU
Evalúa la velocidad de cálculo (H/s) en rangos más grandes y mayor dificultad (ej. 4 o 5 ceros):
```bash
python test.py --start 0 --end 1000000 --prefix "0000" --hash-val "9f83c605188822bb29ec23f37a50d69b"
```

---

### 4. Prueba de Rango sin Solución
Permite verificar el comportamiento cuando ningún nonce del rango cumple con el prefijo:
```bash
python test.py --start 0 --end 500 --prefix "0000000" --hash-val "test_no_match"
```

---

## 📊 Formato de Salida (JSON)

### Caso 1: Desafío Resuelto (`encontrado: true`)
```json
{
  "encontrado": true,
  "numero": 4218,
  "hash": "0000a89f83c605188822bb29ec23f37a",
  "prefix": "0000",
  "hash_val": "9f83c605188822bb29ec23f37a50d69b",
  "start": 0,
  "end": 1000000,
  "inclusive": false,
  "intentos": 4219,
  "tiempo_segundos": 0.003412,
  "hashes_por_segundo": 1236518.17
}
```

### Caso 2: Desafío No Encontrado (`encontrado: false`)
```json
{
  "encontrado": false,
  "numero": null,
  "hash": null,
  "prefix": "0000000",
  "hash_val": "test_no_match",
  "start": 0,
  "end": 500,
  "inclusive": false,
  "intentos": 500,
  "tiempo_segundos": 0.000415,
  "hashes_por_segundo": 1204819.27
}
```
