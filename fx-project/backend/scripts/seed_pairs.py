from app.db import pairs_col

pairs = [
    {"_id":"USD_KRW","base":"USD","target":"KRW","unit":1,"active":True},
    {"_id":"EUR_KRW","base":"EUR","target":"KRW","unit":1,"active":True},
    {"_id":"JPY100_KRW","base":"JPY100","target":"KRW","unit":100,"active":True},
    {"_id":"GBP_KRW","base":"GBP","target":"KRW","unit":1,"active":True},
    {"_id":"CNY_KRW","base":"CNY","target":"KRW","unit":1,"active":True},
    {"_id":"HKD_KRW","base":"HKD","target":"KRW","unit":1,"active":True},
    {"_id":"ISK_KRW","base":"ISK","target":"KRW","unit":1,"active":True},
]

for p in pairs:
    pairs_col.update_one({"_id": p["_id"]}, {"$set": p}, upsert=True)

print("Seeded pairs:", len(pairs))
