import os

from dotenv import load_dotenv

load_dotenv()

# ================================
# KIS API 설정
# ================================
APP_KEY = os.getenv("KIS_APP_KEY")
APP_SECRET = os.getenv("KIS_APP_SECRET")

KIS_ENV = "real"

if KIS_ENV == "real":
    BASE_URL = "https://openapi.koreainvestment.com:9443"
    # 현재가 상세조회(ver2) TR (실전)
    TR_ID_PRICE = "FHPST01010000"
else:
    # 모의투자 서버 (이 TR은 모의 미지원이지만 구조만 유지)
    BASE_URL = "https://openapivts.koreainvestment.com:29443"
    TR_ID_PRICE = "FHPST01010000"

DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
# [DRY_RUN 추가]
# DRY_RUN=true 이면 DB INSERT / UPDATE를 수행하지 않는다

# ================================
# 수집 대상 종목 (Companies.id 와 동일해야 함)
# ================================
TARGET_TICKERS = [
    # 1. 반도체
    "005930",  # 삼성전자
    "000660",  # SK하이닉스
    "000990",  # DB하이텍
    "042700",  # 한미반도체

    # 2. 모빌리티
    "005380",  # 현대차
    "000270",  # 기아
    "012330",  # 현대모비스
    "204320",  # HL만도

    # 3. 2차전지
    "006400",  # 삼성SDI
    "373220",  # LG에너지솔루션
    "096770",  # SK이노베이션
    "003670",  # 포스코퓨처엠

    # 4. 재생에너지
    "112610",  # 씨에스윈드
    "009830",  # 한화솔루션
    "322000",  # HD현대에너지솔루션
    "100090",  # SK오션플랜트

    # 5. 원자력 에너지
    "034020",  # 두산에너빌리티
    "052690",  # 한국전력기술
    "298040",  # 효성중공업
    "015760",  # 한국전력
]

# (로그용) 종목코드 -> 종목명
TICKER_TO_NAME = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "000990": "DB하이텍",
    "042700": "한미반도체",

    "005380": "현대차",
    "000270": "기아",
    "012330": "현대모비스",
    "204320": "HL만도",

    "006400": "삼성SDI",
    "373220": "LG에너지솔루션",
    "096770": "SK이노베이션",
    "003670": "포스코퓨처엠",

    "112610": "씨에스윈드",
    "009830": "한화솔루션",
    "322000": "HD현대에너지솔루션",
    "100090": "SK오션플랜트",

    "034020": "두산에너빌리티",
    "052690": "한국전력기술",
    "298040": "효성중공업",
    "015760": "한국전력",
}

# 루프 설정
LOOP_INTERVAL_SEC = 60      # 1분마다
MAX_LOOPS = None            # 테스트용으로 숫자 넣으면 그 횟수만 실행

# ================================
# DB 설정
# ================================
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# 이 이름으로 테이블이 생성됨
PRICE_TABLE_NAME = "Stocks"     # 주가 스냅샷 테이블
COMPANY_TABLE_NAME = "Companies"  # 이미 만들어둔 종목 마스터
