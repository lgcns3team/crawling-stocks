FROM python:3.11-slim

# 로그 바로 출력
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# requirements 먼저 복사 (캐시 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 소스 복사
COPY . .

# 실행 파일
CMD ["python", "price_collector.py"]
