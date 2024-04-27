texto = '"imagen":"josuegaticaodato/tarea"'
partes = texto.split('/')  # Divide la cadena en partes usando '/' como separador
resultado = partes[-1]  # Selecciona la última parte después de la barra

print(resultado)  # Imprime el resultado