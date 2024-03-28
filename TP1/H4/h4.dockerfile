FROM python:3.13.0a5-alpine3.19

RUN mkdir -p /usr/local/src/H4

ADD H4/Serv_Cli.py /usr/local/src/H4/Serv_Cli.py
EXPOSE 8080

WORKDIR /usr/local/src/H4

COPY H4/start.sh .

# Establecer el script de inicio como el punto de entrada
#ENTRYPOINT ["sh", "start.sh"]

# Definir el comando principal utilizando ENTRYPOINT
ENTRYPOINT ["python3", "Serv_Cli.py"]
# Proporcionar argumentos predeterminados utilizando CMD

#CMD ["0.0.0.0", "8080","127.0.0.1", "8081"]
#ENTRYPOINT ["/bin/sleep", "10"] 