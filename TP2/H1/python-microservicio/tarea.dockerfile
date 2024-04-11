FROM  python:3.9.19-alpine3.19

RUN pip install flask

RUN mkdir -p /usr/local/src/H2

ADD tarea.py /usr/local/src/H2/tarea.py

EXPOSE 5000
WORKDIR /usr/local/src/H2
ENV FLASK_APP=tarea.py    
CMD ["python", "tarea.py"]