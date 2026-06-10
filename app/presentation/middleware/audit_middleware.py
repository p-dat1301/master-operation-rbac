from __future__ import annotations

import re
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from typing import Callable

from app.domain.entities.audit_log import AuditLog
from app.infrastructure.database.session import AsyncSessionLocal

logger = logging.getLogger("audit")

# Pattern to extract resource type and resource_id from URL path
# e.g., /api/v1/users/5 → resource="users", resource_id=5
_PATH_PATTERN = re.compile(r"/api/v1/(\w+)(?:/(\d+))?")


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)

        # Only audit state-changing requests with successful responses
        if request.method in ("POST", "PUT", "DELETE") and 200 <= response.status_code < 300:
            user = getattr(request.state, "user", None)
            user_id = user.id if user else None

            # Parse resource from path
            match = _PATH_PATTERN.match(request.url.path)
            resource = match.group(1) if match else request.url.path
            resource_id_str = match.group(2) if match else None
            resource_id = int(resource_id_str) if resource_id_str else 0

            # Map HTTP method to action
            action_map = {"POST": "create", "PUT": "update", "DELETE": "delete"}
            action = action_map.get(request.method, request.method.lower())

            # Log to console
            logger.info(
                "user=%s method=%s path=%s status=%s",
                user_id, request.method, request.url.path, response.status_code,
            )

            # Persist to DB using a separate session (middleware doesn't share request session)
            try:
                async with AsyncSessionLocal() as session:
                    from app.infrastructure.database.repositories.sqlalchemy_audit_log_repo import SQLAlchemyAuditLogRepository

                    audit_repo = SQLAlchemyAuditLogRepository(session)
                    audit_entry = AuditLog(
                        id=0,
                        user_id=user_id,
                        action=action,
                        resource=resource,
                        resource_id=resource_id,
                        details={
                            "method": request.method,
                            "path": str(request.url.path),
                            "status_code": response.status_code,
                        },
                    )
                    await audit_repo.create(audit_entry)
                    await session.commit()
            except Exception:
                logger.exception("Failed to persist audit log")

        return response
