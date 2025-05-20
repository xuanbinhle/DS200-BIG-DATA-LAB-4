import pandas as pd
from kafka import KafkaProducer
import json
import time

# Load Iris dataset from iris.data
df = pd.read_csv("data/iris.data", header=None)
df.columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "label"]

# Drop empty rows (some exist at the end)
df = df.dropna()

# Encode labels to integers
label_map = {name: i for i, name in enumerate(df["label"].unique())}
df["label"] = df["label"].map(label_map)

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Send each row to Kafka
for _, row in df.iterrows():
    data = row.to_dict()
    producer.send("iris-stream", value=data)
    time.sleep(0.05)

producer.flush()
print("Sent all Iris data to Kafka.")