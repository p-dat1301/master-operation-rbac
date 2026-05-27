# Master Operation — RBAC Demo: Implementation Plan (Clean Architecture)

## Tổng quan

Demo phân quyền đa tầng (RBAC) theo **Clean Architecture**, tách biệt hoàn toàn business logic khỏi infrastructure.

```
Presentation ──► Application ──► Domain ◄── Infrastructure
```

**Đã xác nhận:**
- Giao diện: **Swagger UI** (không frontend)
- Thông báo: **Telegram Bot API thật** + WebSocket
- Schema: **SQL migration files** (không Alembic)
- Bảo mật: Tên công ty, phòng ban, email dùng placeholder

---

## Kiến trúc Thư mục

```
master-operation/
├── app/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── user.py
│   │   │   ├── department.py
│   │   │   ├── task.py
│   │   │   ├── leave.py
│   │   │   ├── leave_balance.py
│   │   │   ├── attendance.py
│   │   │   ├── notification.py
│   │   │   └── audit_log.py
│   │   ├── repositories/          # ABCs
│   │   │   ├── user_repository.py
│   │   │   ├── task_repository.py
│   │   │   ├── leave_repository.py
│   │   │   ├── leave_balance_repository.py
│   │   │   ├── attendance_repository.py
│   │   │   ├── notification_repository.py
│   │   │   └── audit_log_repository.py
│   │   ├── services/
│   │   │   ├── rbac_service.py
│   │   │   └── department_tree.py
│   │   └── exceptions.py
│   │
│   ├── application/
│   │   ├── use_cases/
│   │   │   ├── auth/login_use_case.py, get_me_use_case.py
│   │   │   ├── user/list_users_use_case.py, create_user_use_case.py
│   │   │   ├── task/list_tasks_use_case.py, create_task_use_case.py, assign_task_use_case.py
│   │   │   ├── leave/create_leave_use_case.py, list_leaves_use_case.py, review_leave_use_case.py
│   │   │   └── attendance/checkin_use_case.py, get_heatmap_use_case.py
│   │   ├── dtos/
│   │   │   └── auth_dto.py, user_dto.py, task_dto.py, leave_dto.py, attendance_dto.py
│   │   └── ports/
│   │       └── token_port.py, password_port.py, notification_port.py
│   │
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── models/
│   │   │   │   └── role_model.py, permission_model.py, department_model.py,
│   │   │   │       user_model.py, task_model.py, leave_model.py,
│   │   │   │       leave_balance_model.py, attendance_model.py,
│   │   │   │       notification_model.py, audit_log_model.py
│   │   │   ├── repositories/
│   │   │   │   └── sqlalchemy_user_repo.py, sqlalchemy_task_repo.py,
│   │   │   │       sqlalchemy_leave_repo.py, sqlalchemy_leave_balance_repo.py,
│   │   │   │       sqlalchemy_attendance_repo.py, sqlalchemy_notification_repo.py,
│   │   │   │       sqlalchemy_audit_log_repo.py
│   │   │   ├── session.py
│   │   │   └── seed.py
│   │   ├── security/
│   │   │   ├── jwt_service.py
│   │   │   └── bcrypt_service.py
│   │   └── notifications/
│   │       ├── websocket_manager.py
│   │       └── telegram_notification_service.py
│   │
│   ├── presentation/
│   │   ├── api/v1/
│   │   │   └── auth.py, users.py, tasks.py, leaves.py, attendance.py,
│   │   │       departments.py, notifications.py, audit_logs.py
│   │   ├── schemas/
│   │   ├── dependencies/auth_deps.py, db_deps.py
│   │   └── middleware/audit_middleware.py
│   │
│   ├── container.py
│   └── main.py
│
├── migrations/
│   ├── 010_create_migration_history.sql
│   ├── 001_create_roles.sql
│   ├── 002_create_permissions.sql
│   ├── 003_create_role_permissions.sql
│   ├── 004_create_departments.sql
│   ├── 005_create_users.sql
│   ├── 006_create_tasks.sql
│   ├── 007_create_leave_requests.sql
│   ├── 008_create_attendances.sql
│   ├── 009_create_audit_logs.sql
│   ├── 011_create_leave_balances.sql
│   ├── 012_create_notifications.sql
│   └── run_migrations.sh
├── tests/unit/domain/ và tests/integration/
├── docker-compose.yml, Dockerfile, requirements.txt
├── .env.example, Makefile, README.md
```

