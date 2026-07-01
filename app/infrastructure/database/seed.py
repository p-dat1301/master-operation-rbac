"""Database seeding script — idempotent.

Chạy: python -m app.infrastructure.database.seed
"""
from __future__ import annotations

import asyncio
import random
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.department_model import DepartmentModel
from app.infrastructure.database.models.permission_model import PermissionModel
from app.infrastructure.database.models.role_model import RoleModel
from app.infrastructure.database.models.role_permission_model import RolePermissionModel
from app.infrastructure.database.models.user_model import UserModel
from app.infrastructure.database.models.attendance_model import AttendanceModel
from app.infrastructure.database.session import AsyncSessionLocal as async_session_factory
from app.infrastructure.security.bcrypt_service import BcryptService


# ------------------------------------------------------------------
# Seed data definitions
# ------------------------------------------------------------------

DEPARTMENTS: list[dict] = [
    {"id": 1, "name": "Engineering", "level": 1, "parent_id": None},
    {"id": 2, "name": "HR", "level": 1, "parent_id": None},
    {"id": 3, "name": "Sales", "level": 1, "parent_id": None},
    {"id": 4, "name": "Marketing", "level": 1, "parent_id": None},
    {"id": 5, "name": "Finance", "level": 1, "parent_id": None},
    {"id": 6, "name": "IT Support", "level": 1, "parent_id": None},
]

ROLES: list[dict] = [
    {"id": 1, "name": "admin", "display_name": "Administrator"},
    {"id": 2, "name": "manager", "display_name": "Manager"},
    {"id": 3, "name": "employee", "display_name": "Employee"},
]

PERMISSIONS: list[dict] = [
    {"id": 1, "code": "manage_org", "description": "Manage organization (users, roles, departments)"},
    {"id": 2, "code": "create_task", "description": "Create tasks"},
    {"id": 3, "code": "assign_task", "description": "Assign tasks to others"},
    {"id": 4, "code": "approve_leave", "description": "Approve or reject leave requests"},
    {"id": 5, "code": "view_attendance_all", "description": "View attendance for all departments"},
    {"id": 6, "code": "view_attendance_dept", "description": "View attendance for own department"},
    {"id": 7, "code": "audit:view", "description": "View audit logs"},
    {"id": 8, "code": "system.config.manage", "description": "Manage admin system configuration sync"},
    {"id": 9, "code": "upload_document", "description": "Upload and manage documents"},
    {"id": 10, "code": "read_document", "description": "Read documents"},
    {"id": 11, "code": "update_document", "description": "Update documents"},
    {"id": 12, "code": "delete_document", "description": "Delete documents"},
]

# role_id -> list of permission_ids
ROLE_PERMISSIONS: dict[int, list[int]] = {
    1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],   # admin: all
    2: [2, 3, 4, 6, 9, 10, 11, 12],               # manager: create_task, assign_task, approve_leave, view_attendance_dept, upload_document, document CRUD
    3: [],                                        # employee: no explicit permissions (self-scope by default)
}

