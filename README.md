# Iris Streaming ML Pipeline (Kafka KRaft Mode)

This project showcases a **real-time machine learning pipeline** using **Apache Kafka (KRaft mode)** and **Apache Spark Structured Streaming**. It streams the Iris dataset from a Kafka producer to a Spark consumer, classifies the data with a trained `SGDClassifier`, and evaluates the model's performance.

🔗 GitHub Repo: [xuanbinhle/DS200-BIG-DATA-LAB-4](https://github.com/xuanbinhle/DS200-BIG-DATA-LAB-4.git)

---

## Dataset

- **Name**: Iris Dataset  
- **Source**: [UCI ML Repository](https://archive.ics.uci.edu/ml/datasets/iris)
- **Features**:
  - `sepal_length`
  - `sepal_width`
  - `petal_length`
  - `petal_width`
  - `label` (class: setosa, versicolor, virginica)

---

## Model

- **Algorithm**: `SGDClassifier` from scikit-learn
- **Trained Model File**: `iris_sdg_model_batch19.pkl`
- **Final Accuracy**: **80.67%**

---

## How to Run

### 1. Build the Docker Image

```bash
docker build -t iris-streaming-app .
```

### 2. Start Kafka (KRaft mode)

```bash
docker-compose up -d
```

> Make sure your `docker-compose.yml` is configured for Kafka in **KRaft (no Zookeeper)** mode.

### 3. Create Kafka Topic

```bash
docker exec -it kafka kafka-topics.sh \
  --bootstrap-server kafka:9092 \
  --create \
  --topic iris-stream \
  --partitions 1 \
  --replication-factor 1
```

### 4. Run Kafka Producer

```bash
docker run --rm --network iris-net iris-streaming-app \
  python producer/iris_kafka_producer.py
```

### 5. Run Spark Streaming Consumer

```bash
docker run --rm \
  --network iris-net \
  -v $(pwd):/app \
  -w /app \
  iris-streaming-app \
  spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.kafka:kafka-clients:3.5.0 \
  consumer/iris_kafka_consumer.py
```

### 6. Evaluate the Model

```bash
docker run --rm -v $(pwd)/models:/app/models \
  iris-streaming-app python test_model.py
```

---

## 📌 Notes

- The project is made for LAB 4 of UIT DS200 Course.
- This project uses **Kafka with KRaft mode** (no Zookeeper).
- Model is streamed and evaluated in real time via Spark Streaming.
- Designed for educational and lightweight real-time ML workflows.