import socket
import threading
import time
import sys
HOSTServ = sys.argv[1]  #n La dirección IP de loopback, localhost
PORTServ = int(sys.argv[2])        # Puerto para escuchar las conexioes entrantes
HOSTDest = sys.argv[3] 
PORTDest = int(sys.argv[4]) 
# HOSTServ = '35.196.99.208' #'0.0.0.0'  # La dirección IP de loopback, localhost
# PORTServ = 8080       # Puerto para escuchar las conexiones entrantes
# HOSTDest = '127.0.0.1'
# PORTDest = 8081 

def servidor():
    mi_socket = socket.socket() # Genera socket
    mi_socket.bind((HOSTServ, PORTServ)) # Recibe ip y puerto
    mi_socket.listen(5) # Cantidad de peticiones en cola

    print(f"El servidor está escuchando en {HOSTServ}:{PORTServ}")

    while True:
        try:
            conexion, addr = mi_socket.accept()
            print("Nueva conexion establecida!")
            print(addr)

            peticion = conexion.recv(1024).decode()
            print(peticion)

            conexion.send("Hola, te saludo desde el servidor".encode())
            conexion.close()
        except ConnectionAbortedError:
            print("La conexión fue cerrada por el cliente.")
        except KeyboardInterrupt:
            print("Interrupción del servidor. Cerrando...")
            break

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
            socket_cliente.send("Hola desde el cliente".encode())
            respuesta = socket_cliente.recv(1024).decode() #Buffer
            print(respuesta)
        except (ConnectionResetError, ConnectionAbortedError):
            socket_cliente.close()
            socket_cliente = conectar()  # Usamos una nueva variable para el nuevo socket
            continue
        except KeyboardInterrupt:
            raise  # Volver a lanzar la excepción para que el bloque principal pueda manejarla
        time.sleep(10)  # Esperar 10 segundos antes de enviar el próximo saludo

def cliente ():
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
    #servidor()
    cliente()