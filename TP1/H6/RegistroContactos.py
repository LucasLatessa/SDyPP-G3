from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import json
import threading

#Host y puerto del servidor D
HOSTD = "0.0.0.0" 
PORTD = 8088
PORT_STATUS = 10008 # Puerto status

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
                "key":"h6Contactos",
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
    server_address = (HOSTD, PORT_STATUS)
    httpd = server_class(server_address, handler_class)
    print("Status corriendo!")
    while status:
        httpd.serve_forever() #Maneja solicitudes

# ------------------------------------------------------------------------------
#                                APLICACION
# ------------------------------------------------------------------------------


#Lista de contactos
contactos = []

#Creacion del servidor
mi_socket = socket.socket()
mi_socket.bind((HOSTD,PORTD))
mi_socket.listen(5)

# Ejecutar el servidor HTTP en un hilo separado
threading.Thread(target=statusRun, daemon=True).start()

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