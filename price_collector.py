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
    # 1) 우선 캐시 기반으로 토큰 확보 (없으면 발급)
    try:
        access_token = get_access_token(force_new=False)
    except Exception as e:
        print(f"[FATAL] access_token 발급 실패, 이번 회차 전체 수집 중단: {e}")
        return

    conn = get_connection()
    try:
        for ticker in TARGET_TICKERS:
            kor_name = TICKER_TO_NAME.get(ticker, "")
            try:
                # 2) 첫 시도: 기존 토큰으로 조회
                try:
                    raw = fetch_price_snapshot(ticker, access_token)
                except Exception as e:
                    msg = str(e)
                    # 토큰 문제로 보이는 경우에만 재발급 로직 태움
                    token_error_signs = [
                        "status=401",
                        "status=403",
                        "접근토큰",
                        "기간이 만료된 token",  
                        "기간이 만료된",        
                    ]
                    if any(s in msg for s in token_error_signs):
                        print(f"[WARN] {ticker} {kor_name} 조회 중 토큰 문제 추정 → 재발급 시도")
                        access_token = get_access_token(force_new=True)
                        raw = fetch_price_snapshot(ticker, access_token)
                    else:
                        raise

                # 여기까지 왔으면 raw는 정상
                company_id = get_or_create_company(conn, ticker, kor_name)
                snapshot = {
                    "date": raw["date"],
                    "company_id": company_id,
                    "stck_prpr": raw["stck_prpr"],
                    "stck_oprc": raw["stck_oprc"],
                    "stck_hgpr": raw["stck_hgpr"],
                    "stck_lwpr": raw["stck_lwpr"],
                    "acml_vol": raw["acml_vol"],
                    "stck_prdy_clpr": raw["stck_prdy_clpr"],
                }

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
                # 한 종목에서 실패해도 다음 종목은 시도
                print(f"[ERROR] ticker={ticker} ({kor_name}) 처리 중 오류: {e}")

            time.sleep(0.4)

        conn.commit()
    finally:
        conn.close()


def main():
    print("1분봉 수집 시작")

    conn = get_connection()
    try:
        ensure_price_table(conn)
        print("테이블 준비 완료: Stocks")
    finally:
        conn.close()

    run()


if __name__ == "__main__":
    main()
