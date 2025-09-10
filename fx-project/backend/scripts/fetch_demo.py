from app.services.frankfurter_ingest import ingest_pair

# 예: 3년치 USD_KRW & JPY100_KRW
n1 = ingest_pair("USD_KRW", "2022-01-01", "2025-09-01")
n2 = ingest_pair("JPY100_KRW", "2022-01-01", "2025-09-01")
print("Upserted/Modified:", n1, n2)
