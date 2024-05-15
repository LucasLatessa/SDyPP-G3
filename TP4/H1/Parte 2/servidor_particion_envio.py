from flask import Flask, request 
from particionador import particionar_imagen
import sys
import cv2

app = Flask(__name__)
@app.route(rule="/getRemoteTask", methods=["POST"])
def particionar_enviar_imagen(imagen):
    print(imagen)




if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Como usar el programa: python particionador.py (ruta-imagen)")
        sys.exit(1)

    # Obtengo la ruta y cargo la imagen
    ruta_img = sys.argv[1]
    imagen = cv2.imread(ruta_img)

    particiones = particionar_imagen(imagen)

    particionar_enviar_imagen(particiones)
    