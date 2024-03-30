import requests

# Define una lista de servidores con sus respectivas direcciones IP y puertos
servidores = [
    {"nombre": "Servidor1", "ip": "192.168.1.100", "puerto": 8080},
    {"nombre": "Servidor2", "ip": "192.168.1.101", "puerto": 8080},
    {"nombre": "Servidor3", "ip": "192.168.1.102", "puerto": 8080},
    # Añade más servidores según sea necesario
]

# Función para obtener el estado de un servidor
def obtener_estado(servidor):
    try:
        url = f"http://{servidor['ip']}:{servidor['puerto']}/status"
        response = requests.get(url)
        if response.status_code == 200:
            return servidor['nombre'], "Funcionando"
        else:
            return servidor['nombre'], "Inactivo"
    except requests.ConnectionError:
        return servidor['nombre'], "Error de conexión"

# Función para obtener el estado de todos los servidores
def obtener_estados_servidores():
    estados = []
    for servidor in servidores:
        nombre_servidor, estado = obtener_estado(servidor)
        estados.append({nombre_servidor: estado})
    return estados

# Obtener y mostrar los estados de los servidores
if __name__ == "__main__":
    estados_servidores = obtener_estados_servidores()
    for estado in estados_servidores:
        print(estado)
