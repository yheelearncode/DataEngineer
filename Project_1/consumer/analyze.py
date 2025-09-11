import json
from kafka import KafkaConsumer
import sqlite3

# Kafka Consumer 설정
consumer = KafkaConsumer(
    'stock_topic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

# SQLite DB 연결 및 테이블 생성
conn = sqlite3.connect('stock_data.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    name TEXT,
    change TEXT
)
''')
conn.commit()

print('Kafka Consumer 시작...')
for message in consumer:
    data = message.value
    print('받은 데이터:', data)
    cursor.execute(
        'INSERT INTO stocks (ticker, name, change) VALUES (?, ?, ?)',
        (data['ticker'], data['name'], data['change'])
    )
    conn.commit()

conn.close()
