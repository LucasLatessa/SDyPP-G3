# Configuracion Reddis
import io
import time
import cv2
import numpy as np
import redis
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)

#Funcion que recibe los resultados de los workers
def recibir_resultados(id,cantPartes):
    partes_recibidas = 0
    particiones = [None] * cantPartes
    completo = True

    #Recorro todas las partes de la imagen, para buscar en redis
    while (partes_recibidas < cantPartes) and completo:
        #Consulto por nombre de la imagen y parte
        redis_key = f"{id}_{partes_recibidas}"
        #Hago get a redis para ver si existe esa parte
        mensaje = r.get(redis_key)
        #Si existe esa parte, la guardo
        if mensaje is not None and particiones[partes_recibidas] is None:
            # Convierto a imagne numpy
            imagen_bytes = np.frombuffer(mensaje, np.uint8)
            imagen_np = cv2.imdecode(imagen_bytes, cv2.IMREAD_COLOR)
            particiones[partes_recibidas] = imagen_np
            partes_recibidas += 1
            print(f"Imagen {id} sobel recibida! {partes_recibidas} de {cantPartes}")
        else:
            #Corto el ciclo
            print(partes_recibidas)
            completo = False
        
    #Devuelvo la lista con todas las particiones
    return particiones, completo

#Si ya estan todas las partes, borro la imagen de reddis
def borrar_partes(id,cantPartes):
    #Borro la clave principal que tenia la cantidad de pares
    r.delete(id)
    partes_recibidas = 0
    #Recorro todas las partes de la imagen, para buscar en redis
    while (partes_recibidas < cantPartes):
        #Borro la imagen de redis
        redis_key = f"{id}_{partes_recibidas}"
        r.delete(redis_key)
        partes_recibidas += 1

# Encargado de unir todas las imagenes
def unir_particiones(particiones_sobel):
    # Calculo el tamaño (número de particiones en x y en y)
    n = int(len(particiones_sobel) ** 0.5)

    # Uno las particiones horizontales
    particiones_unidas = []
    for i in range(0, len(particiones_sobel), n):
        grupo = particiones_sobel[i : i + n]
        particiones_unidas.append(np.hstack(grupo))

    # Ahora uno de forma vertical
    imagen_unida = np.vstack(particiones_unidas)

    # Devuelvo la imagen completa
    return imagen_unida

@app.route(rule="/imagen", methods=["GET"])
def procesarImagen():
    #Obtengo el id, nombre y cant_partes
    id = request.args.get("id")
    nombre = request.args.get("nombre")

    #Obtengo la cantidad de partes que tiene la imagen
    try:
        cant_partes = int(r.get(id))
    except:
        return "La imagen no existe", 500 #MEJORAR CODIGOS

    particiones, completo = recibir_resultados(id,cant_partes)

    if (not completo):
        return "La imagen todavia esta siendo procesada", 500
    else:
        #Borro todas las partes que me quedaron en redis
        borrar_partes(id,cant_partes)
        #Une todas las particiones
        imagen_sobel = unir_particiones(particiones)

        #Devuelvo el resultado al WS
        _, imagen_bytes = cv2.imencode('.jpg', imagen_sobel)
        return send_file(io.BytesIO(imagen_bytes.tobytes()), mimetype='image/jpeg')
    
#Endpoint de estado del servidor
@app.route(rule="/status", methods=["GET"])
def status():
    data = {
        "Status": "En funcionamiento :)"
    }
    print(data)
    return data
    
if __name__ == '__main__':
    r = redis.Redis(host='redis', port=6379, decode_responses=False)
    app.run(host='0.0.0.0', port=5002)