import hashlib
import time

def encontrar_numero(prefijo, cadena):
    numero = 1

    while numero <= 2908200:
        texto = cadena + str(numero)
        hash_resultado = hashlib.md5(texto.encode()).hexdigest()
        if hash_resultado.startswith(prefijo):
            return numero
        numero += 1
    return None  # En caso de no encontrar ningún número válido


# Ejemplo de uso
prefijo = "00000"
cadena = "hola"
start_time_total = time.time()
resultado = encontrar_numero(prefijo, cadena)
end_time_total = time.time()
execution_time_total = end_time_total - start_time_total
if resultado is not None:
    print(f"Se encontró el número {resultado} que produce un hash con prefijo {prefijo}.")
else:
    print(f"No se encontró ningún número en el rango proporcionado que cumpla con el prefijo {prefijo}.")
print("tiempo total de ejecucion:",execution_time_total)
