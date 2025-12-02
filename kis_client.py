import json
import requests
from datetime import datetime
from stock_config import APP_KEY, APP_SECRET, BASE_URL, TR_ID_PRICE


def get_access_token() -> str:
    url = f"{BASE_URL}/oauth2/tokenP"
    headers = {"content-type": "application/json; charset=utf-8"}
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
    }

    # 디버깅용 출력
    print("=== [DEBUG] get_access_token 시작 ===")
    print(f"[DEBUG] URL: {url}")
    print(f"[DEBUG] APP_KEY: {APP_KEY}")
    print(f"[DEBUG] APP_SECRET 길이: {len(APP_SECRET) if APP_SECRET else 0}")

    res = requests.post(url, headers=headers, data=json.dumps(body))

    print(f"[DEBUG] status_code: {res.status_code}")
    try:
        print(f"[DEBUG] response text: {res.text}")
    except Exception:
        print("[DEBUG] response text 출력 중 에러")

    # 에러 체크
    if res.status_code != 200:
        raise RuntimeError(
            f"토큰 발급 실패: status={res.status_code}, body={res.text}"
        )

    data = res.json()
    access_token = data.get("access_token") or data.get("accessToken") or data.get("ACCESS_TOKEN")

    if not access_token:
        raise RuntimeError(f"토큰 키(access_token)를 응답에서 찾지 못했습니다: {data}")

    print("ACCESS_TOKEN 발급 완료")
    return access_token



def make_headers(tr_id: str, access_token: str) -> dict:
    return {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id,
        "tr_cont": "N",  # 연속조회 안 씀
    }


def fetch_price_snapshot(ticker: str, access_token: str) -> dict:
    """
    현재가 상세조회(ver2)를 호출해서
    새 DB 스키마에 맞는 raw snapshot(dict)을 반환.
    - 숫자들은 모두 String 그대로 보존.
    """
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price-2"
    headers = make_headers(TR_ID_PRICE, access_token)
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",  # J: 주식
        "FID_INPUT_ISCD": ticker,
    }

    res = requests.get(url, headers=headers, params=params, timeout=10)
    if res.status_code != 200:
        raise RuntimeError(
            f"[PRICE-2] status={res.status_code}, body={res.text}"
        )

    data = res.json()
    if "output" not in data:
        raise RuntimeError(
            f"[PRICE-2] output 없음: {json.dumps(data, ensure_ascii=False, indent=2)}"
        )

    o = data["output"]

    # 기준 날짜/시간
    base_date_str = o.get("stck_bsop_date") or datetime.today().strftime("%Y%m%d")
    time_str = o.get("stck_cntg_hour") or datetime.now().strftime("%H%M%S")

    base_date = datetime.strptime(base_date_str, "%Y%m%d").date()
    base_time = datetime.strptime(time_str, "%H%M%S").time()
    base_datetime = datetime.combine(base_date, base_time)

    # 숫자 필드는 그대로 문자열로 사용
    snapshot = {
        "ticker": ticker,
        "date": base_datetime,
        "stck_prpr": o.get("stck_prpr") or "0",
        "stck_oprc": o.get("stck_oprc") or "0",
        "stck_hgpr": o.get("stck_hgpr") or "0",
        "stck_lwpr": o.get("stck_lwpr") or "0",
        "acml_vol": o.get("acml_vol") or "0",
        "stck_prdy_clpr": o.get("stck_prdy_clpr") or "0",
    }

    return snapshot
