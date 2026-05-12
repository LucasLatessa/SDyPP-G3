FROM python:3.12.3-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir pika requests python-dotenv

COPY Shared/ ./Shared/
COPY Worker-cpu/ ./Worker-cpu/

ENV PYTHONPATH="/app"
ENV RABBIT_HOST=rabbitmq \
    RABBIT_PORT=5672 \
    RABBIT_USER=grupo03 \
    RABBIT_PASS=grupo03 \
    ENDPOINT_COORDINADOR=http://coordinador:5000/tarea_worker \
    COORDINADOR_URL=http://coordinador:5000 \
    WORKER_ID=worker-cpu-auto

WORKDIR /app/Worker-cpu

CMD ["python", "-u", "worker_cpu.py"]
