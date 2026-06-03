from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Any

from jose import jwt

from app.application.ports.token import ITokenService
from app.core.config import settings


class JWTService(ITokenService):
    """Concrete JWT service using python-jose.

    Simple implementation for access token creation/decoding using
    HS256 and settings.SECRET_KEY.
    """

    def create_access_token(self, subject: str, claims: Dict[str, Any] | None = None) -> str:
        from datetime import timezone
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload: Dict[str, Any] = {"sub": subject, "iat": int(now.timestamp()), "exp": int(expire.timestamp())}
        if claims:
            payload.update(claims)
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        return token

    def decode_access_token(self, token: str) -> Dict[str, Any]:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"]) 
