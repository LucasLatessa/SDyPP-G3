import socket

#Host y puerto al que me quiero conectar
HOST = '35.185.81.236'
PORT = 8081 

mi_socket = socket.socket()

#Realiza la conexion
mi_socket.connect((HOST,PORT))

#Enviar mensaje
mi_socket.send("Hola desde el cliente".encode())
respuesta = mi_socket.recv(1024).decode() #Buffer

print (respuesta)
mi_socket.close()