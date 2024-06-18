import pika
import requests
import minero_gpu
import json
import time

#Enviar el resultado al coordinador para verificar que el resultado es correcto
def enviar_resultado(data):
    url = "http://localhost:5000/tarea_worker"
    try:
        response = requests.post(url, json=data)
        print("Resolucion enviada al Coordinador!")
    except Exception as e:
        print("Fallo al enviar el post:", e)

# #Minero: Encargado de realizar el desafio
def minero(ch, method, properties, body):
    data = json.loads(body)
    print(f"Bloque {data} recibido")

#     encontrado = False
    tiempo_inicial = time.time()
    print("Minero comenzado!")
    resultado = minero_gpu.ejecutar_minero(1, data["max_random"], data["prefix"], data["base_string_chain"] + data["blockchain_content"])
    print("Esto", data["base_string_chain"] + data["blockchain_content"])
    
   
#     #Hasta que no encuentra un hash que comienze con el prefijo no para
#     while not encontrado:
#         #Tomo un numero aleatorio y le calculo el hash a: El aleatorio + la base del bloque + contenido de la cadena de bloues"
#         aleatorio = str(random.randint(0,data["max_random"]))
#         hash = calcular_sha256(aleatorio + data["base_string_chain"] + data["blockchain_content"])
#         #Si el hash arranca con el prefijo
#         if hash.startswith(data["prefix"]):
#             #Corto el bucle y envio el resultado al coordinador
#             encontrado = True
    #tiempo_proceso = time.time() - tiempo_inicial
    #{"numero": 9700, "hash_md5_result": "0eb61761a7b8c92cebf4f820f5b9b380"}  
       
    #data["tiempo_proceso"] = tiempo_proceso
    resultado = json.loads(resultado)
    print("resultado",resultado)
    data["hash"] = resultado['hash_md5_result']
    data["numero"] = resultado["numero"]

    enviar_resultado(data)
    #Confirmo con un ACK que lo resolvi
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Resultado encontrado y enviado con el ID Bloque {data['id']}")

#Conexion con rabbit al topico y comienza a ser consumidor
def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', port=5672, credentials=pika.PlainCredentials('grupo03', 'grupo03'))
    )
    channel = connection.channel()
    channel.exchange_declare(exchange='block_challenge', exchange_type='topic', durable=True)
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='block_challenge', queue=queue_name, routing_key='blocks')
    channel.basic_consume(queue=queue_name, on_message_callback=minero, auto_ack=False)
    print('Esperando mensajes. Para salir pulse CTRL+C')
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        connection.close()
        print("Conexion cerrada")

if __name__ == '__main__':
    main()