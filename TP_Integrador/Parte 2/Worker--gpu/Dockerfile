FROM nvidia/cuda:12.6.0-devel-ubuntu22.04

WORKDIR /app

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python3", "-u", "minero_gpu.py"]
