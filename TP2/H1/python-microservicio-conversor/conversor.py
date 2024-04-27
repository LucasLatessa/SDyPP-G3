from flask import Flask, request, jsonify
import os

app = Flask(__name__)

#Funcion que realiza la conversion
def convertir_unidades(valor, unidad_origen, unidad_destino):
    # Define las relaciones de conversión entre diferentes unidades
    relaciones_conversion = {
        'metros': {'metros': 1, 'pies': 3.28084, 'kilómetros': 0.001},
        'pies': {'metros': 0.3048, 'pies': 1, 'kilómetros': 0.0003048},
        'kilómetros': {'metros': 1000, 'pies': 3280.84, 'kilómetros': 1}
    }

    # Realiza la conversión
    if unidad_origen in relaciones_conversion and unidad_destino in relaciones_conversion[unidad_origen]:
        factor_conversion = relaciones_conversion[unidad_origen][unidad_destino]
        valor_convertido = valor * factor_conversion
        return valor_convertido
    else:
        return None

#Endpoint para hacer la conversion
@app.route('/conversor', methods=['POST'])
def convertir():
    valor = request.json["valor"]
    unidad_origen = request.json["unidad_origen"]
    unidad_destino = request.json["unidad_destino"]

    #Si me falta algun campo
    if valor is None or unidad_origen is None or unidad_destino is None:
        return jsonify({'error': 'Se requieren valor, unidad_origen y unidad_destino'}), 400

    #Realizo la operacion y devuelvo
    resultado = convertir_unidades(valor, unidad_origen, unidad_destino)
    if resultado is None:
        #Si no se puede realizar la conversion
        return jsonify({'error': 'No se puede realizar la conversión entre las unidades proporcionadas'}), 400

    return jsonify({'resultado': resultado}), 200

#Endpoint de estado del servidor que realiza la conversion
@app.route(rule="/status", methods=["GET"])
def status():
    data = {
        "status": "Ok"
    }
    print(data)
    return data

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Obtener el puerto de la variable de entorno PORT

    app.run(debug=True, host='0.0.0.0', port=port)