---

## Phase 1 — Foundation

**`docker-compose.yml`** — 3 services: `api` (port 8000), `db` PostgreSQL 16, `redis` Redis 7

**`Dockerfile`** — `python:3.12-slim`, CMD `uvicorn app.main:app --reload`

**`requirements.txt`**: fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic[email], pydantic-settings, python-jose[cryptography], passlib[bcrypt], python-multipart, websockets, httpx, pytest, pytest-asyncio

**`.env.example`**:
```
DATABASE_URL=postgresql://postgres:postgres@db:5432/masterop
SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=15
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### SQL Migration Files (12 tables — không dùng Alembic)

Thứ tự chạy: `010` trước tiên (tạo bảng tracking) → `001` → `002` → ... → `009` → `011` → `012`

| File | Table | Điểm đặc biệt |
|------|-------|--------------|
| `010` | `migration_history` | Chạy đầu tiên — tracking các file đã applied |
| `001` | `roles` | name: admin\|bod\|manager\|employee |
| `002` | `permissions` | code UNIQUE |
| `003` | `role_permissions` | PK(role_id, permission_id) |
| `004` | `departments` | self-ref parent_id, level CHECK 1-4, head_id FK |
| `005` | `users` | employee_code UK, manager_id self-ref, contract_type, hire_date, zalo_id, telegram_username |
| `006` | `tasks` | task_code UK, priority urgent\|high\|medium\|low, status có backlog+cancelled |
| `007` | `leave_requests` | leave_type, rejection_reason, CHECK end>=start |
| `008` | `attendances` | UNIQUE(user_id,date), ip_address, total_minutes, notes |
| `009` | `audit_logs` | BIGSERIAL, JSONB details, user_agent, inet ip |
| `011` | `leave_balances` | UNIQUE(user_id, year), remaining_days |
| `012` | `notifications` | channel: websocket\|telegram, is_read |

**Tổng: 12 tables** = 10 bảng nghiệp vụ + `migration_history` + `role_permissions` (join table)

`run_migrations.sh` — chạy theo glob `[0-9][0-9][0-9]_*.sql`, skip nếu đã có trong `migration_history` (idempotent).

---

## Phase 2 — Domain Layer (ERD v2, 8 entities)

### Entities (Pure Python dataclass — không import SQLAlchemy/FastAPI)

```python
# user.py
@dataclass
class User:
    id: int; employee_code: str; email: str; full_name: str
    phone: str; job_title: str
    contract_type: str  # probation|official|service
    role_name: str      # admin|bod|manager|employee
    department_id: int; manager_id: int | None
    zalo_id: str; telegram_username: str
    hire_date: date; is_active: bool

# department.py
@dataclass
class Department:
    id: int; name: str; level: int  # 1-4
    parent_id: int | None; head_id: int | None; code: str

# task.py
@dataclass
class Task:
    id: int; task_code: str; title: str; description: str
    assignee_id: int; assigner_id: int; department_id: int
    status: str    # backlog|todo|in_progress|done|cancelled
    priority: str  # urgent|high|medium|low
    start_date: date; due_date: datetime; estimated_hours: int

# leave.py
@dataclass
class Leave:
    id: int; requester_id: int
    leave_type: str  # annual|sick|maternity|business|unpaid
    start_date: date; end_date: date; reason: str
    status: str  # pending|approved|rejected
    reviewed_by: int | None; rejection_reason: str | None

# leave_balance.py
@dataclass
class LeaveBalance:
    id: int; user_id: int; year: int
    total_days: Decimal; used_days: Decimal
    pending_days: Decimal; remaining_days: Decimal

# attendance.py
@dataclass
class Attendance:
    id: int; user_id: int; date: date
    check_in: datetime; check_out: datetime | None
    total_minutes: int; ip_address: str; notes: str
    status: str  # on_time|late|absent|online|on_leave

# notification.py
@dataclass
class Notification:
    id: int; recipient_id: int
    type: str; channel: str  # websocket|telegram
    message: str; payload: dict; is_read: bool; sent_at: datetime

