import hashlib
import random
import threading
import time
from flask import Flask, json, jsonify, request
import pika
import redis

# ---------------------------
#        REDIS UTILS
# ---------------------------

class RedisUtils:
    #Conexion con redis cuando se cree la instancia
    def __init__(self, host='localhost',port=6379,db=0,password="grupo03"):
        self.redis_client = redis.StrictRedis(host=host, port=port, db=0, password=password)

    #Publicar el mensaje al inicio de la lista
    def publicar(self,mensaje, list_key='blockchain'):
        mensaje_json = json.dumps(mensaje) # Convierte el mensaje a formato JSON
        self.redis_client.lpush(list_key, mensaje_json) # Inserta el mensaje al inicio de la lista

    #Recupero los ultimos mensajes, en base al count (osea, recupera los ultimos 10)
    def get_ultimos_mensajes(self, list_key='blockchain',count=10):
        mensaje_json = self.redis_client.lrange(list_key, 0, count - 1) # Recupera los últimos 10 mensajes
        return [json.loads(msg) for msg in mensaje_json] # Convierte cada mensaje de JSON a un objeto de Python
    
    #Recupera el ultimo elemento de la lista en Redis
    def get_ultimo(self, list_key='blockchain'):
        latest_element_json = self.redis_client.lindex(list_key, 0)  # Recupera el elemento en la posición 0 (el más reciente)
        if latest_element_json:
            return json.loads(latest_element_json)  # Convierte el elemento de JSON a un objeto de Python si existe
        return None  # Retorna None si la lista está vacía
    
    #Verifica si existe ese ID en la lista de Redis
    def exists_id(self, id, list_key='blockchain'):
        messages_json = self.redis_client.lrange(list_key, 0, -1)  # Recupera todos los mensajes de la lista
        for msg_json in messages_json:
            msg = json.loads(msg_json)  # Convierte cada mensaje de JSON a un objeto de Python
            if 'id' in msg and msg['id'] == id:  # Verifica si el mensaje contiene el ID especificado
                return True
        return False

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
redis = RedisUtils()

# ---------------------------
#    FUNCIONES COORDINADOR
# ---------------------------

# Funcion para calcular el hash -> Utilzia un numero y una cadena base
def calcular_hash(data):
    hash_val = 0  # Valor inicial del hash
    for byte in data.encode(
        "utf-8"
    ):  # Convierte la cadena de entrada a bytes en formato UTF-8 y recorre cada byte
        hash_val = (hash_val * 31 + byte) % (
            2**32
        )  # Multiplica el valor del hash por 31 y añade el valor del byte, asegurando que el resultado esté dentro del rango de 32 bits
        hash_val ^= (hash_val << 13) | (
            hash_val >> 19
        )  # Realiza una rotación de bits: desplaza el valor 13 bits a la izquierda o 19 bits a la derecha, y aplica una operación XOR
        hash_val = (hash_val * 17) % (
            2**32
        )  # Multiplica el valor del hash por 17, asegurando que el resultado esté dentro del rango de 32 bits
        hash_val = (
            (hash_val << 5) | (hash_val >> 27)
        ) & 0xFFFFFFFF  # Realiza otra rotación de bits: desplaza el valor 5 bits a la izquierda o 27 bits a la derecha, y aplica una operación AND para asegurar que el resultado esté dentro de 32 bits
    return hash_val  # Retorna el valor final del hash

def calcular_hash_v2(data):
    hash = hashlib.sha256()
    hash.update(data.encode('utf-8'))
    return hash.hexdigest()

# Funcion para tomar los paquetes que estan en la cola y mandarlo al Topic de Rabbit, asi los workers pueden resolver el desafio
def procesar_paquetes():
    while True:
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

        print(paquete)
        if paquete:
            # Añadir metadatos al paquete del bloque
            tail_elements = (
                redis.get_ultimos_mensajes()
            )  # Obtener los últimos mensajes de Redis
            last_element = (
                redis.get_ultimo()
            )  # Obtener el último elemento de la lista en Redis

            max_random = 1000000
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
            )
            
            print(f"Paquete con Bloque ID {idBloque} enviado a Topic de Rabbit")

        # time.sleep(60) #Se ejecuta cada 1 minuto
        time.sleep(10)

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

    #procesar_paquetes()

    return "Transaccion recibida y encolada en Rabbit", 200


# Endpoint para que los Workers envien la tarea resuelta
@app.route("/tarea_worker", methods=["POST"])
def tarea_worker():
    data = request.get_json()

    datos = f"{data["numero"]}{data["base_string_chain"]}{data["blockchain_content"]}"
    hash = calcular_hash_v2(datos)
    timestamp = time.time()

    print("--------------")
    print("Bloque recibido por parte del worker!!")
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
    
