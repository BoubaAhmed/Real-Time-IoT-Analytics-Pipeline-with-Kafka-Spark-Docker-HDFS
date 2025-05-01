from hdfs import InsecureClient
from kafka import KafkaConsumer
import json
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing HDFS consumer...")
    
    try:
        client = InsecureClient('http://hadoop:9870', user='root', timeout=10)
        logger.info("Connected to HDFS successfully")
    except Exception as e:
        logger.error(f"HDFS connection failed: {str(e)}")
        return

    try:
        consumer = KafkaConsumer(
            'temperature_data',
            bootstrap_servers='kafka:9092',
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=False
        )
        logger.info("Connected to Kafka cluster")
    except Exception as e:
        logger.error(f"Kafka connection failed: {str(e)}")
        return

    for message in consumer:
        try:
            data = message.value
            json_data = json.dumps(data)
            bytes_data = json_data.encode('utf-8')
            path = f"/temperature_data/{data['sensor_id']}/{data['timestamp']}.json"
            
            with client.write(path, overwrite=True) as writer:
                writer.write(bytes_data)
                
            logger.info(f"Wrote {len(bytes_data)} bytes to {path}")
            
            # Log structure every 100 messages
            if message.offset % 100 == 0:
                logger.debug("Current HDFS structure: %s", client.list('/temperature_data', status=False))
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()