FROM  python:3.9.19-alpine3.19

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install -r requirements.txt
COPY ..
ENV FLASK_APP=clase.py    
CMD ["flask", "run", "--host", "0.0.0.0"]