# audit_log.py
@dataclass
class AuditLog:
    id: int; user_id: int | None
    action: str; resource: str; resource_id: int
    details: dict; ip_address: str; user_agent: str; created_at: datetime
```

### RBAC Service

```python
PERMISSION_MATRIX = {
    "admin":    {"view_personnel","approve_leave","create_task","assign_task",
                 "view_attendance_all","view_attendance_dept","view_attendance_self",
                 "manage_org","view_audit_log"},
    "bod":      {"view_personnel","approve_leave","create_task","assign_task",
                 "view_attendance_all","view_attendance_dept","view_attendance_self"},
    "manager":  {"view_personnel","approve_leave","create_task","assign_task",
                 "view_attendance_dept","view_attendance_self"},
    "employee": {"create_task","view_attendance_self"},
}

class RBACService:
    def has_permission(self, user: User, code: str) -> bool:
        return code in PERMISSION_MATRIX.get(user.role_name, set())
    def get_attendance_scope(self, user: User) -> str:
        if user.role_name in ("admin","bod"): return "all"
        if user.role_name == "manager": return "department"
        return "self"
```

### Repository Interfaces

7 ABCs: `IUserRepository`, `ITaskRepository`, `ILeaveRepository`, `ILeaveBalanceRepository`, `IAttendanceRepository`, `INotificationRepository`, `IAuditLogRepository`

### Domain Exceptions

```python
class PermissionDenied(DomainException): ...
class ScopeViolation(DomainException): ...
class ResourceNotFound(DomainException): ...
class BusinessRuleViolation(DomainException): ...
```

---

## Phase 3 — Application Layer

### Ports

```python
class ITokenService(ABC):
    def create_token(payload, expires_minutes) -> str: ...
    def decode_token(token) -> dict: ...

class IPasswordService(ABC):
    def hash(plain) -> str: ...
    def verify(plain, hashed) -> bool: ...

class INotificationService(ABC):
    async def notify_leave_request(leave_id, manager_id) -> None: ...
    async def notify_task_assigned(task_id, assignee_id) -> None: ...
    async def notify_leave_reviewed(leave_id, requester_id, approved) -> None: ...
```

### Key Use Case: ReviewLeaveUseCase

```python
async def execute(actor: User, leave_id: int, approved: bool) -> LeaveDTO:
    if not rbac.has_permission(actor, "approve_leave"):
        raise PermissionDenied()
    leave = leave_repo.find_by_id(leave_id)
    requester = user_repo.find_by_id(leave.requester_id)
    if actor.role_name == "manager":
        if not tree.is_ancestor_of(actor.department_id,
                                   requester.department_id, all_depts):
            raise ScopeViolation()
    updated = leave_repo.update_status(leave_id, approved, actor.id)
    await notif.notify_leave_reviewed(leave_id, requester.id, approved)
    audit_repo.log(actor.id, "review_leave", "leave", leave_id, {"approved": approved})
    return LeaveDTO.from_entity(updated)
