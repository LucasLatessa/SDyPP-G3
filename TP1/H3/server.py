from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import socket
import threading

HOST = '0.0.0.0'  # La dirección IP de loopback, localhost
PORT = 8083        # Puerto para escuchar las conexiones entrantes
PORT_STATUS = 10003 # Puerto statuss

# ------------------------------------------------------------------------------
#                                ENDPOINT
# ------------------------------------------------------------------------------

status = True

#Creamos la ruta
class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/status':
            #Devuelvo un codigo 200 y un mensaje diciendo que el server funciona
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            status_json = json.dumps({
                "key":"h3",
                "status": "Servidor en funcionamiento"})
            self.wfile.write(status_json.encode())
        else:
            #Si es otro path dice que en endpoint no existe(404)
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("Endpoint no encontrado".encode())


def statusRun(server_class=HTTPServer, handler_class=StatusHandler):
    #Crea el socket, y deja corriendo /status
    server_address = (HOST, PORT_STATUS)
    httpd = server_class(server_address, handler_class)
    print("Status corriendo!")
    while status:
        httpd.serve_forever() #Maneja solicitudes

# ------------------------------------------------------------------------------
#                                APLICACION
# ------------------------------------------------------------------------------

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
        finally:
            if conexion:
                conexion.close()  # Cerrar la conexión existente

    mi_socket.close()

if __name__ == "__main__":
    # Ejecutar el servidor HTTP en un hilo separado
    threading.Thread(target=statusRun, daemon=True).start()
    servidor()
    status = False 
