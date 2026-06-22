from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.infrastructure.database.session import AsyncSessionLocal
from app.domain import exceptions as domain_exceptions
from app.presentation.api.v1 import attendance as attendance_router
from app.presentation.api.v1 import audit_logs as audit_logs_router
from app.presentation.api.v1 import auth as auth_router
from app.presentation.api.v1 import departments as departments_router
from app.presentation.api.v1 import i18n_sync as i18n_sync_router
from app.presentation.api.v1 import leave_balances as leave_balances_router
from app.presentation.api.v1 import leaves as leaves_router
from app.presentation.api.v1 import menu_sync as menu_sync_router
from app.presentation.api.v1 import notifications as notifications_router
from app.presentation.api.v1 import permissions as permissions_router
from app.presentation.api.v1 import roles as roles_router
from app.presentation.api.v1 import agentic as agentic_router
from app.presentation.api.v1 import tasks as tasks_router
from app.presentation.api.v1 import users as users_router
from app.presentation.middleware.audit_middleware import AuditMiddleware


app = FastAPI(title="Master Operation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(agentic_router.router)
app.include_router(tasks_router.router)
app.include_router(leaves_router.router)
app.include_router(attendance_router.router)
app.include_router(departments_router.router)
app.include_router(leave_balances_router.router)
app.include_router(notifications_router.router)
app.include_router(audit_logs_router.router)
app.include_router(roles_router.router)
app.include_router(permissions_router.router)
app.include_router(menu_sync_router.router)
app.include_router(i18n_sync_router.router)

# Add audit middleware
app.add_middleware(AuditMiddleware)


@app.exception_handler(domain_exceptions.PermissionDenied)
async def permission_denied_handler(request: Request, exc: domain_exceptions.PermissionDenied):
    return JSONResponse(status_code=403, content={"detail": "Permission denied"})


@app.exception_handler(domain_exceptions.ResourceNotFound)
async def resource_not_found_handler(request: Request, exc: domain_exceptions.ResourceNotFound):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(domain_exceptions.BusinessRuleViolation)
async def business_rule_violation_handler(request: Request, exc: domain_exceptions.BusinessRuleViolation):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(domain_exceptions.ScopeViolation)
async def scope_violation_handler(request: Request, exc: domain_exceptions.ScopeViolation):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.get("/health")
async def health() -> dict[str, str]:
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text("SELECT 1"))
            return {"status": "ok", "db": "connected"}
        except Exception:
            return {"status": "error", "db": "disconnected"}
