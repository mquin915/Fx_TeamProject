import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")  # Atlas URI
DB_NAME = "fxdb"
COLLECTION_NAME = "rates"  # 실제 저장한 collection 이름으로 수정하세요

def check_missing():
    # MongoDB 연결
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # MongoDB → Pandas DataFrame 변환
    df = pd.DataFrame(list(collection.find({}, {"_id": 0})))  # _id 제외

    # 데이터 크기 확인
    print("총 데이터 수:", len(df))

    # 컬럼별 결측치 개수 확인
    print("\n[컬럼별 결측치 개수]")
    print(df.isnull().sum())

    # 결측치 비율
    print("\n[컬럼별 결측치 비율(%)]")
    print(df.isnull().mean() * 100)

    # 필요하다면 CSV 저장
    df.to_csv("exchange_rates.csv", index=False, encoding="utf-8-sig")
    print("\nCSV 파일로 저장 완료: exchange_rates.csv")

if __name__ == "__main__":
    check_missing()
