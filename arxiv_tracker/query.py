from __future__ import annotations
from typing import List, Optional

def _build_category_query(categories: List[str]) -> Optional[str]:
    if not categories:
        return None
    parts = [f"cat:{c.strip()}" for c in categories if c.strip()]
    return " OR ".join(parts) if parts else None

def _quote(s: str) -> str:
    s = s.strip()
    return f'"{s}"' if (" " in s or "-" in s) else s

def _build_keyword_query(keywords: List[str]) -> Optional[str]:
    if not keywords:
        return None
    parts = [f'all:{_quote(k)}' for k in keywords if k.strip()]
    return " OR ".join(parts) if parts else None

def build_search_query(categories: List[str], keywords: List[str], logic: str="AND") -> str:
    cat_q = _build_category_query(categories)
    kw_q  = _build_keyword_query(keywords)
    if cat_q and kw_q:
        op = "AND" if (logic or "AND").upper() == "AND" else "OR"
        return f"({cat_q}) {op} ({kw_q})"
    return cat_q or kw_q or "all:*"
