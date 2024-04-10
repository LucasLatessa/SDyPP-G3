import operator
from flask import Flask, request

app = Flask(__name__)

@app.route(rule="/ejecutarTarea",methods=["POST"])
def ejecutarTarea():
    operador = request.json["operador"]
    numero1 = int(request.json["n1"])
    numero2 = int(request.json["n2"])

    resultado = operacionesMatematica(operador,numero1,numero2)
    
    data = {
        "resultado": resultado
    }
    return data

def operacionesMatematica(operador,n1,n2):
    # Mapear operador con funcion asociada
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
   app.run() 