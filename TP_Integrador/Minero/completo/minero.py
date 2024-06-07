import subprocess

def ejecutar_minero(from_val, to_val, prefix, hash_val):
    # Comando para compilar el archivo CUDA
    compile_command = ['nvcc', 'minero.cu', '-o', 'minero']

    # Ejecutar el comando de compilación
    compile_process = subprocess.run(compile_command, capture_output=True, text=True)

    # Verificar si la compilación fue exitosa
    if compile_process.returncode != 0:
        print("Error al compilar el archivo CUDA:")
        print(compile_process.stderr)
        return
    

    execute_command = ['./minero', str(from_val), str(to_val), prefix, hash_val]

    # Ejecutar el comando de ejecución
    execute_process = subprocess.run(execute_command, capture_output=True, text=True)

    # Verificar si la ejecución fue exitosa
    if execute_process.returncode != 0:
        print("Error al ejecutar el programa minero:")
        print(execute_process.stderr)
        return
    
    # Imprimir la salida del programa
    print("Salida del programa minero:")
    print(execute_process.stdout)

# Ejemplo de uso
ejecutar_minero(10, 12, "0", "00000000000000000000000000000000")
