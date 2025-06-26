from kafka import KafkaProducer
import json
import time
from alpha_vantage.timeseries import TimeSeries

API_KEY = ""

# Kafka 프로듀서 설정
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

# Alpha Vantage 설정
ts = TimeSeries(key=API_KEY, output_format="json")

# 주식 데이터 가져오기 함수
def fetch_stock_data(symbol="AAPL"):  # 예: 애플 주식
    data, meta_data = ts.get_intraday(symbol=symbol, interval="1min", outputsize="compact")
    latest_time = list(data.keys())[0]  # 가장 최근 데이터
    latest_data = data[latest_time]
    
    return {
        "transaction_id": int(time.time()),  # 고유 ID로 타임스탬프 사용
        "user_id": 1,  # 임의 값, 실제 데이터 필요 시 수정
        "amount": float(latest_data["4. close"]),  # 종가 사용
        "timestamp": time.time()
    }

# 주식 심볼 리스트 (필요에 따라 추가)
stock_symbols = ["AAPL", "MSFT", "GOOGL"]  # 애플, 마이크로소프트, 구글

# 데이터 전송
while True:
    for symbol in stock_symbols:
        transaction = fetch_stock_data(symbol)
        producer.send("transaction", transaction)
        print(f"Sent: {transaction}")
        time.sleep(60)  # 1분 대기 (API 호출 제한 고려)