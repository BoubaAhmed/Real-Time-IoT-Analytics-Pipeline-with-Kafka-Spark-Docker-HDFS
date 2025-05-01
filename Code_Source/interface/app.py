from flask import Flask, render_template, jsonify
from kafka import KafkaConsumer
import json
import threading
import logging
from time import sleep
from datetime import datetime

app = Flask(__name__)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KafkaManager:
    def __init__(self):
        self.data = []
        self.alerts = []
        self.running = True
        self.setup_consumers()

    def get_consumer(self, topic):
        while self.running:
            try:
                consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers='kafka:9092',
                    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                    auto_offset_reset='latest',
                    group_id='flask-consumer-group',
                    consumer_timeout_ms=1000
                )
                logger.info(f"Connected to Kafka topic {topic}")
                return consumer
            except Exception as e:
                logger.error(f"Connection error: {e} - Retrying in 5s...")
                sleep(5)

    def setup_consumers(self):
        logger.info("Starting consumers...")
        threading.Thread(target=self.process_data, daemon=True).start()
        threading.Thread(target=self.process_alerts, daemon=True).start()

    def process_data(self):
        logger.info("Starting data consumer")
        consumer = self.get_consumer('temperature_data')
        while self.running:
            try:
                for msg in consumer:
                    data = msg.value
                    # Convertir le timestamp en millisecondes
                    data['timestamp'] = data['timestamp'] * 1000
                    logger.debug(f"Received data: {data}")
                    self.data.append(data)
                    if len(self.data) > 10:
                        self.data.pop(0)
            except Exception as e:
                logger.error(f"Data processing error: {str(e)}")
                sleep(1)

    def process_alerts(self):
        logger.info("Starting alert consumer")
        consumer = self.get_consumer('temperature_alerts')
        while self.running:
            try:
                for msg in consumer:
                    alert = msg.value
                    logger.debug(f"Received alert: {alert}")
                    
                    normalized = None
                    try:
                        # Determine alert type and extract data accordingly
                        alert_type = alert['alert_type'].replace('_alert', '')
                        
                        if alert_type == 'instant':
                            # Handle instant alerts
                            timestamp = int(alert['event_timestamp']) * 1000  # Convert seconds to milliseconds
                            temperature = alert['temperature']
                            severity = alert.get('severity', 'UNKNOWN')
                        elif alert_type == 'windowed':
                            # Handle windowed alerts
                            # Parse window start time from ISO 8601 string
                            start_str = alert['window']['start']
                            dt = datetime.strptime(start_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                            timestamp = int(dt.timestamp() * 1000)
                            temperature = alert['avg_temp']
                            severity = 'WINDOWED_ALERT'  # Custom severity for windowed alerts
                        else:
                            logger.warning(f"Unknown alert type: {alert_type}")
                            continue
                        
                        normalized = {
                            'timestamp': timestamp,
                            'sensor_id': alert['sensor_id'],
                            'alert_type': alert_type,
                            'temperature': float(temperature),
                            'severity': severity
                        }
                        
                    except KeyError as e:
                        logger.error(f"Missing key in alert data: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing alert: {e}")
                        continue
                    
                    self.alerts.append(normalized)
                    if len(self.alerts) > 10:  # Keep last 10 alerts
                        self.alerts.pop(0)
                    
            except Exception as e:
                logger.error(f"Alert processing error: {str(e)}")
                sleep(1)

kafka_manager = KafkaManager()

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/data')
def get_data():
    return jsonify({
        'temperature': kafka_manager.data,
        'alerts': sorted(kafka_manager.alerts, key=lambda x: x['timestamp'], reverse=True)
    })

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'OK',
        'data_points': len(kafka_manager.data),
        'active_alerts': len(kafka_manager.alerts),
        'last_update': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)