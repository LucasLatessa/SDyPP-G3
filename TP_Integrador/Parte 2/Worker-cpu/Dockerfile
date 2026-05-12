FROM python:3.12.3-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir pika requests

COPY Shared/ ./Shared/
COPY Worker-cpu/ ./Worker-cpu/

ENV PYTHONPATH="/app"

WORKDIR /app/Worker-cpu

CMD ["python", "-u", "worker_cpu.py"]
