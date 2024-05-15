import cv2
import sys

def particionar_imagen(image):
    # Obtén las dimensiones de la imagen
    height, width, _ = image.shape

    # Define el número de particiones deseadas
    num_particiones_x = 2
    num_particiones_y = 2

    # Calcula el tamaño de cada partición
    part_height = height // num_particiones_y
    part_width = width // num_particiones_x

    # Lista para almacenar las particiones
    particiones = []

    # Particiona la imagen
    for i in range(num_particiones_y):
        for j in range(num_particiones_x):
            # Calcula los límites de cada partición
            y_start = i * part_height
            y_end = y_start + part_height
            x_start = j * part_width
            x_end = x_start + part_width

            # Extrae la partición
            particion = image[y_start:y_end, x_start:x_end]
            particiones.append(particion)

            # Guarda la partición en un archivo
            cv2.imwrite(f'particion{i}_{j}.jpg', particion)

    print("Imagen particionada!")

    return particiones
