import subprocess

def ejecutar_minero(from_val, to_val, prefix, hash_val):
    # Comando para compilar el archivo CUDA
    compile_command = ['nvcc', 'md5.cu', '-o', 'md5']

    # Ejecutar el comando de compilación
    compile_process = subprocess.run(compile_command, capture_output=True, text=True)
    # Verificar si la compilación fue exitosa
    if compile_process.returncode != 0:
        print("Error al compilar el archivo CUDA:")
        print(compile_process.stderr)
        return
    

    execute_command = ['./md5', str(from_val), str(to_val), prefix, hash_val]

    # Ejecutar el comando de ejecución
    execute_process = subprocess.run(execute_command, capture_output=True, text=True)
    print(execute_process.args)
    # Verificar si la ejecución fue exitosa
    if execute_process.returncode != 0:
        print("No se encontro el resultado")
        print(execute_process.stderr)
        return
    
    # Imprimir la salida del programa
    print("Salida del programa minero:")
    print(execute_process.stdout)
    with open('json_output.txt', 'r') as archivo:
        contenido = archivo.read()
        print(contenido)
    return contenido

# Ejemplo de uso
ejecutar_minero(1, 500, "00", "b")
