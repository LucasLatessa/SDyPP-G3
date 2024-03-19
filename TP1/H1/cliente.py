import socket

HOST = '35.196.99.208'
PORT = 8080 

mi_socket = socket.socket()

mi_socket.connect((HOST,PORT))

mi_socket.send("Hola desde el cliente".encode())
respuesta = mi_socket.recv(1024) #Buffer

print (respuesta)
mi_socket.close()