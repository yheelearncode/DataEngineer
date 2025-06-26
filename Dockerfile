FROM apache/airflow:2.9.0-python3.10 # Airflow 버전을 위에서 다운로드한 docker-compose.yaml과 일치시키세요.

# Chrome 및 ChromeDriver 설치 (root 권한 필요)
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/* \
&& wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
&& echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
&& apt-get update \
&& apt-get install -y google-chrome-stable \
&& rm -rf /var/lib/apt/lists/*

# ChromeDriver 설치 (Chrome 버전과 호환되는 버전으로 설치)
# Check https://chromedriver.chromium.org/downloads for compatibility
# 이 스크립트는 설치된 Chrome 버전에 맞는 ChromeDriver를 자동으로 찾으려고 시도합니다.
RUN CHROME_VERSION=$(google-chrome --version | awk -F' ' '{print $3}' | awk -F'.' '{print $1}') \
    && CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}" | cut -d'.' -f1,2) \
    && wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

# airflow 유저로 다시 전환
USER airflow

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 스크립트 폴더를 /opt/airflow/scripts로 복사 (이후 DAG에서 import 가능하도록)
COPY scripts /opt/airflow/scripts