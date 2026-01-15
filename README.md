# crawling-stocks

>국내 주식 데이터를 수집하여 데이터베이스에 저장하는 크롤링/수집 레포지토리입니다.  
>KIS(Open API)를 활용해 주가 데이터를 주기적으로 수집하고,  
>후속 분석·백엔드 서비스에서 사용할 수 있도록 정형화된 형태로 저장합니다.



## Repository Purpose

이 레포지토리는 다음 목적을 가집니다.

- 국내 주식 **실시간/주기적 가격 데이터 수집**
- 외부 API(KIS Open API) 연동 및 인증 관리
- 수집한 주가 데이터를 **DB에 안정적으로 저장**
- 분석·알림·백엔드 서비스의 **데이터 소스 역할**


## ⚙️ Key Components

### `kis_client.py`
- KIS Open API 인증 토큰 발급 및 갱신
- 주가 조회를 위한 공통 API 클라이언트

### `price_collector.py`
- 설정된 종목에 대해 주가 데이터 수집
- API 호출 결과를 정제하여 DB 저장 로직에 전달

### `stock_config.py`
- 수집 대상 종목 코드 관리
- 환경별 설정 값 분리

### `stock_db.py`
- 데이터베이스 연결 관리
- 주가 데이터 INSERT / UPDATE 처리

## 📊 Collected Stock Data Fields

본 레포지토리는 KIS Open API를 통해 다음과 같은 주가 정보를 수집합니다.

| Field Name           | Description |
|---------------------|-------------|
| `date`              | 주가 기준 일자 (YYYY-MM-DD) |
| `stck_prpr`         | 현재가 (Current Price) |
| `stck_oprc`         | 시가 (Opening Price) |
| `stck_hgpr`         | 고가 (Highest Price) |
| `stck_lwpr`         | 저가 (Lowest Price) |
| `acml_vol`          | 누적 거래량 (Accumulated Volume) |
| `stck_prdy_clpr`    | 전일 종가 (Previous Day Closing Price) |

해당 데이터는 종목별 가격 흐름 분석, 거래량 변화 감지,
그리고 후속 감정 분석 및 알림 시스템의 입력 데이터로 활용됩니다.

## 🔄 Data Flow

1. KIS API 인증 토큰 발급
2. 종목 코드 기반 주가 데이터 요청
3. 응답 데이터 정제
4. DB 저장
5. 후속 분석/백엔드 서비스에서 활용

## Data Structure
```
📦crawling-stocks
 ┣ 📜.gitignore
 ┣ 📜Dockerfile
 ┣ 📜kis_client.py
 ┣ 📜price_collector.py
 ┣ 📜README.md
 ┣ 📜requirements.txt
 ┣ 📜stock_config.py
 ┗ 📜stock_db.py
```
