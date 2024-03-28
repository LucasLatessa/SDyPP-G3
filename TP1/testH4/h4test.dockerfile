FROM python:3.13.0a5-alpine3.19

RUN mkdir -p /usr/local/src/testH4

ADD testH4/test.py /usr/local/src/testH4/test.py
EXPOSE 8080

WORKDIR /usr/local/src/testH4

# Definir el comando principal utilizando ENTRYPOINT
ENTRYPOINT ["python3", "test.py"]
# Proporcionar argumentos predeterminados utilizando CMD
CMD ["hostserv", "portserv","hostdest", "portdest"]