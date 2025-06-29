import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import os

def scrape_and_save_tradingview_data():
    print("스크래핑 및 데이터 저장 작업을 시작합니다...")

    # PostgreSQL 연결 설정 (환경 변수 사용)
    # Docker Desktop의 WSL2 통합으로 로컬 PostgreSQL에 접근할 때 'host.docker.internal' 사용
    db_host = os.getenv("POSTGRES_HOST", "host.docker.internal")
    db_name = os.getenv("POSTGRES_DB", "test")
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "zxasqw12")

    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(
            host=db_host,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        print("PostgreSQL 연결 성공!")

        # 테이블이 없으면 생성 (멱등성 확보)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS us_stock_gainers (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(255) NOT NULL,
                name VARCHAR(255),
                change_percent NUMERIC(10, 2),
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("테이블 존재 여부 확인 및 생성 완료.")

        # Selenium 설정
        options = Options()
        options.add_argument('--headless')           # GUI 없이 실행
        options.add_argument('--no-sandbox')         # 보안 이슈로 필요
        options.add_argument('--disable-dev-shm-usage') # 메모리 사용 최적화
        options.add_argument('--disable-gpu')        # GPU 사용 안 함 (일부 시스템에서 문제 방지)
        options.add_argument('--window-size=1920,1080') # 웹 페이지 전체 렌더링을 위해

        # Chrome Driver 경로 설정 (Dockerfile에서 /usr/local/bin/chromedriver에 설치됨)
        service = Service() # 기본적으로 PATH에서 chromedriver를 찾음

        driver = None
        try:
            driver = webdriver.Chrome(service=service, options=options)
            print("Selenium Chrome 드라이버 초기화 성공 (Headless 모드).")

            url = "https://kr.tradingview.com/markets/stocks-usa/market-movers-gainers/"
            driver.get(url)
            print(f"URL 접속: {url}")

            time.sleep(10) # 페이지 로딩 및 JavaScript 실행을 위해 충분히 기다립니다.
            soup = BeautifulSoup(driver.page_source, "html.parser")
            print("페이지 소스 파싱 완료.")

            rows = soup.select('tr[data-rowkey]')
            if not rows:
                print("데이터를 찾을 수 없습니다. 'tr[data-rowkey]' 셀렉터를 확인하세요.")

            # 상위 5개 종목만 처리
            for row in rows[:5]:
                ticker_tag = row.select_one('a.tickerNameBox-GrtoTeat')
                td_tags = row.select('td')

                if ticker_tag and len(td_tags) >= 2:
                    title = ticker_tag.get("title")
                    symbol = ticker_tag.text.strip()
                    change_raw = td_tags[1].text.strip()

                    try:
                        # %와 + 제거, 쉼표 제거 후 float으로 변환
                        change = float(change_raw.replace('%', '').replace('+', '').replace(',', ''))
                    except ValueError as e:
                        print(f"변경률 파싱 오류 ({change_raw}): {e}")
                        continue

                    cursor.execute("""
                        INSERT INTO us_stock_gainers (symbol, name, change_percent)
                        VALUES (%s, %s, %s)
                    """, (symbol, title, change))

                    print(f"[저장 준비] Symbol: {symbol}, Name: {title}, Change: {change}%")

            conn.commit()
            print("모든 데이터 저장 완료 및 커밋 성공!")

        except Exception as e:
            print(f"Selenium 또는 스크래핑 중 오류 발생: {e}")
            if conn:
                conn.rollback()
                print("데이터베이스 트랜잭션 롤백 완료.")
        finally:
            if driver:
                driver.quit()
                print("Selenium 드라이버 종료.")

    except psycopg2.Error as e:
        print(f"PostgreSQL 연결 또는 쿼리 오류: {e}")
    except Exception as e:
        print(f"예기치 않은 오류 발생: {e}")
    finally:
        if cursor:
            cursor.close()
            print("PostgreSQL 커서 닫기.")
        if conn:
            conn.close()
            print("PostgreSQL 연결 닫기.")

if __name__ == "__main__":
    scrape_and_save_tradingview_data()