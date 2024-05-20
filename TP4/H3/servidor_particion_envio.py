import os
import sys
import cv2
import requests
import json
import numpy as np
from dda_python_terraform import *
from google.cloud import compute_v1


# Envia las particiones a los workers para que apliquen el filtro de sobel
def particionar_enviar_imagen(workers, imagenes):
    HOST = workers
    PORT = 5000  # Puertos donde estaran los workers

    # Aqui se guardan las particiones que envien los workers
    particiones_sobel = []

    # Manejo de workers en circulo, en el caso de que un worker este caido va a la siguinete
    ip_worker = 0

    # Por cada porcion de imagen, envio un request al Worker para que le aplique ese filtro
    for i in range(0, len(imagenes)):
        # Crear el objeto JSON para enviar
        json_data = {
            "id": i,  # Identificador de la imagen
            "imagenes": imagenes[i].tolist(),
        }

        # Convertir el objeto JSON a una cadena JSON
        json_string = json.dumps(json_data)

        # Especificar los encabezados de la solicitud HTTP
        headers = {"Content-Type": "application/json"}

        # Este While true es para pasarle una parte de la iamgen a un worker si o si
        while True:
            try:
                print(f"Envio a {HOST[ip_worker]}:{PORT}")
                # Enviar la solicitud POST al Worker
                response = requests.post(
                    f"http://{HOST[ip_worker]}:{PORT}/sobel",
                    data=json_string,
                    headers=headers,
                )

                # Obtengo la imagen filtrada y la guardo en un arreglo
                imagen_filtrada = response.json()["imagen"]
                imagen_np = np.array(imagen_filtrada, dtype=np.uint8)
                imagen_np = np.squeeze(imagen_np)
                particiones_sobel.append(imagen_np)

                # Si se le aplico el filtro, salgo del bucle
                if response.status_code == 200:
                    print("Lo resolvio :)")
                    ip_worker = (ip_worker + 1) % len(
                        HOST
                    )  # Voy al worker siguiente, ya que el actual estara trabajando
                    break

            # Si el worker esta caido
            except requests.exceptions.RequestException as e:
                print("Cambio de worker :(")
                ip_worker = (ip_worker + 1) % len(HOST)  # Voy al worker siguiente
                # print(f"Error al enviar la solicitud: {e}")

    # Devuelvo el arreglo de particiones
    return particiones_sobel


# Funcion encargada de particionar imagenes en X y Y
def particionar_imagen(image, num_particiones_x, num_particiones_y):
    # Obtén las dimensiones de la imagen
    height, width, _ = image.shape

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

            # Solo para mostrar como quedan las particiones
            # cv2.imwrite(f'particion{i}_{j}.jpg', particion)

    # print("Imagen particionada!")
    return particiones


# Encargado de unir todas las imagenes
def unir_particiones(particiones_sobel):
    # Calculo el tamaño (número de particiones en x y en y)
    n = int(len(particiones_sobel) ** 0.5)

    # Uno las particiones horizontales
    particiones_unidas = []
    for i in range(0, len(particiones_sobel), n):
        grupo = particiones_sobel[i : i + n]
        particiones_unidas.append(np.hstack(grupo))

    # Ahora uno de forma vertical
    imagen_unida = np.vstack(particiones_unidas)

    # Devuelvo la imagen completa
    return imagen_unida


# Obtengo una lista con las IP de cada instancia
def lista_instancias(proyecto, zona):
    lista = []

    instancia_cliente = compute_v1.InstancesClient()
    request = compute_v1.ListInstancesRequest(project=proyecto, zone=zona)

    # LLamo a la API
    response = instancia_cliente.list(request=request)

    for instance in response:
        for interface in instance.network_interfaces:
            if interface.access_configs:
                for config in interface.access_configs:
                    lista.append(config.nat_i_p)

    return lista


# Creador de instancias con terraform
def crear_instancias(numero_instancias):
    working_dir = r"C:\Universidad\2024\Sistemas Distribuidos y Programacion Paralela\SDyPP-G3\TP4\H3\terraform"

    # Inicializo el terraform
    tf = Terraform(working_dir=working_dir)

    # Ejecuta "terraform init"
    return_code, stdout, stderr = tf.init()
    if return_code != 0:
        print("Error durante el init:", stderr)

    # Ejecuta "terraform plan"
    #return_code, stdout, stderr = tf.plan(no_color=IsFlagged,var={'numero_instancias': numero_instancias})
    #if return_code != 0:
    #    print("Error durante el plan:", stderr)

    # Ejecuta 'terraform apply'
    return_code, stdout, stderr = tf.apply(
        skip_plan=True, var={"numero_instancias": numero_instancias}
    )
    if return_code != 0:
        print("Error durante el apply:", stderr)

    print("Terraform apply ejecutado exitosamente.")

    return tf


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Como usar el programa: python servidor_particion_envio.py (ruta-imagen) (cantidad_particiones_x) (cantidad_particiones_y)"
        )
        sys.exit(1)

    cantidad_particiones_x = int(sys.argv[2])
    cantidad_particiones_y = int(sys.argv[3])
    
    # Cantidad de instancias
    numero_instancias = cantidad_particiones_x + cantidad_particiones_y

    # Creo y levanto las maquinas
    tf = crear_instancias(numero_instancias)

    # Obtengo la ruta y cargo la imagen
    ruta_img = sys.argv[1]
    imagen = cv2.imread(ruta_img)

    # Obtener el nombre del archivo sin la extensión
    nombre_archivo = os.path.splitext(os.path.basename(ruta_img))[0]

    # Particiono las imagenes
    particiones = particionar_imagen(
        imagen, cantidad_particiones_x, cantidad_particiones_y
    )  # Cantidad de particiones en X y Y

    # Obtengo las IP de cada instancia y se la paso al encargado de enviar las peticiones
    proyecto = "sdypp-2024"
    zona = "us-east4-a"

    # Envio todas las particiones para que los workers apliquen sobel, y la guardo en un arreglo
    particiones_sobel = particionar_enviar_imagen(
        lista_instancias(proyecto, zona), particiones
    )

    # Uno las particiones y guardo la imagen
    mi_imagen = unir_particiones(particiones_sobel)

    # Guardo la imagen
    cv2.imwrite(nombre_archivo + "_sobel.jpg", mi_imagen)
    print("Imagen filtrada con exito!")

    # Terminado el trabajo, borro las maquians
    #return_code, stdout, stderr = tf.destroy()
    #if return_code != 0:
    #    print("Error durante terraform destroy:", stderr)
    #    exit(1)
