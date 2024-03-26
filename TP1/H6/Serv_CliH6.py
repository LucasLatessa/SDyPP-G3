import random
import socket
import threading
import time
import sys
import json

def puerto_aleatorio():
    min = 1024
    max = 65534
    return random.randint(min,max)

HOSTServ = "127.0.0.1"  # La dirección IP de loopback, localhost
PORTServ = puerto_aleatorio()  # Puerto para escuchar las conexiones entrantes
HOST_D = sys.argv[1]
PORT_D = int(sys.argv[2])

def servidor():
    mi_socket = socket.socket()  # Genera socket
    mi_socket.bind((HOSTServ, PORTServ))  # Recibe ip y puerto
    mi_socket.listen(5)  # Cantidad de peticiones en cola

    print(f"El servidor está escuchando en {HOSTServ}:{PORTServ}")

    while True:
        try:
            conexion, addr = mi_socket.accept()
            print("Nueva conexion establecida!")
            print(addr)

            peticion = json.loads(conexion.recv(1024).decode())  # Decodifica JSON
            print("Petición recibida:", peticion)

            respuesta = {"mensaje": "Hola, soy un nodo C"}
            conexion.send(json.dumps(respuesta).encode())  # Envia respuesta como JSON
            conexion.close()
        except ConnectionAbortedError:
            print("La conexión fue cerrada por el cliente.")
        except KeyboardInterrupt:
            print("Interrupción del servidor. Cerrando...")
            break

    mi_socket.close()

def conectar(IP,PUERTO):
    mi_socket = socket.socket()
    while True:
        try:
            mi_socket.connect((IP, PUERTO))
            return mi_socket
        except ConnectionRefusedError:
            # print("La conexión fue rechazada. Intentando de nuevo...")
            #  time.sleep(5) Esperar 5 segundos antes de intentar de nuevo
            continue
        except KeyboardInterrupt:
            raise  # Volver a lanzar la excepción para que el bloque principal pueda manejarla

def enviar_socket(socket_cliente):
    while True:
        try:
            mensaje = {
                "mensaje": "Hola, te paso mis datos",
                "ip":HOSTServ,
                "puerto":PORTServ,
                }
            socket_cliente.send(json.dumps(mensaje).encode())  # Envia mensaje como JSON
            respuesta = json.loads(socket_cliente.recv(1024).decode())  # Decodifica respuesta JSON


            for i in range(0, respuesta.length):
                ip = respuesta.decode()[i]["ip"]
                puerto = respuesta.decode()[i]["puerto"]
                nuevoSocket = conectar(ip,puerto)
                enviar_saludo(nuevoSocket)
                nuevoSocket.close()

            #print("Respuesta recibida:", respuesta)
        except (ConnectionResetError, ConnectionAbortedError):
            socket_cliente.close()
            #socket_cliente = conectar()  # Usamos una nueva variable para el nuevo socket
            continue
        except KeyboardInterrupt:
            raise  # Volver a lanzar la excepción para que el bloque principal pueda manejarla
        time.sleep(10)  # Esperar 10 segundos antes de enviar el próximo saludo

def enviar_saludo(socket_cliente):
    while True:
        mensaje = {"mensaje": "Hola, soy un nodo C"}
        socket_cliente.send(json.dumps(mensaje).encode())

def cliente():
    try:
        mi_socket = conectar()
        enviar_saludo(mi_socket)
        mi_socket.close()
    except KeyboardInterrupt:
        print("Interrupción del cliente. Cerrando...")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python serv_cli.py <ip_servidor> <puerto_servidor> <ip_destino> <puerto_destino>")
        sys.exit(1)

    servidor_thread = threading.Thread(target=servidor)
    servidor_thread.start()
    cliente()
