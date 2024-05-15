import os
import cv2 # Biblioteca para el procesamiento de imagenes
import numpy as np #Biblioteca para la computacion cientifica en Python, que permite realizar operaciones matematicas eficientes en matrices y matrices mutldimiensionales.
import sys

def sobel(imagen):

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

    print(magenitud)
    #Retorno la imagen con el filtro (bordes resaltados)
    return magnitud