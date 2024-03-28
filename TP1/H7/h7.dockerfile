FROM python:3.13.0a5-alpine3.19

RUN mkdir -p /usr/local/src/H7

# Definir la variable de entorno en el Dockerfile, por defecto 8087
ENV PUERTO_EXT 8087

RUN pip install requests

ADD H7/Serv_CliH7.py /usr/local/src/H7/Serv_Cli.py
EXPOSE 8080

WORKDIR /usr/local/src/H7

# Definir el comando principal utilizando ENTRYPOINT
ENTRYPOINT ["python3", "Serv_Cli.py"]

# Proporcionar argumentos predeterminados utilizando CMD
CMD [HOSTDest,PORTDest]
#ENTRYPOINT ["/bin/sleep", "10"] 