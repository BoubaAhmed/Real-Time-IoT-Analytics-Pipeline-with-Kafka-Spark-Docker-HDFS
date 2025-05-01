from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic, ConfigResource
from kafka.errors import TopicAlreadyExistsError
import json
import time
import random
from retrying import retry
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@retry(stop_max_attempt_number=10, wait_fixed=5000)
def create_producer():
    try:
        # Configure topic retention when creating producer
        admin_client = KafkaAdminClient(
            bootstrap_servers='kafka:9092',
            api_version_auto_timeout_ms=3000
        )
        
        # Try to create topic with retention settings
        try:
            admin_client.create_topics([
                NewTopic(
                    name='temperature_data',
                    num_partitions=1,
                    replication_factor=1,
                    topic_configs={'retention.ms': '3600000'}  # 1 hour retention
                )
            ])
            logger.info("Created topic with 1-hour retention")
        except TopicAlreadyExistsError:
            # Update existing topic configuration
            config_resource = ConfigResource(
                resource_type='TOPIC',
                name='temperature_data',
                configs={'retention.ms': '3600000'}
            )
            admin_client.alter_configs([config_resource])
            logger.info("Updated topic retention to 1 hour")
        
        producer = KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3,
            linger_ms=1000,
            api_version_auto_timeout_ms=3000
        )
        return producer
        
    except Exception as e:
        logger.error(f"Kafka setup failed: {str(e)}")
        raise

def delivery_callback(err, msg):
    """Delivery report callback"""
    if err:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.debug(f"Message delivered to {msg.topic}[{msg.partition}] @ offset {msg.offset}")

def cleanup_old_messages():
    """Force log cleanup if needed"""
    try:
        admin = KafkaAdminClient(bootstrap_servers='kafka:9092')
        # This forces Kafka to immediately clean up old segments
        admin.delete_records({
            'temperature_data': {
                0: 0  # Delete all messages older than retention period
            }
        })
        logger.debug("Triggered log compaction")
    except Exception as e:
        logger.warning(f"Cleanup failed: {str(e)}")

# Initialize producer
producer = create_producer()
last_minute_sent = None

while True:
    try:
        current_minute = datetime.now().minute
        
        if current_minute != last_minute_sent:
            data = {
                "timestamp": int(time.time()),
                "sensor_id": f"sensor{random.randint(1,3)}",
                "temperature": round(random.uniform(20, 100), 2)
            }
            
            # Send message with delivery callback
            producer.send(
                'temperature_data',
                value=data
            ).add_callback(lambda m: delivery_callback(None, m))
            
            # Force cleanup every 10 minutes
            if current_minute % 10 == 0:
                cleanup_old_messages()
            
            logger.info(f"Sent data: {json.dumps(data)}")
            last_minute_sent = current_minute
        
        time.sleep(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        try:
            producer.close()
        except Exception:
            pass
        producer = create_producer()
        time.sleep(5)