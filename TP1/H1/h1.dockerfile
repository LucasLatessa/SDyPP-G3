FROM python:3.13.0a5-alpine3.19

RUN mkdir -p /usr/local/src/H1

ADD H1/server.py /usr/local/src/H1/server.py

EXPOSE 8080
WORKDIR /usr/local/src/H1
ENTRYPOINT ["python3", "server.py"]     

#ENTRYPOINT ["/bin/sleep", "10"] 