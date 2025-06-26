from fastapi import FastAPI
import psycopg2
from typing import List
from pydantic import BaseModel

app = FastAPI()

# 모델 정의
class Stock(BaseModel):
    symbol: str
    name: str
    change_percent: float
    collected_at: str

# DB 연결 함수
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        dbname="test",
        user="postgres",
        password="zxasqw12",
        port=5432
    )

@app.get("/gainers", response_model=List[Stock])
def get_gainers(limit: int = 5, min_rate: float = 5.0):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT symbol, name, change_percent, collected_at
        FROM us_stock_gainers
        WHERE change_percent >= %s
        ORDER BY change_percent DESC
        LIMIT %s
    """, (min_rate, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "symbol": row[0],
            "name": row[1],
            "change_percent": float(row[2]),
            "collected_at": row[3].strftime("%Y-%m-%d %H:%M:%S")
        }
        for row in rows
    ]
