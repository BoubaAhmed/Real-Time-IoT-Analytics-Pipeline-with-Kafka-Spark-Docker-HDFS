FROM bitnami/spark:3.3

# Copy the script into the container
COPY streaming_alerts.py /app/

# Set the working directory
WORKDIR /app

# Set the default command
CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.4", "/app/streaming_alerts.py"]