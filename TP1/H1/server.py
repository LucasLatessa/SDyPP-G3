import socket

HOST = '0.0.0.0'  # Cualquier host
PORT = 8080        # Puerto para escuchar las conexiones entrantes

mi_socket = socket.socket() #Genera socket

mi_socket.bind((HOST,PORT)) #Establece conexion: Recibe ip y puerto

mi_socket.listen(5) #Cantidad de peticiones en cola

print(f"El servidor está escuchando en {HOST}:{PORT}")

while True:
    conexion,direccion = mi_socket.accept() #Acepto las peticiones
    print ("Nueva conexion establecida!")
    print (direccion)

    peticion = conexion.recv(1024).decode()
    print (peticion)

    conexion.send("Hola, te saludo desde el servidor".encode())
    conexion.close()