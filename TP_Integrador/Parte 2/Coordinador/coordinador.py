from flask import Flask, json, jsonify, request
import pika

# ---------------------------
#        CONEXIONES
# ---------------------------

# Conexion con Rabbbit
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost",port=5672,credentials=pika.PlainCredentials("rabbitmq", "rabbitmq")))

channel = connection.channel()
#Creacion de la cola
channel.queue_declare(queue="transacciones")
#Creacion del exchange del tipo TOPIC -> Todos los workers compiten para resolver el desafio
channel.exchange_declare(exchange="block_challenge", exchange_type="topic",
durable=True)

# ---------------------------
#        SERVIDOR
# ---------------------------

app = Flask(__name__)

#Endpoint para agregar una transaccion a la cola
@app.route("/transaccion", methods=["POST"])
def agregar_transaccion():

    data = request.get_json()
    print(f"Transaccion recibida: {data} ")

    #Obtengo origen, destino y monto
    origen = data["origen"]
    destino = data["destino"]
    monto = data["monto"]

    #Mando a la cola de Rabbit
    channel.basic_publish(exchange='',routing_key='transacciones',body=json.dumps(data))

#Endpoint para que los Workers envien la tarea resuelta
@app.route('/tarea_worker', methods=["POST"])
def tarea_worker():
    data = request.get_json()

    










#Endpoint del estado del servidor
@app.route("/status", methods=["GET"])
def status():
    return jsonify({'status':'funcionando :D'})