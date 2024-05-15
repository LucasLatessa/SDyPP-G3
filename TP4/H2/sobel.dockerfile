FROM  python:3.9.19-alpine3.19

COPY requirements.txt /usr/local/src/TP4/H2/requirements.txt
WORKDIR /usr/local/src/TP4/H2
RUN apt-get update && pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /usr/local/src/TP4/H2

ADD servidor_sobel.py /usr/local/src/TP4/H2/servidor_sobel.py

EXPOSE 5000
WORKDIR /usr/local/src/TP4/H2
ENV FLASK_APP=servidor_sobel.py    
CMD ["python", "servidor_sobel.py"]