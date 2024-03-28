import socket
import json
import threading
import time
#Host y puerto del servidor D
HOST_D = "0.0.0.0"#"35.196.99.208"
PORT_D = 8080

# Lista de contactos para la ventana actual
contactos_actual = []
# Lista de contactos para la siguiente ventana
contactos_siguiente = []

def mover_reg():
    print("Cambio de registros...")
    global contactos_actual, contactos_siguiente
    contactos_actual=contactos_siguiente
    contactos_siguiente=[]
    print(contactos_actual)

def servidor():
    mi_socket = socket.socket()
    mi_socket.bind((HOST_D, PORT_D))
    mi_socket.listen(5)

    print(f"El servidor está escuchando en {HOST_D}:{PORT_D}")

    while True:
        try:
            #Nueva conexion
            conexion, addr = mi_socket.accept()
            print("Nueva conexión con un nodo C establecida!")

            #Recibo el socket del nodo que envio la peticion
            peticion = json.loads(conexion.recv(1024).decode())
            print("Petición recibida:", peticion)
            #Devuelvo la lista de contactos actuales y agrego el nuevo a contactos siguientes
            respuesta = contactos_actual
            conexion.send(json.dumps(respuesta).encode())
            contactos_siguiente.append(peticion)

            conexion.close()
        except ConnectionAbortedError:
            print("La conexión fue cerrada por el cliente.")
        except KeyboardInterrupt:
            print("Interrupción del servidor. Cerrando...")
            break
    mi_socket.close()

servidor_thread = threading.Thread(target=servidor)
servidor_thread.start()
while True:
    time.sleep(60) # Mover registros cada 60 segundos
    mover_reg()