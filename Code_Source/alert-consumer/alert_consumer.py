from kafka import KafkaConsumer
from hdfs import InsecureClient
import json
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_to_hdfs(url, user, retries=5, delay=5):
    """Connect to HDFS with retries."""
    for attempt in range(retries):
        try:
            client = InsecureClient(url, user=user, timeout=10)
            logger.info("Connected to HDFS successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to connect to HDFS (Attempt {attempt + 1}/{retries}): {str(e)}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise

def connect_to_kafka(topic, bootstrap_servers, retries=5, delay=5):
    """Connect to Kafka with retries."""
    for attempt in range(retries):
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=False
            )
            logger.info("Connected to Kafka cluster")
            return consumer
        except Exception as e:
            logger.error(f"Failed to connect to Kafka (Attempt {attempt + 1}/{retries}): {str(e)}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise

def process_message(client, message):
    """Process a single Kafka message and save it to HDFS."""
    try:
        data = message.value
        json_data = json.dumps(data)
        bytes_data = json_data.encode('utf-8')

        # Create structured path in HDFS directly under /alerts
        if 'window' in data:  # Windowed average alert
            path = f"/alerts/avg_temp/{data['sensor_id']}/{data['window']['start']}.json"
        else:  # Instant temperature alert
            path = f"/alerts/instant/{data['sensor_id']}/{data['event_timestamp']}.json"

        # Write to HDFS
        with client.write(path, overwrite=True) as writer:
            writer.write(bytes_data)

        logger.info(f"Wrote {len(bytes_data)} bytes to {path}")

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)

def main():
    logger.info("Initializing Alert Consumer...")

    try:
        # HDFS Client setup with retries
        hdfs_client = connect_to_hdfs(url='http://hadoop:9870', user='root')

        # Kafka Consumer setup with retries
        kafka_consumer = connect_to_kafka(topic='temperature_alerts', bootstrap_servers='kafka:9092')

        # Process Kafka messages
        for message in kafka_consumer:
            process_message(hdfs_client, message)

    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()