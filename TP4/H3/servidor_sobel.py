import cv2
from flask import Flask, jsonify, request
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

@app.route(rule="/status", methods=["GET"])
def status():
    data = {
        "status": "Ok"
    }
    print(data)
    return data


def sobel(imagen):
    #print(imagen)
    #Primero convierto la imagen a escala de grises
    gris = cv2.cvtColor(imagen,cv2.COLOR_BGR2GRAY)

    #Aplico el operador de Sobel en los ejes X e Y
    sobel_x = cv2.Sobel(gris,cv2.CV_64F, 1, 0, ksize=3) #Detecta bordes verticales
    sobel_y = cv2.Sobel(gris,cv2.CV_64F, 0, 1, ksize=3) #Detecta bordes horizontales

    #Calculo la magnitud del gradiente, combinando los resultados de X e Y
    magnitud = np.sqrt(sobel_x**2 + sobel_y**2)

    #Normaliza la magnitud, asi la convierto ea imagen de 8 bits
    magnitud = cv2.normalize(magnitud, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U) 
    #De esta forma, los valores estan en el rango de 0 a 255

    #Retorno la imagen con el filtro (bordes resaltados)
    return magnitud

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0')