DEMO_USERS: list[dict] = [
    {
        "id": 1,
        "employee_code": "EMP001",
        "email": "admin@company.vn",
        "full_name": "Admin User",
        "password": "Admin@123",
        "role_id": 1,
        "department_id": None,
        "manager_id": None,
    },
    {
        "id": 2,
        "employee_code": "EMP002",
        "email": "manager@company.vn",
        "full_name": "Manager User",
        "password": "Manager@123",
        "role_id": 2,
        "department_id": 1,  # Engineering
        "manager_id": 1,     # admin as manager
    },
    {
        "id": 3,
        "employee_code": "EMP003",
        "email": "employee@company.vn",
        "full_name": "Employee User",
        "password": "Employee@123",
        "role_id": 3,
        "department_id": 1,  # Engineering
        "manager_id": 2,     # manager as direct manager
    },
    {
        "id": 4,
        "employee_code": "EMP004",
        "email": "alice@company.vn",
        "full_name": "Alice Pham",
        "password": "Employee@123",
        "role_id": 2,  # HR Manager
        "department_id": 2,  # HR
        "manager_id": 1,
    },
    {
        "id": 5,
        "employee_code": "EMP005",
        "email": "bob@company.vn",
        "full_name": "Bob Nguyen",
        "password": "Employee@123",
        "role_id": 3,  # Employee
        "department_id": 2,  # HR
        "manager_id": 4,
    },
    {
        "id": 6,
        "employee_code": "EMP006",
        "email": "charlie@company.vn",
        "full_name": "Charlie Tran",
        "password": "Employee@123",
        "role_id": 2,  # Sales Manager
        "department_id": 3,  # Sales
        "manager_id": 1,
    },
    {
        "id": 7,
        "employee_code": "EMP007",
        "email": "david@company.vn",
        "full_name": "David Le",
        "password": "Employee@123",
        "role_id": 3,  # Sales Employee
        "department_id": 3,  # Sales
        "manager_id": 6,
    },
    {
        "id": 8,
        "employee_code": "EMP008",
        "email": "eva@company.vn",
        "full_name": "Eva Vu",
        "password": "Employee@123",
        "role_id": 3,
        "department_id": 4,  # Marketing
        "manager_id": 1,
    },
    {
        "id": 9,
        "employee_code": "EMP009",
        "email": "frank@company.vn",
        "full_name": "Frank Do",
        "password": "Employee@123",
        "role_id": 3,
        "department_id": 6,  # IT Support
        "manager_id": 1,
    },
    {
        "id": 10,
        "employee_code": "EMP010",
        "email": "grace@company.vn",
        "full_name": "Grace Trinh",
        "password": "Employee@123",
        "role_id": 2,  # Finance Manager
        "department_id": 5,  # Finance
        "manager_id": 1,
    },
    {
        "id": 11,
        "employee_code": "EMP011",
        "email": "helen@company.vn",
        "full_name": "Helen Ngo",
        "password": "Employee@123",
        "role_id": 3,
        "department_id": 5,  # Finance Employee
        "manager_id": 10,
    },
]


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

async def _seed_departments(session: AsyncSession) -> None:
    for data in DEPARTMENTS:
        stmt = select(DepartmentModel).where(DepartmentModel.id == data["id"])
        result = await session.execute(stmt)
        if result.scalars().first() is None:
            session.add(DepartmentModel(**data))
    await session.flush()
    print("  [seed] departments OK")


async def _seed_roles(session: AsyncSession) -> None:
    for data in ROLES:
        stmt = select(RoleModel).where(RoleModel.id == data["id"])
        result = await session.execute(stmt)
        if result.scalars().first() is None:
            session.add(RoleModel(**data))
    await session.flush()
    print("  [seed] roles OK")


async def _seed_permissions(session: AsyncSession) -> None:
    for data in PERMISSIONS:
        stmt = select(PermissionModel).where(PermissionModel.id == data["id"])
        result = await session.execute(stmt)
        if result.scalars().first() is None:
            session.add(PermissionModel(**data))
    await session.flush()
    print("  [seed] permissions OK")


async def _seed_role_permissions(session: AsyncSession) -> None:
    for role_id, perm_ids in ROLE_PERMISSIONS.items():
        for perm_id in perm_ids:
            stmt = select(RolePermissionModel).where(
                RolePermissionModel.role_id == role_id,
                RolePermissionModel.permission_id == perm_id,
            )
            result = await session.execute(stmt)
            if result.scalars().first() is None:
                session.add(RolePermissionModel(role_id=role_id, permission_id=perm_id))
    await session.flush()
    print("  [seed] role_permissions OK")


async def _seed_users(session: AsyncSession) -> None:
    bcrypt = BcryptService()
    for data in DEMO_USERS:
        stmt = select(UserModel).where(UserModel.id == data["id"])
        result = await session.execute(stmt)
        if result.scalars().first() is None:
            user_data = {k: v for k, v in data.items() if k != "password"}
            user_data["hashed_password"] = bcrypt.hash(data["password"])
            user_data["is_active"] = True
            user_data["hire_date"] = date(2024, 1, 1)
            session.add(UserModel(**user_data))
    await session.flush()
    print("  [seed] users OK")


