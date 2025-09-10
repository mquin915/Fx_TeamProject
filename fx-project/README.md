# FX Project (Frontend + Backend) — Quick Start

이 저장소는 **React (Vite) 프론트엔드 + FastAPI 백엔드**의 최소 동작 예제를 포함합니다.
기본값은 **MOCK=1**(가짜 데이터 생성)으로 설정되어 있어 **MongoDB 없이**도 바로 실행/확인할 수 있습니다.
실전 연결은 `backend/.env` 에서 MOCK=0 으로 바꾸고 MONGO_URI 를 설정하세요.

## 폴더 구조
```
fx-project/
├── backend/        # FastAPI
└── frontend/       # Vite React
```

---

## 1) 백엔드 실행 (FastAPI)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# (선택) 환경설정 확인 — 기본은 MOCK=1 이므로 DB 없이 동작합니다.
# echo 'MOCK=1' > .env

uvicorn app.main:app --reload --port 8000
# http://localhost:8000/docs
```

### 엔드포인트 확인
- `/api/pairs` : 통화 목록 + 예시 페어
- `/api/history?pair=USD_KRW&start=2024-01-01&end=2024-12-31`
- `/api/predict?pair=USD_KRW&horizon=7`

> MOCK 모드에서는 날짜 범위에 맞춰 **부드러운 곡선형 데모 시계열**을 생성합니다.

---

## 2) 프론트엔드 실행 (Vite React)
```bash
cd ../frontend
npm i
npm run dev
# http://localhost:5173
```

- 상단에서 **Base/Target 통화**와 **기간(최대 10년)** 을 선택 후 **[역사 불러오기]**
- **[예측 오버레이]** 버튼으로 점선 예측 시리즈 표시
- Vite 프록시 설정으로 `/api/...` 호출은 자동으로 `http://localhost:8000`으로 전달됩니다.

---

## 3) 결과 확인 체크리스트
- [ ] 프론트 페이지가 열리고 드롭다운/기간 입력 UI가 보인다.
- [ ] USD / KRW 선택 후 1년 범위로 **역사 불러오기** → 차트에 실선 표시.
- [ ] **예측 오버레이** 클릭 → 같은 차트에 점선 표시.
- [ ] 브라우저 DevTools Network 탭에서 `/api/history`, `/api/predict` 응답 200 확인.
- [ ] 백엔드 콘솔에 요청 로그가 출력됨.

---

## 4) 실전 DB 연결 (선택)
1) `backend/.env` 예시
```
MOCK=0
MONGO_URI=mongodb://localhost:27017
DB_NAME=fx
ALLOWED_ORIGINS=http://localhost:5173
```
2) `python scripts/seed_pairs.py` 로 페어 시드
3) `uvicorn app.main:app --reload --port 8000` 재기동

> 현재 예제 라우터는 MOCK 모드 구현이 완전하며, DB 모드는 스켈레톤입니다.
> 실 DB 사용 시 `/api/history`, `/api/predict`에서 `TODO` 부분을 채워 넣으세요.

---

## 5) API 수동 테스트 (VSCode REST Client 또는 curl)
- `ops/dev.http`에 샘플 요청이 준비되어 있습니다.
- 또는 터미널에서:
```bash
curl 'http://localhost:8000/api/pairs'
curl 'http://localhost:8000/api/history?pair=USD_KRW&start=2024-07-01&end=2024-08-31'
curl 'http://localhost:8000/api/predict?pair=USD_KRW&horizon=7'
```

행운을 빕니다! 🚀
