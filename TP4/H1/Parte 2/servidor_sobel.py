from flask import Flask, jsonify, request
from sobel_Parte1 import sobel
import os
import json
import numpy as np

app = Flask(__name__)

@app.route(rule="/sobel",methods=["POST"])
def aplicar_sobel():

    imagen = request.json["imagenes"][0]
    imagen_np = np.array(list(imagen.values()))

    imagen_sobel = sobel(imagen_np)

    imagen_sobel = {
        "imagen" : imagen_sobel
    }
    
    return jsonify(imagen_sobel)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 9999))  # Obtener el puerto de la variable de entorno PORT

    app.run(debug=True, host='0.0.0.0', port=port)