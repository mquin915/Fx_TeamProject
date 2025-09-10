# app/services/frankfurter_ingest.py
import requests
from datetime import datetime
from pymongo import ReplaceOne
from ..db import rates_col

BASE_URL = "https://api.frankfurter.app"

def _dates_ok(s: str, e: str):
    datetime.fromisoformat(s); datetime.fromisoformat(e)

def _real(code: str) -> str:
    return "JPY" if code == "JPY100" else code

def _factor(code: str) -> int:
    return 100 if code == "JPY100" else 1

def _fetch_range(base: str, target: str, start: str, end: str):
    url = f"{BASE_URL}/{start}..{end}?from={base}&to={target}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json().get("rates", {})

def ingest_pair(pair: str, start: str, end: str):
    """
    - API는 JPY100을 모름 → JPY로 질의 후 저장 시 스케일 보정
    - 보정: scale = factor(base) / factor(target)
    """
    _dates_ok(start, end)

    base, target = pair.split("_", 1)
    if base == target:
        return 0

    q_base = _real(base)
    q_target = _real(target)
    rates = _fetch_range(q_base, q_target, start, end)
    if not rates:
        return 0

    scale = _factor(base) / _factor(target)

    ops = []
    for d, obj in rates.items():
        val = obj.get(q_target)
        if val is None:
            continue
        adj = float(val) * float(scale)
        dt = datetime.fromisoformat(d)
        ops.append(
            ReplaceOne(
                {"pair": pair, "date": dt},
                {"pair": pair, "date": dt, "rate": adj},
                upsert=True
            )
        )

    if ops:
        res = rates_col.bulk_write(ops, ordered=False)
        return res.upserted_count + res.modified_count
    return 0
