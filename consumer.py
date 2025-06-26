from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, IntegerType, FloatType, DoubleType
from kafka import KafkaConsumer
import json
from elasticsearch import Elasticsearch

# Elasticsearch 설정
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "qu=FuLvHmTRDXRavdVed"),  # 사용자의 ID/PW로 변경
    verify_certs=False  # SSL 인증 무시
)

# Spark 세션 생성
spark = SparkSession.builder.appName("TransactionProcessor").getOrCreate()

# Kafka에서 데이터 읽기
consumer = KafkaConsumer(
    "transaction",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

# 데이터 스키마 정의
schema = StructType([
    StructField("transaction_id", IntegerType(), True),
    StructField("user_id", IntegerType(), True),
    StructField("amount", FloatType(), True),
    StructField("timestamp", DoubleType(), True)
])

# 이상 탐지 기준 (예: 4000 이상 거래는 이상 거래로 간주)
THRESHOLD = 4000

for message in consumer:
    transaction = message.value
    if transaction["amount"] > THRESHOLD:
        print(f"⚠️ 이상 거래 감지: {transaction}")

        # Elasticsearch에 저장
        es.index(index="fraud_transactions", body=transaction)
