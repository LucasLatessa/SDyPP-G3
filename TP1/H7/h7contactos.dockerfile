FROM python:3.13.0a5-alpine3.19

RUN mkdir -p /usr/local/src/H7

ADD H7/RegistroContactos.py /usr/local/src/H7/RegistroContactos.py
EXPOSE 8080
WORKDIR /usr/local/src/H7
ENTRYPOINT ["python3", "RegistroContactos.py"] 

#ENTRYPOINT ["/bin/sleep", "10"] 