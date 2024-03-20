import socket

HOST = '0.0.0.0'  # La dirección IP de loopback, localhost
PORT = 8080        # Puerto para escuchar las conexiones entrantes

def servidor():
    mi_socket = socket.socket() # Genera socket
    mi_socket.bind((HOST, PORT)) # Recibe ip y puerto
    mi_socket.listen(5) # Cantidad de peticiones en cola

    print(f"El servidor está escuchando en {HOST}:{PORT}")

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

if __name__ == "__main__":
    servidor()
