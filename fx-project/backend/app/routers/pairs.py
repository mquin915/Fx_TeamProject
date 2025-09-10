from fastapi import APIRouter
from ..config import MOCK
from ..db import pairs_col
from ..services import data as mock

router = APIRouter()

@router.get("/pairs")
def get_pairs():
    if MOCK:
        return mock.list_pairs()
    # DB 모드: 활성 페어와 통화 목록
    currencies = ["USD","EUR","GBP","CNY","JPY100","HKD","ISK","KRW"]
    pairs = list(pairs_col.find({"active": True}, {"_id":1, "base":1, "target":1, "unit":1, "active":1}))
    return {"currencies": currencies, "pairs": pairs}
