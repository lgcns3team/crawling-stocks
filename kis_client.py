# kis_client.py

import json
import os
from pathlib import Path
from datetime import datetime, timedelta

import requests
from stock_config import APP_KEY, APP_SECRET, BASE_URL, TR_ID_PRICE

TOKEN_FILE_PATH = Path(__file__).parent / "kis_access_token.json"


# ==============================
# 토큰 캐시 로드/저장
# ==============================
def _load_cached_token():
    if not TOKEN_FILE_PATH.exists():
        return None

    try:
        with open(TOKEN_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        token = data.get("token")
        issued_at_str = data.get("issued_at")
        if not token or not issued_at_str:
            return None
        issued_at = datetime.fromisoformat(issued_at_str)
        return {"token": token, "issued_at": issued_at}
    except Exception as e:
        print(f"[WARN] 토큰 캐시 파일 읽기 실패: {e}")
        return None


def _save_cached_token(token: str):
    data = {
        "token": token,
        "issued_at": datetime.now().isoformat(),
    }
    try:
        with open(TOKEN_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] 토큰 캐시 파일 쓰기 실패: {e}")


def _request_new_access_token() -> str:
    url = f"{BASE_URL}/oauth2/tokenP"
    headers = {"content-type": "application/json; charset=utf-8"}
    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
    }

    print("=== [DEBUG] 새 access_token 발급 요청 ===")
    print(f"[DEBUG] URL: {url}")
    print(f"[DEBUG] APP_KEY: {APP_KEY}")
    print(f"[DEBUG] APP_SECRET 길이: {len(APP_SECRET) if APP_SECRET else 0}")

    res = requests.post(url, headers=headers, data=json.dumps(body))

    print(f"[DEBUG] status_code: {res.status_code}")
    print(f"[DEBUG] response text: {res.text}")

    if res.status_code != 200:
        raise RuntimeError(
            f"토큰 발급 실패: status={res.status_code}, body={res.text}"
        )

    data = res.json()
    token = (
        data.get("access_token")
        or data.get("accessToken")
        or data.get("ACCESS_TOKEN")
    )
    if not token:
        raise RuntimeError(f"토큰 키(access_token)를 응답에서 찾지 못했습니다: {data}")

    _save_cached_token(token)
    print("ACCESS_TOKEN 발급 & 캐시 저장 완료")
    return token


def get_access_token(force_new: bool = False) -> str:
    """
    force_new=False:
      - 캐시가 있으면 무조건 재사용
      - 없으면 새 발급
    force_new=True:
      - 1분 이내에 발급한 기록이 있으면 기존 토큰 재사용 (EGW00133 방지)
      - 그 외에는 새 발급
    """
    cached = _load_cached_token()

    if not force_new:
        # 캐시가 있으면 그냥 사용
        if cached is not None:
            return cached["token"]
        # 없으면 새 발급
        return _request_new_access_token()

    # force_new=True 인 경우
    if cached is not None:
        elapsed = (datetime.now() - cached["issued_at"]).total_seconds()
        if elapsed < 60:
            # 1분 내 재발급 시도는 EGW00133 나니까 기존 토큰 재사용
            print("[INFO] 1분 내 재발급 시도 → 기존 토큰 재사용")
            return cached["token"]

    # 1분 지났거나 캐시 없음 → 새 발급
    return _request_new_access_token()


def make_headers(tr_id: str, access_token: str) -> dict:
    return {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": tr_id,
        "tr_cont": "N",
    }


def fetch_price_snapshot(ticker: str, access_token: str) -> dict:
    """
    주어진 access_token으로만 조회 (여기서 토큰 발급은 안 함).
    토큰 문제나 기타 오류는 RuntimeError로 던진다.
    """
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price-2"
    headers = make_headers(TR_ID_PRICE, access_token)
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
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

    base_date_str = o.get("stck_bsop_date") or datetime.today().strftime("%Y%m%d")
    time_str = o.get("stck_cntg_hour") or datetime.now().strftime("%H%M%S")

    base_date = datetime.strptime(base_date_str, "%Y%m%d").date()
    base_time = datetime.strptime(time_str, "%H%M%S").time()
    base_datetime = datetime.combine(base_date, base_time)

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
