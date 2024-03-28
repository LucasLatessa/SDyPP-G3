"""import socket

#Host y puerto al que me quiero conectar
HOST = '35.185.81.236'
PORT = 8082

mi_socket = socket.socket()

#Realiza la conexion
mi_socket.connect((HOST,PORT))

#Enviar mensaje
mi_socket.send("Hola desde el cliente".encode())
respuesta = mi_socket.recv(1024).decode() #Buffer

print (respuesta)
mi_socket.close()"""

import json
import socket

#Host y puerto al que me quiero conectar
HOST = '35.185.81.236'
PORT = 8085

mi_socket = socket.socket()

#Realiza la conexion
mi_socket.connect((HOST,PORT))

mensaje = {"mensaje": "Hola desde el cliente test"}
mi_socket.send(json.dumps(mensaje).encode())  # Envia mensaje como JSON
respuesta = json.loads(mi_socket.recv(1024).decode())  # Decodifica respuesta JSON
print("Respuesta recibida:", respuesta)

#print (respuesta)
mi_socket.close()

"""import subprocess

def obtener_ip_publica():
    try:
        # Ejecutar el comando curl ifconfig.me y capturar la salida
        resultado = subprocess.run(['curl', 'ifconfig.me'], capture_output=True, text=True)
        # Verificar si el comando se ejecutó correctamente
        if resultado.returncode == 0:
            return resultado.stdout.strip()  # Devolver la salida sin espacios en blanco
        else:
            print("Error al obtener la dirección IP pública.")
    except Exception as e:
        print("Error al ejecutar el comando:", e)

# Obtener y mostrar la dirección IP pública
ip_publica = obtener_ip_publica()
if ip_publica:
    print("La dirección IP pública es:", ip_publica)"""

"""import random

# Función para generar un puerto aleatorio entre 1024 y 65535
def puerto_aleatorio():
    return random.randint(1024, 65535)

# Obtener y mostrar la dirección IP pública
HOSTServ = "0.0.0.0"  # La dirección IP de C
PORTServ = "8080"  # Puerto aleatorio para escuchar las conexiones entrantes con los nodos C
PORTDocker = puerto_aleatorio()
# Resto de tu código...
print(HOSTServ)
print(PORTServ)
print(PORTDocker)
while True:
    pass"""

"""import os
import random

puerto_ext = random.randint(10800, 10810)

# Configurar la variable de entorno PUERTO_EXT
os.environ['PUERTO_EXT'] = str(puerto_ext)

# Imprimir el puerto generado
print(f"El puerto externo generado es: {puerto_ext}")

while True:
    pass"""

import os

"""# Obtener el valor de la variable de entorno
puerto_ext = os.getenv('PUERTO_EXT')

# Verificar si la variable está definida
if puerto_ext:
    print(f"El valor de la variable PUERTO_EXT es: {puerto_ext}")
else:
    print("La variable PUERTO_EXT no está definida.")"""