async def _seed_attendance(session: AsyncSession) -> None:
    today = date.today()
    start_date = today - timedelta(days=30)
    
    stmt = select(UserModel)
    res = await session.execute(stmt)
    users = res.scalars().all()
    
    print(f"  [seed] seeding attendance for {len(users)} users over the past 30 days...")
    
    for user in users:
        for i in range(31):
            day = start_date + timedelta(days=i)
            if day == today:
                continue
                
            check_stmt = select(AttendanceModel).where(
                AttendanceModel.user_id == user.id,
                AttendanceModel.date == day
            )
            existing = await session.execute(check_stmt)
            if existing.scalars().first() is not None:
                continue

            is_weekend = day.weekday() in (5, 6)
            
            if is_weekend:
                # 90% chance of no record on weekends
                if random.random() > 0.1:
                    continue
                # Weekend overtime
                check_in_hour = random.randint(8, 10)
                check_in_min = random.randint(0, 59)
                check_in_dt = datetime(day.year, day.month, day.day, check_in_hour, check_in_min, tzinfo=timezone.utc)
                hours_worked = random.uniform(8.0, 9.5)
                check_out_dt = check_in_dt + timedelta(hours=hours_worked)
                total_mins = int(hours_worked * 60)
                
                session.add(AttendanceModel(
                    user_id=user.id,
                    date=day,
                    check_in=check_in_dt,
                    check_out=check_out_dt,
                    total_minutes=total_mins,
                    ip_address="127.0.0.1",
                    department_id=user.department_id,
                    status="checked_out",
                    note="Làm thêm cuối tuần"
                ))
            else:
                rand = random.random()
                if rand < 0.08:
                    # Absent / Short hours (Red)
                    session.add(AttendanceModel(
                        user_id=user.id,
                        date=day,
                        check_in=datetime(day.year, day.month, day.day, 8, 0, tzinfo=timezone.utc),
                        check_out=datetime(day.year, day.month, day.day, 10, 30, tzinfo=timezone.utc),
                        total_minutes=150,
                        ip_address="127.0.0.1",
                        department_id=user.department_id,
                        status="absent",
                        note="Số giờ công quá thấp"
                    ))
                elif rand < 0.18:
                    # Short shift (Yellow)
                    check_in_hour = random.randint(9, 11)
                    check_in_min = random.randint(0, 59)
                    check_in_dt = datetime(day.year, day.month, day.day, check_in_hour, check_in_min, tzinfo=timezone.utc)
                    hours_worked = random.uniform(4.0, 6.0)
                    check_out_dt = check_in_dt + timedelta(hours=hours_worked)
                    total_mins = int(hours_worked * 60)
                    
                    session.add(AttendanceModel(
                        user_id=user.id,
                        date=day,
                        check_in=check_in_dt,
                        check_out=check_out_dt,
                        total_minutes=total_mins,
                        ip_address="127.0.0.1",
                        department_id=user.department_id,
                        status="checked_out",
                        note="Về sớm / Đi muộn"
                    ))
                else:
                    # Regular shift (Green)
                    check_in_hour = 8
                    check_in_min = random.randint(0, 30)
                    check_in_dt = datetime(day.year, day.month, day.day, check_in_hour, check_in_min, tzinfo=timezone.utc)
                    hours_worked = random.uniform(8.0, 9.5)
                    check_out_dt = check_in_dt + timedelta(hours=hours_worked)
                    total_mins = int(hours_worked * 60)
                    
                    session.add(AttendanceModel(
                        user_id=user.id,
                        date=day,
                        check_in=check_in_dt,
                        check_out=check_out_dt,
                        total_minutes=total_mins,
                        ip_address="127.0.0.1",
                        department_id=user.department_id,
                        status="checked_out",
                        note="Đạt tiêu chuẩn ca làm"
                    ))
    await session.flush()
    print("  [seed] attendance OK")


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

async def seed_all() -> None:
    print("[seed] Starting database seeding...")
    async with async_session_factory() as session:
        async with session.begin():
            await _seed_departments(session)
            await _seed_roles(session)
            await _seed_permissions(session)
            await _seed_role_permissions(session)
            await _seed_users(session)
            await _seed_attendance(session)
    print("[seed] Done.")


if __name__ == "__main__":
    asyncio.run(seed_all())
