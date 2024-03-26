import socket
import json

#Host y puerto del servidor D
HOSTD = "127.0.0.1"
PORTD = 65535

#Lista de contactos
contactos = []

#Creacion del servidor
mi_socket = socket.socket()
mi_socket.bind((HOSTD,PORTD))
mi_socket.listen(5)

print(f"El servidor está escuchando en {HOSTD}:{PORTD}")

while True:
    try:
        #Nueva conexion
        conexion, addr = mi_socket.accept()
        print("Nueva conexion con un nodo C establecida!")

        #Recibo el socket del nodo que envio la peticion
        peticion = json.loads(conexion.recv(1024).decode())
     
        print("Petición recibida:", peticion)

        #Devuelvo la lista de contacto y agrego al nuevo
        respuesta = contactos
        conexion.send(json.dumps(respuesta).encode())
        contactos.append(peticion)

        #Muestro la lista actualizada
        print("------------------")
        print("Lista de contactos actualizada")
        print("Mis Contactos:")
        print(contactos)
        print("------------------")

        conexion.close()
    except ConnectionAbortedError:
        print("La conexión fue cerrada por el cliente.")
    except KeyboardInterrupt:
        print("Interrupción del servidor. Cerrando...")
        break

mi_socket.close()