def crear_instancia(nombre,zone, project_id, instancia_cliente):
    # Definir la configuración de la instancia
    instance_body = {
        "name": f"{nombre}",
        "machine_type": f"zones/{zone}/machineTypes/n1-standard-1",
        "disks": [
            {
                "boot": True,
                "auto_delete": True,
                "initialize_params": {
                    "source_image": "projects/debian-cloud/global/images/family/debian-10"
                }
            }
        ],
        "network_interfaces": [
            {
                "network": "global/networks/default"
            }
        ]
    }

    # Crear la instancia
    operation = instancia_cliente.insert(project=project_id, zone=zone, instance_resource=instance_body)

    print("Creando la instancia...")
    operation.result()
    print("Instancia creada exitosamente.")

def listar_instancias(zone, project_id, instancia_cliente):
    #Obtengo la lista de instancias
    lista_instancias = instancia_cliente.list(project=project_id, zone=zone)

    print("Instancias:")
    count = 1
    for instancia in lista_instancias:
        print(f" {count} | ID: {instancia.id} | Nombre: {instancia.name} | Estado: {instancia.status}")
        count += 1

def pausar_instancias(zone,project_id, nombre, instancia_cliente):
    # Detener la instancia
    instancia_cliente.stop(project=project_id, zone=zone, instance=nombre)

    print(f"Instancia '{nombre}' pausada correctamente.")