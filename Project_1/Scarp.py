from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from kafka import KafkaProducer
import json

# ==============================
# Kafka Producer 설정
# ==============================
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# ==============================
# Selenium 설정
# ==============================
options = Options()
options.add_argument("--headless")  # 브라우저 안 띄움
options.add_argument("window-size=1920,1080")

service = Service()
driver = webdriver.Chrome(service=service, options=options)

url = "https://kr.tradingview.com/markets/stocks-usa/market-movers-gainers/"
driver.get(url)

soup = BeautifulSoup(driver.page_source, "html.parser")

# ==============================
# 데이터 파싱 (행 단위 접근)
# ==============================
rows = soup.select("tr[data-rowkey]")
last_data = {}

for row in rows:
    try:
        # 티커 & 회사명
        ticker = row.select_one("a.tickerName-GrtoTeat").get_text(strip=True)
        name = row.select_one("sup.tickerDescription-GrtoTeat").get_text(strip=True)

        # 모든 열(td) 가져오기
        cols = row.select("td")

        # 2번째 td → 변화율(%)
        change = cols[1].get_text(strip=True) if len(cols) > 1 else "N/A"

        # 3번째 td → 가격
        price = cols[2].get_text(strip=True) if len(cols) > 2 else "N/A"

        # 4번째 td → 시가총액
        market_cap = cols[3].get_text(strip=True) if len(cols) > 3 else "N/A"

        # 5번째 td → 거래량
        volume = cols[4].get_text(strip=True) if len(cols) > 4 else "N/A"

        # 메시지 생성
        data = {
            "ticker": ticker,
            "name": name,
            "change": change,
            "price": price,
            "market_cap": market_cap,
            "volume": volume
        }

        # 변화율이 바뀐 경우만 Kafka 전송 (중복 방지)
        if last_data.get(ticker) != data["change"]:
            producer.send("stock_topic", value=data).get(timeout=10)
            last_data[ticker] = data["change"]

        print(data)

    except Exception as e:
        print(f"[ERROR] {e}")

# ==============================
# 마무리
# ==============================
producer.flush()
driver.quit()
