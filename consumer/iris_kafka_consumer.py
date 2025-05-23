import os
import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score
import joblib  

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, FloatType, IntegerType, StringType
from pyspark.sql import DataFrame
import traceback

model = SGDClassifier(loss="log_loss", max_iter=1000, tol=1e-3)
# Initialize model
model_initialized = False

LOG_PATH = "logs/training_log.csv"
MODEL_DIR = "models"
os.makedirs("logs", exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
if not os.path.exists(LOG_PATH):
    pd.DataFrame(columns=["batch_id", "accuracy"]).to_csv(LOG_PATH, index=False)

SAVE_EVERY = 10
batch_counter = 0

# Spark setup
spark = SparkSession.builder.appName("KafkaMLConsumer").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Define schema
schema = StructType() \
    .add("sepal_length", FloatType()) \
    .add("sepal_width", FloatType()) \
    .add("petal_length", FloatType()) \
    .add("petal_width", FloatType()) \
    .add("label", StringType())

# Read stream from Kafka
try:
    df = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "iris-stream") \
        .option("startingOffsets", "earliest") \
        .load()
except Exception as e:
    print("❌ Spark failed to load Kafka stream:")
    traceback.print_exc()
    raise

json_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

json_df.printSchema()

# Training function for each batch
def train_batch(batch_df, batch_id):
    global batch_counter, model, model_initialized
    if batch_df.count() == 0:
        print(f"[Batch {batch_id}] No data received at all.")
        return

    pdf = batch_df.toPandas()
    print(f"[Batch {batch_id}] Raw batch:\n{pdf.head()}") 

    pdf = pdf.dropna(subset=["label"])
    if pdf.empty:
        print(f"[Batch {batch_id}] Skipped batch: all labels were NaN.")
        return

    X = pdf[["sepal_length", "sepal_width", "petal_length", "petal_width"]]
    y = pdf["label"]
    y = pdf["label"].astype(float).astype(int)

    if len(set(y)) < 1:
        print(f"[Batch {batch_id}] Skipped: No valid labels.")
        return

    if not model_initialized:
        model.partial_fit(X, y, classes=[0, 1, 2])  
        model_initialized = True
    else:
        model.partial_fit(X, y) 

    preds = model.predict(X)
    acc = accuracy_score(y, preds)
    print(f"[Batch {batch_id}] Accuracy: {acc:.2%}")

    # Logging
    pd.DataFrame([[batch_id, acc]], columns=["batch_id", "accuracy"]) \
        .to_csv(LOG_PATH, mode="a", header=False, index=False)

    batch_counter += 1
    if batch_counter % SAVE_EVERY == 0:
        model_path = os.path.join(MODEL_DIR, f"iris_sdg_model_batch{batch_id}.pkl")
        joblib.dump(model, model_path)
        print(f"[Checkpoint] Saved model at {model_path}")

# Start streaming
json_df.writeStream.foreachBatch(train_batch).start().awaitTermination()
# json_df.writeStream \
#     .format("console") \
#     .outputMode("append") \
#     .start() \
#     .awaitTermination()
