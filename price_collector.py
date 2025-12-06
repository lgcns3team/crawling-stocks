import time
from datetime import datetime

from stock_config import (
    TARGET_TICKERS,
    TICKER_TO_NAME,
)
from stock_db import (
    get_connection,
    ensure_price_table,
    get_or_create_company,
    insert_price_snapshot,
)
from kis_client import get_access_token, fetch_price_snapshot


def run():
    access_token = get_access_token()
    conn = get_connection()
    try:
        for ticker in TARGET_TICKERS:
            kor_name = TICKER_TO_NAME.get(ticker, "")
            try:
                # 1) KIS API에서 현재가 스냅샷 가져오기
                raw = fetch_price_snapshot(ticker, access_token)
                # 2) Companies에 이 종목이 존재하는지 확인
                company_id = get_or_create_company(conn, ticker, kor_name)
                # 3) Stocks 테이블로 넣을 데이터 만들기
                snapshot = {
                    "date": raw["date"],               # datetime 객체
                    "company_id": company_id,          # = ticker 문자열
                    "stck_prpr": raw["stck_prpr"],
                    "stck_oprc": raw["stck_oprc"],
                    "stck_hgpr": raw["stck_hgpr"],
                    "stck_lwpr": raw["stck_lwpr"],
                    "acml_vol": raw["acml_vol"],
                    "stck_prdy_clpr": raw["stck_prdy_clpr"],
                }
                # 4) INSERT / UPDATE
                insert_price_snapshot(conn, snapshot)
                print(
                    f"[{ticker} {kor_name}] "
                    f"{snapshot['date']} "
                    f"현재가={snapshot['stck_prpr']} "
                    f"시가={snapshot['stck_oprc']} "
                    f"고가={snapshot['stck_hgpr']} "
                    f"저가={snapshot['stck_lwpr']} "
                    f"누적거래량={snapshot['acml_vol']} "
                    f"전일종가={snapshot['stck_prdy_clpr']}"
                )
            except Exception as e:
                print(f"[ERROR] ticker={ticker} ({kor_name}) 처리 중 오류: {e}")
            time.sleep(0.4)
        conn.commit()
    finally:
        conn.close()


def main():
    print("1분봉 수집 시작")

    conn = get_connection()
    try:
        # 새 스키마 테이블 생성 (Stocks)
        ensure_price_table(conn)
    finally:
        conn.close()

    run()


if __name__ == "__main__":
    main()
