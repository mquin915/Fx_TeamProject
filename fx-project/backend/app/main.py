from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import ALLOWED_ORIGINS
from .routers import pairs, history, predict

app = FastAPI(title="FX API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pairs.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(predict.router, prefix="/api")

@app.get("/health")
def health():
    return {"ok": True}
