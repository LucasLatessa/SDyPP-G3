from google.cloud import compute_v1
from manejo_instancias import listar_instancias,crear_instancia,pausar_instancias

#Se crea un cliente para la API de Compute Engine (manejador de VM)
instancia_cliente = compute_v1.InstancesClient()

#Proyecto y zona
project_id = "organic-premise-416700"
zone = "us-east1-b"

menu = True
while (menu):
    print("Que quiere hacer con las instancias:")
    print("1 - Listar instancias")
    print("2 - Crear una nueva instancia")
    print("3 - Pausar una instancia")

    opcion = int(input("Eliga una opcion: "))
    if(opcion == 1):
        listar_instancias(zone,project_id,instancia_cliente)
    elif(opcion == 2):
        nombre = input("Ingrese nombre: ")
        crear_instancia(nombre,zone,project_id,instancia_cliente)
    elif(opcion == 3):
        nombre = input("Ingrese nombre de la instancia: ")
        pausar_instancias(nombre,zone,project_id,instancia_cliente)