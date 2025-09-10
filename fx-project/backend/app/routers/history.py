from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from ..config import MOCK
from ..db import rates_col
from ..services import data as mock
from pymongo import ASCENDING

router = APIRouter()

@router.get("/history")
def history(pair: str = Query(...), start: str = Query(...), end: str = Query(...)):
    # 간단 유효성
    try:
        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
    except Exception:
        raise HTTPException(400, "start/end는 YYYY-MM-DD 형식이어야 합니다.")
    if s > e:
        raise HTTPException(400, "start는 end보다 이후일 수 없습니다.")
    # 10년 제한
    if (e - s).days > 366*10:
        raise HTTPException(400, "최대 10년까지만 조회할 수 있습니다.")
    if MOCK:
        return {"pair": pair, "data": mock.mock_history(pair, start, end)}
    
    # DB 모드: Mongo에서 조회
    cur = rates_col.find(
        {"pair": pair, "date": {"$gte": s, "$lte": e}},
        {"_id":0, "date":1, "rate":1}
    ).sort("date", ASCENDING)

    data = [{"date": d["date"].strftime("%Y-%m-%d"), "rate": float(d["rate"])} for d in cur]
    return {"pair": pair, "data": data}