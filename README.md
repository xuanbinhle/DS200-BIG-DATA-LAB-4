# Spark DL Streaming with Kafka + PyTorch

This project streams the Iris dataset from a Kafka producer and consumes it with a PyTorch model trained in real-time via Spark Structured Streaming.

## How to Run

1. Build Docker image:
   ```bash
   docker build -t iris-streaming-app .
   ```

2. Start Kafka:
   ```bash
   docker-compose up -d
   ```

3. Create Kafka topic (inside Kafka container):
   ```bash
   docker exec -it kafka bash
   kafka-topics.sh --create --topic iris-stream --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
   ```

4. Run Producer:
   ```bash
   docker run --rm --network iris-net iris-streaming-app python producer/iris_kafka_producer.py
   ```

5. Run Consumer:
   ```bash
   docker run --rm --network iris-net iris-streaming-app spark-submit consumer/iris_kafka_consumer.py
   ```

6. Evaluate model:
   ```bash
   docker run --rm -v $(pwd)/models:/app/models iris-streaming-app python model/test_model.py
   ```
# DS200-BIG-DATA-LAB-4
