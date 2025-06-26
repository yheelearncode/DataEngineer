from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from elasticsearch import Elasticsearch
import time

# Elasticsearch 설정 (기존 설정 재사용)
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "qu=FuLvHmTRDXRavdVed"),
    verify_certs=False
)

# Dash 앱 초기화
app = Dash(__name__)

# 레이아웃 정의
app.layout = html.Div([
    html.H1("실시간 거래 대시보드"),
    dcc.Interval(id="interval-component", interval=2*1000, n_intervals=0),  # 2초마다 업데이트
    dcc.Graph(id="transaction-graph"),
    dcc.Graph(id="anomaly-graph")
])

# Elasticsearch에서 데이터 가져오기
def fetch_transactions():
    query = {"query": {"match_all": {}}}
    response = es.search(index="fraud_transactions", body=query, size=100)  # 최근 100개 이상 거래
    hits = response["hits"]["hits"]
    data = [hit["_source"] for hit in hits]
    return pd.DataFrame(data)

# 콜백 함수: 그래프 업데이트
@app.callback(
    [Output("transaction-graph", "figure"), Output("anomaly-graph", "figure")],
    [Input("interval-component", "n_intervals")]
)
def update_graphs(n):
    # 데이터 가져오기
    df = fetch_transactions()

    # 전체 거래 그래프 (amount vs timestamp)
    transaction_fig = px.scatter(
        df,
        x="timestamp",
        y="amount",
        title="전체 거래 내역",
        labels={"timestamp": "시간", "amount": "거래 금액"},
        hover_data=["transaction_id", "user_id"]
    )

    # 이상 거래 필터링 (amount > 4000)
    anomaly_df = df[df["amount"] > 4000]
    anomaly_fig = px.scatter(
        anomaly_df,
        x="timestamp",
        y="amount",
        title="이상 거래 내역",
        labels={"timestamp": "시간", "amount": "거래 금액"},
        hover_data=["transaction_id", "user_id"],
        color_discrete_sequence=["red"]  # 이상 거래는 빨간색으로 표시
    )

    return transaction_fig, anomaly_fig

# 앱 실행
if __name__ == "__main__":
    app.run(debug=True)