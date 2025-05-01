FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip --trusted-host pypi.python.org --default-timeout=100 && \
    pip install --trusted-host pypi.python.org --default-timeout=100 \
    kafka-python \
    hdfs

WORKDIR /app
COPY alert_consumer.py .
CMD ["python", "alert_consumer.py"]