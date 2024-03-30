from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import socket
import threading

HOST = '0.0.0.0'  # La dirección IP de loopback, localhost
PORT = 8080        # Puerto para escuchar las conexiones entrantes

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
                "key":"h1",
                "status": "Servidor en funcionamiento"})
            self.wfile.write(status_json.encode())
        else:
            #Si es otro path dice que en endpoint no existe(404)
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("Endpoint no encontrado".encode())


def statusRun(server_class=HTTPServer, handler_class=StatusHandler, puerto=10001):
    #Crea el socket, y define las peticiones co
    server_address = (HOST, puerto)
    httpd = server_class(server_address, handler_class)
    print("Status corriendo!")
    while status:
        httpd.serve_forever() #Maneja solicitudes

# ------------------------------------------------------------------------------
#                                APLICACION
# ------------------------------------------------------------------------------

mi_socket = socket.socket() #Genera socket

mi_socket.bind((HOST,PORT)) #Recibe ip y puerto

mi_socket.listen(1) #Cantidad de peticiones en cola

print(f"El servidor está escuchando en {HOST}:{PORT}")

# Ejecutar el servidor HTTP en un hilo separado
threading.Thread(target=statusRun, daemon=True).start()

conexion,addr = mi_socket.accept()
print ("Nueva conexion establecida!")
print (addr)

peticion = conexion.recv(1024).decode()
print (peticion)

conexion.send("Hola, te saludo desde el servidor".encode())
conexion.close()

status = False #Terminada la comunicacion con el cliente, se da de baja el status