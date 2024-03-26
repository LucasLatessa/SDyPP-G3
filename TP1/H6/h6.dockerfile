FROM python:3.13.0a5-alpine3.19

RUN mkdir -p /usr/local/src/H6

ADD H6/Serv_CliH6.py /usr/local/src/H6/Serv_CliH6.py
ADD H6/RegistroContactos.py /usr/local/src/H6/RegistroContactos.py
EXPOSE 8080
WORKDIR /usr/local/src/H6
ENTRYPOINT ["python3", "Serv_CliH6.py"]     

#ENTRYPOINT ["/bin/sleep", "10"] 