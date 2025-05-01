from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, struct, to_json, avg, lit, when, from_unixtime, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, TimestampType
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_spark_session():
    logger.info("Creating Spark session...")
    return SparkSession.builder \
        .appName("ThermoAlertProcessor") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
        .config("spark.sql.shuffle.partitions", "2") \
        .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
        .getOrCreate()

def main():
    logger.info("Starting main process...")
    spark = create_spark_session()
    
    # Define input schema matching producer's format
    input_schema = StructType([
        StructField("timestamp", LongType()),  # Unix timestamp in seconds
        StructField("sensor_id", StringType()),
        StructField("temperature", DoubleType())
    ])
    logger.info("Input schema defined.")
    
    # Read from Kafka
    logger.info("Reading data from Kafka topic 'temperature_data'...")
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "temperature_data") \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()
    logger.info("Successfully subscribed to Kafka topic 'temperature_data'.")
    
    # Log schema of the Kafka DataFrame
    kafka_df.printSchema()
    
    # Parse JSON and convert timestamp to proper TimestampType
    logger.info("Parsing data from Kafka...")
    parsed_df = kafka_df.select(
        from_json(col("value").cast("string"), input_schema).alias("data")
    ).select(
        col("data.timestamp").alias("event_timestamp"),  # Keep original timestamp as long
        col("data.sensor_id"),
        col("data.temperature"),
        (col("data.timestamp").cast("timestamp")).alias("event_time")  # Convert to proper timestamp type
    )
    logger.info("Data parsing complete.")
    
    # Log schema of the parsed DataFrame
    parsed_df.printSchema()

    # Add severity classification (aligned with producer's 20-100 range)
    logger.info("Classifying severity levels...")
    classified_df = parsed_df.withColumn(
        "severity",
        when(col("temperature") > 90, "CRITICAL")
        .when(col("temperature") > 80, "HIGH")
        .when(col("temperature") > 70, "MEDIUM")
        .otherwise("NORMAL")
    )
    logger.info("Severity classification complete.")
    
    # Log some rows from the classified DataFrame
    classified_df.writeStream \
        .foreachBatch(lambda batch_df, _: logger.info(f"Classified batch received: {batch_df.show(truncate=False)}")) \
        .start()
    
    # Generate instant alerts (immediate notifications)
    logger.info("Generating instant alerts...")
    instant_alerts = classified_df.filter(
        (col("severity") == "CRITICAL") | (col("severity") == "HIGH")
    ).withColumn(
        "alert_type", lit("instant_alert")
    ).withColumn(
        "alert_timestamp", col("event_timestamp")  # Use original event timestamp
    )
    logger.info("Instant alerts generation complete.")
    
    # Generate windowed alerts (aggregate over 5-minute windows)
    logger.info("Generating windowed alerts...")
    windowed_alerts = classified_df \
        .withWatermark("event_time", "10 minutes") \
        .groupBy(
            window(col("event_time"), "5 minutes"),
            col("sensor_id")
        ) \
        .agg(
            avg("temperature").alias("avg_temp"),
            avg(when(col("severity").isin(["CRITICAL", "HIGH"]), 1).otherwise(0)).alias("alert_ratio")
        ) \
        .filter(
            (col("avg_temp") > 75) | (col("alert_ratio") > 0.3)  # Lower ratio threshold
        ) \
        .withColumn(
            "alert_type", lit("windowed_alert")
        )
    logger.info("Windowed alerts generation complete.")
    
    # Prepare alerts for Kafka
    logger.info("Preparing alerts for publishing to Kafka...")
    alerts_to_publish = instant_alerts.select(
        to_json(struct(
            "event_timestamp",
            "sensor_id",
            "temperature",
            "severity",
            "alert_type",
            "alert_timestamp"
        )).alias("value")
    ).union(
        windowed_alerts.select(
            to_json(struct(
                "window",
                "sensor_id",
                "avg_temp",
                "alert_ratio",
                "alert_type"
            )).alias("value")
        )
    )
    logger.info("Alerts prepared for publishing.")
    
    # Write to Kafka
    logger.info("Starting streaming query to write alerts to Kafka topic 'temperature_alerts'...")
    query = alerts_to_publish.writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("topic", "temperature_alerts") \
        .option("checkpointLocation", "/tmp/alert_checkpoints") \
        .outputMode("append") \
        .start()
    logger.info("Streaming query started. Waiting for termination...")
    
    query.awaitTermination()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Processor failed: {str(e)}", exc_info=True)
        raise