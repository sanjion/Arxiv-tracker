# -*- coding: utf-8 -*-
import os, time, random, requests
from tenacity import (
    retry, stop_after_attempt, wait_exponential, wait_random,
    retry_if_exception, retry_if_exception_type, retry_any
)

ARXIV_HTTP  = os.getenv("ARXIV_API_BASE_HTTP",  "http://export.arxiv.org/api/query")
ARXIV_HTTPS = os.getenv("ARXIV_API_BASE_HTTPS", "https://export.arxiv.org/api/query")

HEADERS = {
    "User-Agent": os.getenv("ARXIV_UA", "arxiv-tracker/0.3 (+mailto:you@example.com)")
}

def _retryable_http_error(e: Exception) -> bool:
    if not isinstance(e, requests.exceptions.HTTPError):
        return False
    code = getattr(e.response, "status_code", None)
    # 限流/临时故障：重试
    return code in (429, 500, 502, 503, 504)

_retry_policy = retry_any(
    retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
    retry_if_exception(_retryable_http_error),
)

@retry(
    reraise=True,
    stop=stop_after_attempt(int(os.getenv("ARXIV_MAX_ATTEMPTS", "6"))),
    wait=wait_exponential(multiplier=1, min=2, max=45) + wait_random(0, 1.5),
    retry=_retry_policy,
)
def _do_get(url, params, timeout=30):
    resp = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
    # 触发 tenacity 的重试
    if resp.status_code >= 500 or resp.status_code in (429,):
        resp.raise_for_status()
    resp.raise_for_status()
    return resp

def fetch_arxiv_feed(search_query: str, start: int=0, max_results: int=10,
                     sort_by: str="submittedDate", sort_order: str="descending") -> str:
    params = {
        "search_query": search_query or "all:*",
        "start": start,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": sort_order
    }

    # 多基址轮询 + 间隔暂停（对服务友好）
    bases = [
        os.getenv("ARXIV_API_BASE", ARXIV_HTTPS),  # 允许一键覆盖
        ARXIV_HTTP,
        ARXIV_HTTPS,  # 再尝一次
    ]
    last_err = None
    for i, base in enumerate(bases):
        try:
            r = _do_get(base, params)
            time.sleep(float(os.getenv("ARXIV_PAUSE", "1.2")))  # 轻限速
            return r.text
        except Exception as e:
            last_err = e
            # 轮换前的额外退避
            time.sleep(1.0 + i * 1.5 + random.random())
            continue
    # 全部失败
    raise last_err
