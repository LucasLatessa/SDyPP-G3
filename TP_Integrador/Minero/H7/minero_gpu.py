import subprocess
import json

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

    while (rep <= repeticiones and not(encontrado)):
        desde += (512 * 150)

        execute_command = ['./md5', str(desde), str(to_val), prefix, hash_val]
        execute_process = subprocess.run(execute_command, capture_output=True, text=True)
        with open(file_path, 'r') as archivo:
            contenido = archivo.read()
        resultado = json.loads(contenido)
        if not(resultado['hash_md5_result'] == ""):
            encontrado = True
        rep += 1
    
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
#ejecutar_minero(1, 10000000, "391aaa", "at2az11212")
