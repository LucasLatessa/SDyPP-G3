import hashlib
import random
import threading
import time
from flask import Flask, json, jsonify, request
from redis import Redis
import pika
import redis

# ---------------------------
#        CONEXIONES
# ---------------------------

# Conexion con Rabbbit
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host="localhost",
        port=5672,
        credentials=pika.PlainCredentials("grupo03", "grupo03"),
    )
)

channel = connection.channel()
# Creacion de la cola
channel.queue_declare(queue="transacciones")
# Creacion del exchange del tipo TOPIC -> Todos los workers compiten para resolver el desafio
channel.exchange_declare(
    exchange="block_challenge", exchange_type="topic", durable=True
)


# Conexion con Redis
redis = Redis()

# ---------------------------
#    FUNCIONES COORDINADOR
# ---------------------------



#En el caso de que ningun worker agarre el mensaje, levanto workers cpu en Gcloud
def handle_return(channel, method, properties, body):
    global message_returned
    message_returned = True
    print("Mensaje devuelto por Rabbit")

#Manejo de devolucion de mensajes
channel.add_on_return_callback(handle_return)

# Funcion para tomar los paquetes que estan en la cola y mandarlo al Topic de Rabbit, asi los workers pueden resolver el desafio
def procesar_paquetes():
    while True:
        try:
          paquete = []  # Almacenar los mensajes del paquete actual
          # Procesa en bloques de 10
          for _ in range(10):
              # Obtener un mensaje de la cola 'transactions' de RabbitMQ
              method_frame, header_frame, body = channel.basic_get(
                  queue="transacciones", auto_ack=False
              )
              if method_frame:
                  # Añadir el mensaje al paquete
                  paquete.append(json.loads(body))
                  # Confirmar que el mensaje ha sido recibido y procesado (acknowledge)
                  channel.basic_ack(delivery_tag=method_frame.delivery_tag)
              else:
                  break  # No hay más mensajes disponibles, salir del bucle

          #print(paquete)
          #AGREGAR MANEJO DE PAQUETES NO PROCESADOS!!!!!!!!!!!!!! -> SI NO SE PROCESO EL PAQUETE ENTONCES REENVIO, 
          #EL COORDINADOR NO LE IMPORTA LA CANTIDAD DE WORKERS QUE HAY CONSUMIENDO!
          if paquete:
              # Añadir metadatos al paquete del bloque
              tail_elements = (
                  redis.get_ultimos_mensajes()
              )  # Obtener los últimos mensajes de Redis
              last_element = (
                  redis.get_ultimo()
              )  # Obtener el último elemento de la lista en Redis

              max_random = 20000000
              idBloque = str(random.randint(0, max_random))

              bloque = {
                  "id": idBloque,
                  "transaccion": paquete,
                  "prefix": "0",  # Dificulta de tres 0 -> Buscar el quiebre
                  "base_string_chain": "papa", #Es lo que concateno para el hash, que tiene que arrancar con el prefijo
                  "blockchain_content": (
                      last_element["blockchain_content"] if last_element else "[]"
                  ),  # Contenido de la cadena de bloques hasta el bloque anterior
                  "max_random": max_random,  # Random usado en la prueba de trabajo
              }

              # Mando el bloque al Topic de Rabbit
              channel.basic_publish(
                  exchange="block_challenge",
                  routing_key="blocks",
                  body=json.dumps(bloque),
                  mandatory=True
              )
              
              print(f"Paquete con Bloque ID {idBloque} enviado a Topic de Rabbit")
              global message_returned
              message_returned = False
              #Manejo de paquetes devueltos

              timeout = 10  # segundos
              start = time.time()

              while not message_returned and (time.time() - start < timeout):
                  connection.process_data_events()
                  time.sleep(1)
              if not message_returned:
                print("Timeout esperando respuesta de Rabbit")

          # time.sleep(60) #Se ejecuta cada 1 minuto
          print("Pasaron X segundos, procesamiento de paquetes")
          time.sleep(10)
        except Exception as e:
          print(f"Error en thread: {e}")

#Procesamiento de paquetes en segundo plano
procesamiento_paquetes = threading.Thread(target=procesar_paquetes)
procesamiento_paquetes.start()

# ---------------------------
#        SERVIDOR
# ---------------------------

app = Flask(__name__)


# Endpoint para agregar una transaccion a la cola
@app.route("/transaccion", methods=["POST"])
def agregar_transaccion():

    data = request.get_json()
    print(f"Transaccion recibida: {data} ")

    # Obtengo origen, destino y monto
    origen = data["origen"]
    destino = data["destino"]
    monto = data["monto"]

    # Mando a la cola de Rabbit
    channel.basic_publish(
        exchange="", routing_key="transacciones", body=json.dumps(data)
    )

    return "Transaccion recibida y encolada en Rabbit", 200


# Endpoint para que los Workers envien la tarea resuelta
@app.route("/tarea_worker", methods=["POST"])
def tarea_worker():
    data = request.get_json()

    datos = f"{data["numero"]}{data["base_string_chain"]}{data["blockchain_content"]}"
    hash = calcular_hash_v2(datos)
    timestamp = time.time()

    print("---------------------------")
    print("    ¡BLOQUE RECIBIDO!      ")
    print("---------------------------")
    print(f"Hash recibidos: {data["hash"]}")
    print(f"Hash calculado de forma local: {hash}")

    if data["hash"] == hash:
        print("Coinciden :)")
        print("--------------")
        #Verifico si existe un bloque igual en redis
        if redis.exists_id(data['id']):
            return jsonify({'mensaje':'Ya existe ese bloque en redis, queda descartado!'}), 200
        else:
            print("Vamos a agregar el bloque a la cadena")
            print(f"Hash:  {data["hash"]}")
            print(f"Contenido del bloque anterior: {data["blockchain_content"]}")

            #Le calculo el hash 
            blockchain_data = f"{data["base_string_chain"]}{data["hash"]}"
            blockchain_content = calcular_hash_v2(blockchain_data)

            #Obtengo el bloque anterior para conectar, si no hay quiere decir que este es el origen
            try:
                bloque_previo = redis.get_ultimo()
            except:
                bloque_previo = "Null"

            if bloque_previo != None:
                print(f"Hash del bloque previo:  {bloque_previo["hash"]}")
                data["previous_block"] = bloque_previo["hash"]
            else:
                print(f"Hash del bloque previo: NULL")
                data["previous_block"] = "None"
            
            data['timestamp'] = timestamp
            data['blockchain_content'] = blockchain_content

            print("Bloque final")
            print(data)

            redis.publicar(data)

            return jsonify({"mensaje":"Bloque validado y añadido a la blockchain"}),201
        
    else:
        print("No coinciden :(")
        return jsonify({"mensaje":"Los hash no coinciden, paquete descartado!"}),400   


# Endpoint del estado del servidor
@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "funcionando :D"})

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", debug=True)
    except KeyboardInterrupt:
        # Definir una bandera para detener el hilo
        stop_event = threading.Event()
        # Solicitar detener el hilo
        stop_event.set()
        print("Servidor parado")
    
