import requests
import time
import threading
from server import vercel
from server import decorators as dec

APPID = "your_appid"
SECRET = "your_secret"


def get_unionid_from_code(js_code: str) -> str | None:
    """Exchange a Weixin js_code for unionid (or openid as fallback).
    Returns unionid string on success, None on failure.
    This helper can be used by other backend handlers.
    """
    if not js_code:
        return None
    # Check in-memory cache first to avoid repeatedly calling jscode2session
    # for the same js_code (which is single-use). Cache stores (identity, expire_ts).
    # thread-safe read from cache
    cached = None
    try:
        with _CODE_CACHE_LOCK:
            cached = _CODE_CACHE.get(js_code)
    except Exception:
        cached = None
    if cached:
        identity, expire_ts = cached
        if time.time() < expire_ts:
            # still valid
            return identity
        else:
            # expired, remove
            try:
                with _CODE_CACHE_LOCK:
                    if js_code in _CODE_CACHE:
                        del _CODE_CACHE[js_code]
            except Exception:
                pass
    payload = {
        "appid": APPID,
        "secret": SECRET,
        "js_code": js_code,
        "grant_type": "authorization_code"
    }
    try:
        res = requests.get("https://api.weixin.qq.com/sns/jscode2session", params=payload, timeout=5)
        res.raise_for_status()
        res_json = res.json()
        # 如果接口返回错误码（例如 code been used），视为失败并返回 None
        if isinstance(res_json, dict) and res_json.get("errcode"):
            # 打印错误信息以便排查（不会抛异常）
            print("jscode2session error:", res_json.get("errcode"), res_json.get("errmsg"))
            return None
        # prefer unionid, fallback to openid
        identity = res_json.get("unionid") or res_json.get("openid")
        print("unionid:", res_json.get("unionid"))
        print("res_json:", res_json)
        if identity:
            # store in cache for a short period to avoid reusing js_code to re-request
            try:
                with _CODE_CACHE_LOCK:
                    _CODE_CACHE[js_code] = (identity, time.time() + _CODE_CACHE_TTL)
            except Exception:
                pass
        return identity
    except Exception:
        return None


# Simple in-memory cache for js_code -> identity (unionid/openid)
# TTL chosen as 5 minutes by default; this cache exists only for the lifetime of the process.
_CODE_CACHE: dict[str, tuple[str, float]] = {}
_CODE_CACHE_TTL = 300
_CODE_CACHE_LOCK = threading.Lock()


def _prune_code_cache():
    """Remove expired entries from the code cache."""
    now = time.time()
    try:
        with _CODE_CACHE_LOCK:
            keys = list(_CODE_CACHE.keys())
            for k in keys:
                try:
                    _, exp = _CODE_CACHE.get(k, (None, 0))
                    if exp and exp < now:
                        del _CODE_CACHE[k]
                except Exception:
                    pass
    except Exception:
        pass

@dec.hot_reload
@vercel.register
def auth(response, data):
    assert isinstance(data, dict), "Input data must be a dictionary."
    assert "code" in data, "Input data must contain 'js_code' field."

    js_code = data["code"]
    grant_type = "authorization_code"

    payload = {
        "appid": APPID,
        "secret": SECRET,
        "js_code": js_code,
        "grant_type": grant_type
    }
    try:
        res = requests.get("https://api.weixin.qq.com/sns/jscode2session", params=payload)
        res.raise_for_status()
        res_json = res.json()
        response.send_code(200)
        response.send_json({
            "code": res_json.get("errcode", 0),
            "msg": res_json.get("errmsg", "Success"),
            "data": {
                "openid": res_json.get("openid", ""),
                "unionid": res_json.get("unionid", "")
            }
        })
    except requests.RequestException as e:
        response.send_code(200)
        response.send_json({
            "code": 500,
            "msg": f"Request failed: {str(e)}",
            "data": {
                "openid": "",
                "unionid": ""
            }
        })