from flask import Flask, jsonify, request
from sobel_Parte1 import sobel
import numpy as np

app = Flask(__name__)

@app.route(rule="/sobel",methods=["POST"])
def aplicar_sobel():

    #Reviso la imagen y la convierto a nparray para poder aplicarle Sobel
    imagen = request.json["imagenes"]
    print(request.json["id"])
    imagen_np = np.array(imagen,dtype=np.uint8)
    imagen_np = np.squeeze(imagen_np)

    #Le aplico sobel
    imagen_sobel = sobel(imagen_np)

    #Armo el json con la respuesta
    imagen_sobel_json = {
        "imagen" : imagen_sobel.tolist() #Como lista ya que estamos trabajando con arreglo de pixeles
    }
    
    return jsonify(imagen_sobel_json)