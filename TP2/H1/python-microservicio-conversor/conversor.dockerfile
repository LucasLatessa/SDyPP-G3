FROM  python:3.9.19-alpine3.19

RUN pip install flask

RUN mkdir -p /usr/local/src/H2

ADD conversor.py /usr/local/src/H2/conversor.py

EXPOSE 5000
WORKDIR /usr/local/src/H2
ENV FLASK_APP=conversor.py    
CMD ["python", "conversor.py"]