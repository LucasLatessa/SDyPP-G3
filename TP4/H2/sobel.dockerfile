FROM python:3.9-slim

#Instalo las dependencias
WORKDIR /app
COPY requirements.txt .

#Dependencias necesarios para OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

RUN pip install --no-cache-dir -r requirements.txt

ADD servidor_sobel.py /app/servidor_sobel.py

EXPOSE 5000

# Establece la variable de entorno para Flask
ENV FLASK_APP=servidor_sobel.py

# Comando para ejecutar la aplicación
CMD ["python", "servidor_sobel.py"]