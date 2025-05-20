FROM python:3.9-slim

# Install Java, curl, and system deps
RUN apt-get update && apt-get install -y \
    default-jre \
    curl \
    && apt-get clean

# Set Java home for Spark
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Download Kafka connector JAR
RUN mkdir -p /opt/spark/jars && \
    curl -L -o /opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.0.jar \
    https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.0/spark-sql-kafka-0-10_2.12-3.5.0.jar

# Set PySpark to load it automatically
ENV PYSPARK_SUBMIT_ARGS="--jars /opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.0.jar pyspark-shell"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app