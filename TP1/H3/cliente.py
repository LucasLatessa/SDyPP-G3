import socket
import time

HOST = '35.196.99.208'
PORT = 8083 

def conectar():
    mi_socket = socket.socket()
    while True:
        try:
            mi_socket.connect((HOST, PORT))
            return mi_socket
        except (ConnectionRefusedError, TimeoutError):
            print("La conexión fue rechazada. Intentando de nuevo...")
            time.sleep(5)  # Esperar 5 segundos antes de intentar de nuevo      
            continue
        except KeyboardInterrupt:
            raise  # Volver a lanzar la excepción para que el bloque principal pueda manejarla

def enviar_saludo(socket_cliente):
    socket_cliente.send("Hola desde el cliente".encode())
    respuesta = socket_cliente.recv(1024).decode() #Buffer
    print(respuesta)

def cliente():
    while True:
        try:
            mi_socket = conectar()
            enviar_saludo(mi_socket)
            mi_socket.close()
            time.sleep(10)  # Esperar 10 segundos para reconecatar
        except (ConnectionResetError, ConnectionAbortedError):
            socket_cliente.close()
            socket_cliente = conectar()  # Usamos una nueva variable para el nuevo socket
        except KeyboardInterrupt:
            raise  # Volver a lanzar la excepción para que el bloque principal pueda manejarla

cliente()