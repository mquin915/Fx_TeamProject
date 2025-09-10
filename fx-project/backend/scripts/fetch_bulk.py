# backend/scripts/fetch_bulk.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # backend 경로 추가

from datetime import date, timedelta, datetime
from typing import List
from app.services.frankfurter_ingest import ingest_pair
from app.services.data import CURRENCIES  # ["USD","EUR","GBP","CNY","JPY100","HKD","ISK","KRW"]

# 최근 10년의 같은 달/일을 맞추되, 2/29 같은 케이스는 안전하게 -1일 보정
def ten_years_range(end: date | None = None) -> tuple[str, str]:
    if end is None:
        end = date.today()
    try:
        start = end.replace(year=end.year - 10)
    except ValueError:
        # 2/29 등 존재하지 않는 날짜 보정
        start = (end - timedelta(days=365 * 10))
    return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

# 연도 단위로 쪼개서 여러 번 적재(안전/복구/재시도에 유리)
def year_chunks(start_iso: str, end_iso: str) -> List[tuple[str, str]]:
    s = datetime.fromisoformat(start_iso).date()
    e = datetime.fromisoformat(end_iso).date()
    chunks = []
    cur_start = date(s.year, s.month, s.day)
    while cur_start <= e:
        cur_end = date(cur_start.year, 12, 31)
        if cur_end > e:
            cur_end = e
        chunks.append((cur_start.strftime("%Y-%m-%d"), cur_end.strftime("%Y-%m-%d")))
        # 다음 해 1/1
        cur_start = date(cur_start.year + 1, 1, 1)
    return chunks

# 전체 조합 생성 (순서있는 페어, base != quote)
def build_all_pairs(codes: List[str]) -> List[str]:
    pairs = [f"{b}_{q}" for b in codes for q in codes if b != q]
    # 필요 시 중복 제거(이론상 없음) 및 정렬
    return sorted(set(pairs))

# 전체 조합을 10년 구간으로 적재
def ingest_all_pairs_10y():
    start, end = ten_years_range()
    pairs = build_all_pairs(CURRENCIES)
    total = 0
    print(f"[INFO] Ingest 10y range {start}..{end} for {len(pairs)} pairs")

    for pair in pairs:
        pair_total = 0
        for s, e in year_chunks(start, end):
            try:
                n = ingest_pair(pair, s, e)
                pair_total += n
                print(f"  - {pair} {s}..{e}: upserted/modified {n}")
            except Exception as ex:
                print(f"  ! {pair} {s}..{e} ERROR: {ex}")
        print(f"[DONE] {pair}: total upserted/modified {pair_total}")
        total += pair_total

    print(f"[RESULT] all pairs total upserted/modified: {total}")

if __name__ == "__main__":
    ingest_all_pairs_10y()

