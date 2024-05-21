#Funcion que aplica sobel
import cv2
import numpy as np
import sys, os


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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Como usar el programa: python sobel-Parte1.py (ruta-imagen)")
        sys.exit(1)

    #Obtengo la ruta y cargo la imagen
    ruta_img = sys.argv[1]
    imagen = cv2.imread(ruta_img)

    # Obtener el nombre del archivo sin la extensión
    nombre_archivo = os.path.splitext(os.path.basename(ruta_img))[0]

    #Aplico Sobel
    imagen_sobel = sobel(imagen)

    #Guardo la imagen}
    cv2.imwrite(nombre_archivo + "_sobel.jpg", imagen_sobel )

    print("Imagen filtrada!")