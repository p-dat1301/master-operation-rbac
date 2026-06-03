from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from typing import Callable


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        # Simple audit logger: log POST/PUT/DELETE with user if present
        if request.method in ("POST", "PUT", "DELETE"):
            user = getattr(request.state, "user", None)
            user_id = user.id if user else None
            print(f"[audit] user={user_id} method={request.method} path={request.url.path} status={response.status_code}")
        return response
