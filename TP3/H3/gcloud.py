from google.cloud import compute_v1
from manejo_instancias import listar_instancias,crear_instancia,pausar_instancia, reiniciar_instancia, eliminar_instancia

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
    print("4 - Reiniciar una instancia")
    print("5 - Eliminar una instancia")
    print("")
    print("0 - Salir")

    opcion = int(input("Eliga una opcion: "))
    if(opcion == 1):
        listar_instancias(zone,project_id,instancia_cliente)
    elif(opcion == 2):
        nombre = input("Ingrese nombre: ")
        crear_instancia(nombre,zone,project_id,instancia_cliente)
    elif(opcion == 3):
        nombre = input("Ingrese nombre de la instancia: ")
        pausar_instancia(nombre,zone,project_id,instancia_cliente)
    elif(opcion == 4):
        nombre = input("Ingrese nombre de la instancia: ")
        reiniciar_instancia(nombre,zone,project_id,instancia_cliente)
    elif(opcion == 5):
        nombre = input("Ingrese nombre de la instancia: ")
        eliminar_instancia(nombre,zone,project_id,instancia_cliente)
    elif(opcion == 0):
        menu = False
        print("Adeus")