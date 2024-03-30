from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import socket
import requests
import threading
import time
import sys
import json

#Necesito la direccion IP para poder mandarsela al nodo D
def obtener_ip_publica():
    try:
        # Hacer una solicitud HTTP a ifconfig.me para obtener la dirección IP pública
        response = requests.get('https://ifconfig.me')
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            return response.text.strip()  # Devolver la dirección IP obtenida del cuerpo de la respuesta
        else:
            print("Error al obtener la dirección IP pública. Código de estado:", response.status_code)
    except Exception as e:
        print("Error al ejecutar la solicitud HTTP:", e)
        
HOSTServ = "0.0.0.0" # Obtener y mostrar la dirección IP pública  # La dirección IP de C
#Host y Puerto del nodo D, que vienen como argumento cuando se llama al programa
HOST_D = sys.argv[1] # La direccion IP de D: 35.196.99.208
PORT_D = int(sys.argv[2]) # 8088
PORT_STATUS = 10007 # Puerto status

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
                "key":"h7",
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
    server_address = (HOSTServ, PORT_STATUS)
    httpd = server_class(server_address, handler_class)
    print("Status corriendo!")
    while status:
        httpd.serve_forever() #Maneja solicitudes

# ------------------------------------------------------------------------------
#                                APLICACION
# ------------------------------------------------------------------------------

IPExt = obtener_ip_publica()
PuertoEXT = os.getenv('PUERTO_EXT')
PORTServ = int(PuertoEXT) # Puerto para escuchar las conexiones entrantes con los nodos C

#Servidor en escucha
def servidor():
    mi_socket = socket.socket()  # Genera socket
    mi_socket.bind((HOSTServ, PORTServ))  # Recibe ip y puerto
    mi_socket.listen(5)  # Cantidad de peticiones en cola

    print(f"El servidor está escuchando en {IPExt}:{PuertoEXT}")

    while True:
        try:
            conexion, addr = mi_socket.accept()

            #Recibo una peticion y genero un decodifico JSON
            peticion = json.loads(conexion.recv(1024).decode())

            print("Nueva conexion establecida!")
            print("Petición:", peticion)

            #Le respondo al nodo y cierro conexion
            respuesta = {"mensaje": "Hola, un gusto!"}
            conexion.send(json.dumps(respuesta).encode())
            conexion.close()
        except ConnectionAbortedError:
            print("La conexión fue cerrada por el cliente.")
        except KeyboardInterrupt:
            print("Interrupción del servidor. Cerrando...")
            break

    mi_socket.close()

#Enviar peticion a un servidor dado puerto y IP
def conectar(IP,PUERTO):
    mi_socket = socket.socket()
    try:
        mi_socket.connect((IP, PUERTO))
        print("Enviar peticion a " + IP + ":" + str(PUERTO))
        return mi_socket
    except ConnectionRefusedError:
        print("")
    except KeyboardInterrupt:
        raise
    except Exception as e:
    # Manejo de la excepción: muestra el mensaje de error en pantalla
        print("Se ha producido un error:", e)

#Funcion que le envia el socket al cliente y recibe la lista de contactos donde tiene que enviar peticiones
def enviar_socket(socket_cliente):
    try:
        #Envio mi socket
        mensaje = {
            "ip":IPExt,
            "puerto":PuertoEXT,
            }
        socket_cliente.send(json.dumps(mensaje).encode())

        #Obtengo la lista de contactos
        respuesta = json.loads(socket_cliente.recv(1024).decode())

        print("Respuesta recibida del Nodo D:", respuesta)

        #Por cada contacto, envio una peticion a cada nodo
        for elemento in respuesta:
            ip = elemento["ip"]
            puerto = int(elemento["puerto"])
            try:
                nuevoSocket = conectar(ip,puerto)
                enviar_saludo(nuevoSocket)
                respuesta = json.loads(nuevoSocket.recv(1024).decode())
                print("Respuesta recibida: ", respuesta)
                nuevoSocket.close()
            #Solamente se lleva a cabo si el nodo esta en escucha
            except:
                print("Servidor "+ ip + ":" + str(puerto) + " caido/fuera de funcionamiento")
            #except Exception as e:
                # Manejo de la excepción: muestra el mensaje de error en pantalla
                #print("Se ha producido un error:", e)


    except (ConnectionResetError, ConnectionAbortedError):
        socket_cliente.close()
    except KeyboardInterrupt:
        raise
    except json.decoder.JSONDecodeError as e:
        #print("Error al decodificar la respuesta JSON:", e)
        pass
    time.sleep(10)  # Esperar 10 segundos antes de enviar el próximo saludo

#Funcion que envia un mensaje como saludo en forma de JSON a los nodos C
def enviar_saludo(socket_cliente):
    mensaje = {
        "mensaje": "Hola, soy un nodo C",
        "ip":IPExt,
        "puerto":PuertoEXT
}
    socket_cliente.send(json.dumps(mensaje).encode())

#Funcion cliente
def cliente():
    try:
        #Creo la conexion con el Nodo D y envio mi socket
        mi_socket = conectar(HOST_D,PORT_D)
        enviar_socket(mi_socket)
        mi_socket.close()
    except KeyboardInterrupt:
        print("Interrupción del cliente. Cerrando...")



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python serv_cli.py <ip_d> <puerto_d>")
        sys.exit(1)

#Ejecucion del servidor en otro hilo
servidor_thread = threading.Thread(target=servidor)
servidor_thread.start()
# Ejecutar el servidor HTTP en un hilo separado
threading.Thread(target=statusRun, daemon=True).start()
cliente()
