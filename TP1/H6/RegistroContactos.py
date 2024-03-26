import socket
import json

HOSTD = "127.0.0.1"
PORTD = 65535

contactos = [
]

mi_socket = socket.socket()
mi_socket.bind((HOSTD,PORTD))
mi_socket.listen(5)

print(f"El servidor está escuchando en {HOSTD}:{PORTD}")

while True:
    try:
        conexion, addr = mi_socket.accept()
        print("Nueva conexion con un nodo Cestablecida!")
        print(addr)

        peticion = json.loads(conexion.recv(1024).decode())  # Decodifica JSON

        contactos.append(peticion)

        print("Petición recibida:", peticion)

        respuesta = contactos

        conexion.send(json.dumps(respuesta).encode())  # Envia respuesta como JSON
        conexion.close()
    except ConnectionAbortedError:
        print("La conexión fue cerrada por el cliente.")
    except KeyboardInterrupt:
        print("Interrupción del servidor. Cerrando...")
        break

mi_socket.close()