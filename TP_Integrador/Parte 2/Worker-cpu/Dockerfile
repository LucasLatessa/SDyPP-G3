FROM python:3.12.3-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/Worker-cpu

RUN pip install --no-cache-dir pika requests python-dotenv

COPY Worker-cpu/worker_cpu.py ./worker_cpu.py

ENV RABBIT_HOST=rabbitmq \
    RABBIT_PORT=5672 \
    ENDPOINT_COORDINADOR=http://coordinador:5000/tarea_worker \
    COORDINADOR_URL=http://coordinador:5000 \
    WORKER_ID=worker-cpu-auto

CMD ["python", "-u", "worker_cpu.py"]