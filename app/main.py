from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.infrastructure.database.session import AsyncSessionLocal

app = FastAPI(title="Master Operation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text("SELECT 1"))
            return {"status": "ok", "db": "connected"}
        except Exception:
            return {"status": "error", "db": "disconnected"}