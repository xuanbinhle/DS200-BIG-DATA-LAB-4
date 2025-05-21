import pandas as pd
from kafka import KafkaProducer
import json
import time

# Load dataset
df = pd.read_csv("data/iris.data", header=None)
df.columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "label"]
df = df.dropna()

label_map = {name: i for i, name in enumerate(df["label"].unique())}
df["label"] = df["label"].map(label_map)

# Group by label and shuffle each group
grouped = {label: group.sample(frac=1, random_state=42).reset_index(drop=True)
           for label, group in df.groupby("label")}

# Interleave rows from each group to build balanced batches
min_len = min(len(g) for g in grouped.values())
interleaved_rows = []
for i in range(min_len):
    for label in sorted(grouped.keys()):
        interleaved_rows.append(grouped[label].iloc[i])

# Send to Kafka in balanced batches
producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

batch_size = 9  # divisible by 3 → 3 samples per label per batch
print("Sending balanced batches to Kafka...")

for i in range(0, len(interleaved_rows), batch_size):
    batch = interleaved_rows[i:i+batch_size]
    for row in batch:
        producer.send("iris-stream", value=row.to_dict())
    print(f"Sent batch {i // batch_size}")
    time.sleep(5)  

producer.flush()
print("Done sending balanced batches.")