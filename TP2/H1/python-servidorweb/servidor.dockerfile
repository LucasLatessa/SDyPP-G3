FROM  python:3.9.19-alpine3.19

COPY requirements.txt /usr/local/src/H2/requirements.txt
WORKDIR /usr/local/src/H2
RUN pip install -r requirements.txt

RUN mkdir -p /usr/local/src/H2

ADD servidorweb.py /usr/local/src/H2/servidorweb.py

EXPOSE 8080
WORKDIR /usr/local/src/H2
ENV FLASK_APP=servidorweb.py    
CMD ["python", "servidorweb.py"]