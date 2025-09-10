from datetime import datetime, timedelta
import math
from typing import List, Dict

CURRENCIES = ["USD","EUR","CNY","JPY100","ISK","RUB","KRW"] #"GBP","HKD",Icelandic krona

def list_pairs() -> Dict[str, list]:
    # 간단한 예시 페어(표시용). 실제로는 DB에서 관리.
    example_pairs = [
        {"_id": "USD_KRW", "base": "USD", "target": "KRW", "unit": 1, "active": True},
        {"_id": "EUR_KRW", "base": "EUR", "target": "KRW", "unit": 1, "active": True},
        {"_id": "JPY100_KRW", "base": "JPY100", "target": "KRW", "unit": 100, "active": True},
        {"_id": "USD_EUR", "base": "USD", "target": "EUR", "unit": 1, "active": True},
    ]
    return {"currencies": CURRENCIES, "pairs": example_pairs}

def _pair_seed(pair: str) -> int:
    return sum(ord(c) for c in pair) % 37

def _base_value(pair: str) -> float:
    # 과장되지 않은 기본값
    if pair.endswith("_KRW"):
        return 1200.0
    return 1.0

def mock_history(pair: str, start: str, end: str) -> List[Dict[str, float]]:
    s = datetime.fromisoformat(start)
    e = datetime.fromisoformat(end)
    if s > e:
        return []
    days = (e - s).days + 1
    seed = _pair_seed(pair)
    base = _base_value(pair)
    data = []
    for i in range(days):
        day = s + timedelta(days=i)
        # 부드러운 곡선 + 약한 트렌드
        val = base + 40.0*math.sin(2*math.pi*(i+seed)/30.0) + 0.1*i
        if "JPY100" in pair and pair.endswith("_KRW"):
            val *= 0.1  # 과도한 수치 방지용 스케일
        data.append({"date": day.strftime("%Y-%m-%d"), "rate": round(val, 4)})
    return data

def mock_predict(pair: str, horizon: int) -> List[Dict[str, float]]:
    # 오늘 다음날부터 horizon일
    today = datetime.utcnow().date()
    seed = _pair_seed(pair)
    base = _base_value(pair)
    res = []
    for i in range(1, horizon+1):
        day = today + timedelta(days=i)
        idx = i + 5  # 살짝 시프트
        val = base + 40.0*math.sin(2*math.pi*(idx+seed)/30.0) + 0.12*idx
        if "JPY100" in pair and pair.endswith("_KRW"):
            val *= 0.1
        res.append({"date": day.strftime("%Y-%m-%d"), "value": round(val, 4)})
    return res
