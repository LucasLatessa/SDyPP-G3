import subprocess
import json
import time

def ejecutar_minero(prefix, hash_val):
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
    execute_command = ['./md5',prefix, hash_val]
    start_time_total = time.time()
    execute_process = subprocess.run(execute_command, capture_output=True, text=True)
    end_time_total = time.time()
    execution_time_total = end_time_total - start_time_total
    
    # Ejecutar el comando de ejecución

    print(execute_process.args)
    # Verificar si la ejecución fue exitosa
    if execute_process.returncode != 0:
        print("No se encontro el resultado")
        print(execute_process.stderr)
        return

    with open(file_path, 'r') as archivo:
        contenido = archivo.read()
    resultado = json.loads(contenido)

    
    # Imprimir la salida del programa
    print("Salida del programa minero:")
    print(execute_process.stdout)
    print("Tiempo de ejecucion:",execution_time_total )
    return contenido

# Ejemplo de uso
ejecutar_minero("000", "hola")
