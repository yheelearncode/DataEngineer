from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# scripts 폴더에 있는 tradingview_scraper.py 모듈을 임포트합니다.
# Airflow 컨테이너에서 /opt/airflow/scripts가 PYTHONPATH에 포함되어 있으므로 직접 임포트 가능합니다.
from scripts.tradingview_scraper import scrape_and_save_tradingview_data

with DAG(
    dag_id='tradingview_stock_gainers_hourly_scraper',
    start_date=datetime(2023, 1, 1), # DAG의 시작 날짜 (이 날짜 이전의 스케줄은 실행되지 않음)
    schedule_interval=timedelta(hours=1), # 매시간 실행 (Crontab 형식으로 '0 *d * * *' 도 가능)
    catchup=False, # start_date 이후의 과거 스케줄을 실행할지 여부. False로 설정하여 과거 실행 방지.
    tags=['stock', 'scraping', 'tradingview'],
    default_args={
        'owner': 'airflow',
        'depends_on_past': False, # 이전 태스크 실패와 관계없이 실행
        'email_on_failure': False, # 실패 시 이메일 알림
        'email_on_retry': False,   # 재시도 시 이메일 알림
        'retries': 3,              # 실패 시 3번 재시도
        'retry_delay': timedelta(minutes=5), # 재시도 간격
    },
) as dag:
    # PythonOperator를 사용하여 정의한 함수를 실행합니다.
    scrape_task = PythonOperator(
        task_id='scrape_and_save_data', # 태스크 고유 ID
        python_callable=scrape_and_save_tradingview_data, # 호출할 함수
    )