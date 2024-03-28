import subprocess

def obtener_ip_publica():
    try:
        # Ejecutar el comando curl ifconfig.me y capturar la salida
        resultado = subprocess.run(['curl', 'ifconfig.me'], capture_output=True, text=True)
        # Verificar si el comando se ejecutó correctamente
        if resultado.returncode == 0:
            return resultado.stdout.strip()  # Devolver la salida sin espacios en blanco
        else:
            print("Error al obtener la dirección IP pública.")
    except Exception as e:
        print("Error al ejecutar el comando:", e)

# Obtener y mostrar la dirección IP pública
ip_publica = obtener_ip_publica()
if ip_publica:
    print("La dirección IP pública es:", ip_publica)
