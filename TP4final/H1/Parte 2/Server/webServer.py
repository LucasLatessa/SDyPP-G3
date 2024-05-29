# El WebServer cumple 2 funciones principales:
# .Recibir la imagen, comprobando que todo este bien para que comienze el ciclo,
#   enviando la imagen al spliter
# .Resolver las consultas a los ID que envia el usuario, que identifican
#   a las imagenes que estan siendo procesadas

import io
import uuid
from flask import Flask, jsonify, request, send_file
import requests

app = Flask(__name__)

# Endpoint para transformar las imagenes con el operador sobel
@app.route(rule="/sobel", methods=["POST"])
def sobelWS():
    try:
        # Verifico que exista un archivo en la solicitud
        if "imagen" not in request.files:
            return jsonify({"error": "No hay archivo de imagen en la solicitud"}), 400

        imagen_file = request.files["imagen"]
        nombreImagen = imagen_file.filename

        # Verifico que el archivo no esté vacío
        if imagen_file.filename == "":
            return jsonify({"error": "El nombre del archivo está vacío"}), 400

        # Verifico que los parámetros de partición estén presentes
        if "particion-x" not in request.form or "particion-y" not in request.form:
            return jsonify({"error": "Faltan parámetros de partición"}), 400

        # Verifico que los parámetros de partición sean enteros y mayores que cero
        try:
            partX = int(request.form["particion-x"])
            partY = int(request.form["particion-y"])
            if partX <= 0 or partY <= 0:
                return (
                    jsonify(
                        {"error": "Los valores de partición deben ser mayores que cero"}
                    ),
                    400,
                )
        except ValueError:
            return jsonify({"error": "Los valores de partición deben ser enteros"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Si paso todas las validaciones, comienzo con el ciclo, enviando la imagen a el spliter

    # Genero un identificador unico universal
    id = uuid.uuid4()

    response = requests.post(
        f"http://{split}:5001/split",
        files={"imagen": imagen_file},
        data={"particion-x": partX, "particion-y": partY, "id": id},
    )

    if response.status_code != 200:
        #Devuelvo el error con el codigo
        return response.text, response.status_code
    else:
        # Devuelvo el id en un JSON
        return jsonify({"message": "ID para consultar por la imagen", "id": str(id)}), 200

@app.route(rule="/imagen/<id>", methods=["GET"])
def consultarImagen(id):
    url = f'http://{joiner}:5002/imagen?id=' + id
    response = requests.get(url)

    if response.status_code != 200:
        return response.text, response.status_code
    
    content_type = response.headers.get('Content-Type')

    if content_type == 'image/jpeg':
        img_file = io.BytesIO(response.content)
        return send_file(img_file, mimetype='image/jpeg')
    else:
        return response.text, 200

#Endpoint de estado del servidor
@app.route(rule="/status", methods=["GET"])
def status():
    data = {
        "Status": "En funcionamiento :)"
    }
    print(data)
    return data


if __name__ == '__main__':
    split = "localhost"
    joiner = "localhost"
    app.run(host='0.0.0.0', port=5000)