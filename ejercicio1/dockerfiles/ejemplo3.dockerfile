FROM python:3.13.0a5-alpine3.19

#RUN mkdir -p /usr/local/src/pythonapp
RUN mkdir -p /usr/local/src/pythonapp/htmls

ADD src/index.html /usr/local/src/pythonapp/htmls/index.html
ADD src/main.py /usr/local/src/pythonapp/server.py

EXPOSE 8080
WORKDIR /usr/local/src/pythonapp
ENTRYPOINT ["python3", "server.py"]     

#ENTRYPOINT ["/bin/sleep", "10"] 