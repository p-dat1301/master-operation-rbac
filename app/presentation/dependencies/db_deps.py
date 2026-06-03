from __future__ import annotations

from typing import AsyncGenerator

from app.infrastructure.database.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session