```

---

## Phase 4 — Infrastructure Layer

### Telegram Notification (INotificationService thật)

```python
class TelegramNotificationService(INotificationService):
    def __init__(self, bot_token: str, ws_manager: WebSocketManager):
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.ws = ws_manager

    async def _send(self, chat_id: str, text: str):
        async with httpx.AsyncClient() as c:
            await c.post(f"{self.api_url}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

    async def notify_leave_request(self, leave_id, manager_id):
        await self._send(settings.TELEGRAM_CHAT_ID,
            f"📋 <b>Đơn xin phép mới</b>\nID: #{leave_id}")
        await self.ws.send_to_user(manager_id,
            {"type": "new_leave_request", "leave_id": leave_id})
```

### SQLAlchemy Repositories

Mỗi repo implement tương ứng ABC, có `_to_entity(model) -> DomainEntity`.

---

## Phase 5 — Presentation Layer

### API Endpoints

| Method | Path | Permission | Scope |
|--------|------|-----------|-------|
| POST | `/api/v1/auth/login` | — | JWT |
| GET | `/api/v1/auth/me` | authenticated | — |
| GET | `/api/v1/users/` | `view_personnel` | admin/bod=all; manager=dept |
| POST | `/api/v1/users/` | `manage_org` | admin |
| GET | `/api/v1/tasks/` | authenticated | employee=self; manager=dept; admin=all |
| POST | `/api/v1/tasks/` | `create_task` | employee=self; manager=dept |
| PUT | `/api/v1/tasks/{id}/assign` | `assign_task` | manager scope |
| POST | `/api/v1/leaves/` | authenticated | notify manager |
| GET | `/api/v1/leaves/` | authenticated | employee=self; manager=dept |
| PUT | `/api/v1/leaves/{id}/approve` | `approve_leave` | scope check |
| PUT | `/api/v1/leaves/{id}/reject` | `approve_leave` | scope check |
| POST | `/api/v1/attendance/checkin` | authenticated | self |
| GET | `/api/v1/attendance/heatmap` | authenticated | self/dept/all |
| GET | `/api/v1/departments/tree` | authenticated | org chart |
| WS | `/ws/notifications` | JWT param | real-time |
| GET | `/api/v1/notifications/` | authenticated | unread |
| GET | `/api/v1/audit-logs/` | `view_audit_log` | admin |
| GET | `/health` | — | DB ping |

---

## Phase 6 — DI Container

```python
# app/container.py — điểm duy nhất wire implementations
def get_notification_service() -> INotificationService:
    return TelegramNotificationService(settings.TELEGRAM_BOT_TOKEN, ws_manager)

def get_review_leave_use_case(db=Depends(get_db),
    notif=Depends(get_notification_service)) -> ReviewLeaveUseCase:
    return ReviewLeaveUseCase(
        leave_repo=SQLAlchemyLeaveRepository(db),
        user_repo=SQLAlchemyUserRepository(db),
        dept_repo=SQLAlchemyDepartmentRepository(db),
        rbac=RBACService(), tree=DepartmentTreeService(),
        notif=notif, audit_repo=SQLAlchemyAuditLogRepository(db),
    )
```

---

## Phase 7 — Database Seeding

**3 tài khoản demo:**

| Email | Password | Role | Đơn vị |
|-------|----------|------|--------|
| `admin@company.vn` | `Admin@123` | Admin | [Công ty] |
| `manager@company.vn` | `Manager@123` | Manager | [Phòng Z] |
| `employee@company.vn` | `Employee@123` | Employee | [Phòng Z] |

**Org 4 tầng (tên đơn vị ẩn vì bảo mật):**
```
[Công ty] (L1) → [Ban A]/[Ban B] (L2) → [Phòng X/Y/Z] (L3) → [Nhóm] (L4)
```

Dữ liệu: 10 users, 15 tasks (đủ status + priority), 5 leave requests, 30 ngày attendance, leave_balance, sample notifications.

---

## Phase 8 — Tests

### Unit (không cần DB)

```python
assert not rbac.has_permission(employee, "approve_leave")  # False
assert rbac.get_attendance_scope(manager) == "department"
assert tree.is_ancestor_of(parent_id, child_id, depts)    # True
assert not tree.is_ancestor_of(sibling_id, child_id, depts) # False
```

### Integration — 9 RBAC Scenarios

| # | Actor | Action | Expected |
|---|-------|--------|----------|
| S1 | employee | GET /users/ phòng khác | 403 |
| S2 | manager | PUT /leaves/{id}/approve cùng phòng | 200 |
| S3 | manager | PUT /leaves/{id}/approve phòng khác | 403 |
| S4 | employee | POST /tasks/ assign người khác | 403 |
| S5 | manager | PUT /tasks/{id}/assign cùng phòng | 200 |
| S6 | employee | POST /attendance/checkin | 200 |
| S7 | employee | GET /attendance/heatmap | chỉ data mình |
| S8 | manager | GET /attendance/heatmap | toàn phòng |
| S9 | employee | GET /audit-logs/ | 403 |

---

## Verification Plan

```bash
docker-compose up --build -d
docker-compose exec api bash migrations/run_migrations.sh   # 12 tables
docker-compose exec api python -m app.infrastructure.database.seed
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/ --cov=app --cov-report=term-missing           # ≥80%
# Swagger UI: http://localhost:8000/docs
docker-compose exec api bash migrations/run_migrations.sh   # idempotent check
```
