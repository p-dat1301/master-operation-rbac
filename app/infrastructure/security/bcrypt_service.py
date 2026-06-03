from __future__ import annotations

from app.application.ports.password import IPasswordService
from passlib.context import CryptContext


_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptService(IPasswordService):
    """Simple bcrypt wrapper implementing `IPasswordService` port."""

    def hash(self, plain_password: str) -> str:
        return _ctx.hash(plain_password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return _ctx.verify(plain_password, hashed_password)
