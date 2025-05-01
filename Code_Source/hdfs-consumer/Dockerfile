FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip --trusted-host pypi.python.org --default-timeout=100 && \
    pip install --trusted-host pypi.python.org --default-timeout=100 \
    hdfs \
    kafka-python

WORKDIR /app
COPY hdfs_consumer.py .
CMD ["python", "hdfs_consumer.py"]