import operator
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

#Endpoint donde llevaran las peticiones del servidor web
@app.route(rule="/ejecutarTarea",methods=["POST"])
def ejecutarTarea():
    #Obtengo los datos de la tarea
    operador = request.json["operador"]
    numero1 = int(request.json["n1"])
    numero2 = int(request.json["n2"])

    #Resuelvo en base a lo enviado
    resultado = operacionesMatematica(operador,numero1,numero2)
    
    data = {
        "resultado": resultado
    }
    
    #Devuelvo el resultado
    return jsonify(data)

#Endpoint de estado del servidor de tarea
@app.route(rule="/status", methods=["GET"])
def status():
    data = {
        "status": "Ok"
    }
    print(data)
    return data

#Funcion de tarea basica, realiza una operacion matematica en base a lo que se envie
def operacionesMatematica(operador,n1,n2):
    # Mapea el operador con la funcion asociada
    operadores = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv
    }

    if operador in operadores:
        resultado = operadores[operador](n1, n2)
    else:
        resultado = "Operador no válido"
    return resultado

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Obtener el puerto de la variable de entorno PORT

    app.run(debug=True, host='0.0.0.0', port=port)