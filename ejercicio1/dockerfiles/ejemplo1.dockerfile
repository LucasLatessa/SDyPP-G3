FROM python:3 
# FROM DEBIAN 12 ISO 
RUN mkdir /usr/local/src/pythonapp
RUN mkdir /usr/local/src/pythonapp/htmls

ADD src/index.html /usr/local/src/pythonapp/htmls/index.html
ADD src/main.py /usr/local/src/pythonapp/server.py

EXPOSE 8080
WORKDIR /usr/local/src/pythonapp
ENTRYPOINT ["python3", "server.py"]