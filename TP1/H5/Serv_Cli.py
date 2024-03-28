import socket
import threading
import time
import sys
import json

HOSTServ = sys.argv[1]  # La dirección IP de loopback, localhost
PORTServ = int(sys.argv[2])  # Puerto para escuchar las conexiones entrantes
HOSTDest = sys.argv[3]
PORTDest = int(sys.argv[4])

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

            respuesta = {"mensaje": "Hola, te saludo desde el servidor"}
            conexion.send(json.dumps(respuesta).encode())  # Envia respuesta como JSON

        except ConnectionAbortedError:
            print("La conexión fue cerrada por el cliente.")
        except KeyboardInterrupt:
            print("Interrupción del servidor. Cerrando...")
        except BrokenPipeError:
            print("Se produjo un error de pipe roto.")
        finally:
            conexion.close()

    mi_socket.close()

def conectar():
    mi_socket = socket.socket()
    while True:
        try:
            mi_socket.connect((HOSTDest, PORTDest))
            return mi_socket
        except ConnectionRefusedError:
            print("La conexión fue rechazada. Intentando de nuevo...")
            time.sleep(5)  # Esperar 5 segundos antes de intentar de nuevo
            continue
        except KeyboardInterrupt:
            raise  # Volver a lanzar la excepción para que el bloque principal pueda manejarla

def enviar_saludo(socket_cliente):
    while True:
        try:
            mensaje = {"mensaje": "Hola desde el cliente"}
            socket_cliente.send(json.dumps(mensaje).encode())  # Envia mensaje como JSON
            respuesta = json.loads(socket_cliente.recv(1024).decode())  # Decodifica respuesta JSON
            print("Respuesta recibida:", respuesta)
        except (ConnectionResetError, ConnectionAbortedError,BrokenPipeError):
            print("Se produjo un error de conexión. Reintentando (Cliente)...")
            socket_cliente.close()
            socket_cliente = conectar()  # Usamos una nueva variable para el nuevo socket
            continue
        except KeyboardInterrupt:
            raise  # Volver a lanzar la excepción para que el bloque principal pueda manejarla
        except json.decoder.JSONDecodeError as e:
            #print("Error al decodificar la respuesta JSON:", e)
            pass
        time.sleep(10)  # Esperar 10 segundos antes de enviar el próximo saludo

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
