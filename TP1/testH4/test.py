"""import sys

HOSTServ = sys.argv[1]  #n La dirección IP de loopback, localhost
PORTServ = int(sys.argv[2])        # Puerto para escuchar las conexioes entrantes
HOSTDest = sys.argv[3] 
PORTDest = int(sys.argv[4]) 

print(HOSTServ)
print(PORTServ)
print(HOSTDest)
print(PORTDest)

#Docker run --rm --name h4test -p 8080:8080 testh4 127.0.0.1 8080 127.0.0.1 8081

while True:
    print("uwu")"""

import socket

#Host y puerto al que me quiero conectar
HOST = '127.0.0.1'
PORT = 8080 

mi_socket = socket.socket()

#Realiza la conexion
mi_socket.connect((HOST,PORT))

#Enviar mensaje
mi_socket.send("Hola desde el cliente".encode())
respuesta = mi_socket.recv(1024).decode() #Buffer

print (respuesta)
mi_socket.close()