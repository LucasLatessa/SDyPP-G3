import subprocess
import json
import time

def ejecutar_minero(from_val, to_val, prefix, hash_val):
    file_path= 'json_output.txt'
    with open(file_path, 'w') as archivo:
        json.dump({"numero": 0, "hash_md5_result": ""}, archivo)
    # Comando para compilar el archivo CUDA
    compile_command = ['nvcc', 'md5.cu', '-o', 'md5']

    # Ejecutar el comando de compilación
    compile_process = subprocess.run(compile_command, capture_output=True, text=True)
    # Verificar si la compilación fue exitosa
    if compile_process.returncode != 0:
        print("Error al compilar el archivo CUDA:")
        print(compile_process.stderr)
        return
    
    rep = 0
    encontrado = False
    repeticiones = int(to_val / (512 * 150))
    desde = 1
    print("repeticiones:", repeticiones)
    start_time_total = time.time()
    while (rep <= repeticiones and not(encontrado)):
        print("ciclos:", rep, "comienzo:", desde)

        execute_command = ['./md5', str(desde), str(to_val), prefix, hash_val]

        start_time = time.time()
        execute_process = subprocess.run(execute_command, capture_output=True, text=True)
        end_time = time.time()

        with open(file_path, 'r') as archivo:
            contenido = archivo.read()

        resultado = json.loads(contenido)
        execution_time = end_time - start_time

        if not(resultado['hash_md5_result'] == ""):
            encontrado = True
        desde += (512 * 150)
        rep += 1
        #print(f"Tiempo de ejecución: {execution_time} segundos")
    end_time_total = time.time()
    execution_time_total = end_time_total - start_time_total
    #print(f"Tiempo de ejecución total: {execution_time_total} segundos")
    # Ejecutar el comando de ejecución

    print(execute_process.args)
    # Verificar si la ejecución fue exitosa
    if execute_process.returncode != 0:
        print("No se encontro el resultado")
        print(execute_process.stderr)
        return
    
    # Imprimir la salida del programa
    print("Salida del programa minero:")
    print(execute_process.stdout)
    return contenido

# Ejemplo de uso
ejecutar_minero(1, 1000000, "0000000", "at22")

import subprocess
import json
import time
