from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import json
import threading
import time

#Host y puerto del servidor D
HOST_D = "0.0.0.0"#"35.196.99.208"
PORT_D = 8089
PORT_STATUS = 10009 # Puerto status

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
                "key":"h7Contactos",
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
    server_address = (HOST_D, PORT_STATUS)
    httpd = server_class(server_address, handler_class)
    print("Status corriendo!")
    while status:
        httpd.serve_forever() #Maneja solicitudes

# ------------------------------------------------------------------------------
#                                APLICACION
# ------------------------------------------------------------------------------

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

    # Ejecutar el servidor HTTP en un hilo separado
    threading.Thread(target=statusRun, daemon=True).start()

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