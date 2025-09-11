import sqlite3
import requests
import datetime

# DB에서 최신 급등주 데이터 조회
conn = sqlite3.connect('../stock_data.db')
cursor = conn.cursor()
cursor.execute('SELECT ticker, name, change FROM stocks ORDER BY id DESC LIMIT 10')
stocks = cursor.fetchall()
conn.close()

# 콘텐츠 생성
now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
content = f"[실시간 급등주 현황] {now}\n\n"
for ticker, name, change in stocks:
    content += f"종목: {ticker} ({name}), 등락률: {change}\n"

# 예시: 티스토리 블로그 API로 포스팅 (access_token, blogName 필요)
access_token = 'YOUR_TISTORY_ACCESS_TOKEN'
blogName = 'YOUR_BLOG_NAME'
url = f'https://www.tistory.com/apis/post/write'
data = {
    'access_token': access_token,
    'output': 'json',
    'blogName': blogName,
    'title': f'실시간 급등주 현황 ({now})',
    'content': content,
    'visibility': 3  # 3: 발행
}

response = requests.post(url, data=data)
if response.status_code == 200:
    print('블로그에 글이 성공적으로 발행되었습니다.')
else:
    print('발행 실패:', response.text)
