#!/bin/bash

echo "Waiting for Kafka broker..."
sleep 10

TOPIC="iris-stream"
BROKER="kafka:9092"

until /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server $BROKER --list &>/dev/null
do
  echo "Kafka not ready, retrying in 5s..."
  sleep 5
done

echo "Kafka is ready."

EXISTS=$(/opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server $BROKER --list | grep "^$TOPIC$")

if [ "$EXISTS" ]; then
  echo "Kafka topic '$TOPIC' already exists."
else
  echo "Creating Kafka topic '$TOPIC'..."
  /opt/bitnami/kafka/bin/kafka-topics.sh --create \
    --bootstrap-server $BROKER \
    --replication-factor 1 \
    --partitions 1 \
    --topic $TOPIC
fi