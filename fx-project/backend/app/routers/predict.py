from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta, date as date_cls
from pymongo import DESCENDING
from ..config import MOCK
from ..db import rates_col
from ..services import data as mock

router = APIRouter()

@router.get("/predict")
def predict(pair: str = Query(...), horizon: int = Query(7, ge=1, le=60)):
    if MOCK:
        return {"pair": pair, "horizon": horizon, "yhat": mock.mock_predict(pair, horizon)}
     # DB 모드: 가장 최근값 사용한 naive 예측 (샘플)
    last = rates_col.find({"pair": pair}).sort("date", DESCENDING).limit(1)
    last_doc = next(iter(last), None)
    if not last_doc:
        raise HTTPException(404, f"No history for {pair}")

    last_rate = float(last_doc["rate"])
    today = datetime.utcnow().date()
    yhat = []
    for i in range(1, horizon+1):
        d = today + timedelta(days=i)
        yhat.append({"date": d.strftime("%Y-%m-%d"), "value": last_rate})

    return {"pair": pair, "horizon": horizon, "yhat": yhat}