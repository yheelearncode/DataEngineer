# Dockerfile

# Airflow 버전을 위에서 다운로드한 docker-compose.yaml과 일치시키세요.
FROM apache/airflow:2.9.0-python3.10

# Chrome 및 ChromeDriver 설치 (root 권한 필요)
USER root

# 1. 시스템 업데이트 및 기본 도구 & GPG 키/저장소 설정 (첫 번째 RUN)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    unzip \
    ca-certificates \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# 2. Google Chrome Stable 저장소 설정 및 설치 (더 견고한 최신 APT GPG 키 권장 방식)
#    Google Chrome GPG 키를 apt-key add 대신 최신 방식으로 /usr/share/keyrings/ 에 추가
#    apt-transport-https는 이미 설치되어 있어야 하지만, 혹시 몰라 포함
#    dirmngr은 gpg 명령이 키 서버와 통신할 때 필요할 수 있습니다.
RUN apt-get update && apt-get install -y --no-install-recommends apt-transport-https dirmngr && \
    wget -qO- https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# 3. ChromeDriver 다운로드 및 설치
RUN wget -q https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.49/linux64/chromedriver-linux64.zip -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/chromedriver_dir && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver_dir/chromedriver-linux64/chromedriver && \
    mv /usr/local/bin/chromedriver_dir/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    rm -rf /usr/local/bin/chromedriver_dir

# airflow 유저로 다시 전환
USER airflow

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 스크립트 폴더를 /opt/airflow/scripts로 복사 (이후 DAG에서 import 가능하도록)
COPY scripts /opt/airflow/scripts