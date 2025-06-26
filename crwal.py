from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import psycopg2

# PostgreSQL 연결 설정
conn = psycopg2.connect(
    host="localhost",
    dbname="test",
    user="postgres",
    password="zxasqw12"
)
cursor = conn.cursor()

# Selenium 설정
options = Options()
driver = webdriver.Chrome()

url = "https://kr.tradingview.com/markets/stocks-usa/market-movers-gainers/"
driver.get(url)

time.sleep(5)
soup = BeautifulSoup(driver.page_source, "html.parser")

rows = soup.select('tr[data-rowkey]')

for row in rows[:5]:
    ticker_tag = row.select_one('a.tickerNameBox-GrtoTeat')
    td_tags = row.select('td')

    if ticker_tag and len(td_tags) >= 2:
        title = ticker_tag.get("title")             
        symbol = ticker_tag.text.strip()         
        change_raw = td_tags[1].text.strip()          
        change = float(change_raw.replace('%', '').replace('+', '').replace(',', ''))

        
        cursor.execute("""
            INSERT INTO us_stock_gainers (symbol, name, change_percent)
            VALUES (%s, %s, %s)
        """, (symbol, title, change))

        print(f"[저장 완료] {symbol} {title} {change}%")

conn.commit()
cursor.close()
conn.close()
driver.quit()
