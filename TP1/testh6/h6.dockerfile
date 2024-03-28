FROM python:3.13.0a5-alpine3.19

RUN mkdir -p /usr/local/src/testh6

#RUN pip install requests

# Definir la variable de entorno en el Dockerfile
ENV PUERTO_EXT 8087

ADD testh6/test.py /usr/local/src/testh6/test.py
EXPOSE 8080

WORKDIR /usr/local/src/testh6

# Cambiar el propietario del archivo script.py a root
USER root
RUN chown root:root test.py

# Dar permisos de ejecución al script.py
RUN chmod +x test.py

# Definir el comando principal utilizando ENTRYPOINT
ENTRYPOINT ["python3", "test.py"]

# Proporcionar argumentos predeterminados utilizando CMD
#CMD [HOSTDest,PORTDest]
#ENTRYPOINT ["/bin/sleep", "10"] 