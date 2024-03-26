import random
import socket
import threading
import time
import sys
import json

#Funcion para generar el puerto aleatorio
def puerto_aleatorio():
    min = 1024
    max = 65534
    return random.randint(min,max)

HOSTServ = "127.0.0.1"  # La dirección IP del servidor D
PORTServ = puerto_aleatorio()  # Puerto para escuchar las conexiones entrantes con los nodos C
#Host y Puerto del nodo D, que vienen como argumento cuando se llama al programa
HOST_D = sys.argv[1]
PORT_D = int(sys.argv[2])

#Servidor en escucha
def servidor():
    mi_socket = socket.socket()  # Genera socket
    mi_socket.bind((HOSTServ, PORTServ))  # Recibe ip y puerto
    mi_socket.listen(5)  # Cantidad de peticiones en cola

    print(f"El servidor está escuchando en {HOSTServ}:{PORTServ}")

    while True:
        try:
            conexion, addr = mi_socket.accept()

            #Recibo una peticion y genero un decodifico JSON
            peticion = json.loads(conexion.recv(1024).decode())

            print("Nueva conexion establecida!")
            print("Petición:", peticion)

            #Le respondo al nodo y cierro conexion
            respuesta = {"mensaje": "Hola, un gusto!"}
            conexion.send(json.dumps(respuesta).encode())
            conexion.close()
        except ConnectionAbortedError:
            print("La conexión fue cerrada por el cliente.")
        except KeyboardInterrupt:
            print("Interrupción del servidor. Cerrando...")
            break

    mi_socket.close()

#Enviar peticion a un servidor dado puerto y IP
def conectar(IP,PUERTO):
    mi_socket = socket.socket()
    try:
        mi_socket.connect((IP, PUERTO))
        print("Enviar peticion a " + IP + ":" + str(PUERTO))
        return mi_socket
    except ConnectionRefusedError:
        print("")
    except KeyboardInterrupt:
        raise

#Funcion que le envia el socket al cliente y recibe la lista de contactos donde tiene que enviar peticiones
def enviar_socket(socket_cliente):
    try:
        #Envio mi socket
        mensaje = {
            "ip":HOSTServ,
            "puerto":PORTServ,
            }
        socket_cliente.send(json.dumps(mensaje).encode())

        #Obtengo la lista de contactos
        respuesta = json.loads(socket_cliente.recv(1024).decode())

        print("Respuesta recibida del Nodo D:", respuesta)

        #Por cada contacto, envio una peticion a cada nodo
        for elemento in respuesta:
            ip = elemento["ip"]
            puerto = elemento["puerto"]
            try:
                nuevoSocket = conectar(ip,puerto)
                enviar_saludo(nuevoSocket)
                respuesta = json.loads(nuevoSocket.recv(1024).decode())
                print("Respuesta recibida: ", respuesta)
                nuevoSocket.close()
            #Solamente se lleva a cabo si el nodo esta en escucha
            except:
                print("Servidor "+ ip + ":" + str(puerto) + " caido")


    except (ConnectionResetError, ConnectionAbortedError):
        socket_cliente.close()
    except KeyboardInterrupt:
        raise
    time.sleep(10)  # Esperar 10 segundos antes de enviar el próximo saludo

#Funcion que envia un mensaje como saludo en forma de JSON a los nodos C
def enviar_saludo(socket_cliente):
    mensaje = {
        "mensaje": "Hola, soy un nodo C",
        "ip":HOSTServ,
        "puerto":PORTServ
}
    socket_cliente.send(json.dumps(mensaje).encode())

#Funcion cliente
def cliente():
    try:
        #Creo la conexion con el Nodo D y envio mi socket
        mi_socket = conectar(HOST_D,PORT_D)
        enviar_socket(mi_socket)
        mi_socket.close()
    except KeyboardInterrupt:
        print("Interrupción del cliente. Cerrando...")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python serv_cli.py <ip_d> <puerto_d>")
        sys.exit(1)

#Ejecucion del servidor en otro hilo
servidor_thread = threading.Thread(target=servidor)
servidor_thread.start()
cliente()
