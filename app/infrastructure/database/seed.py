"""Database seeding script — idempotent.

Chạy: python -m app.infrastructure.database.seed
"""
from __future__ import annotations

import asyncio
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.department_model import DepartmentModel
from app.infrastructure.database.models.permission_model import PermissionModel
from app.infrastructure.database.models.role_model import RoleModel
from app.infrastructure.database.models.role_permission_model import RolePermissionModel
from app.infrastructure.database.models.user_model import UserModel
from app.infrastructure.database.session import AsyncSessionLocal as async_session_factory
from app.infrastructure.security.bcrypt_service import BcryptService


# ------------------------------------------------------------------
# Seed data definitions
# ------------------------------------------------------------------

DEPARTMENTS: list[dict] = [
    {"id": 1, "name": "Engineering", "level": 1, "parent_id": None},
    {"id": 2, "name": "HR", "level": 1, "parent_id": None},
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
]

# role_id -> list of permission_ids
ROLE_PERMISSIONS: dict[int, list[int]] = {
    1: [1, 2, 3, 4, 5, 6, 7, 8],      # admin: all
    2: [2, 3, 4, 6],                # manager: create_task, assign_task, approve_leave, view_attendance_dept
    3: [],                          # employee: no explicit permissions (self-scope by default)
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
        "manager_id": 1,     # admin as manager (for hierarchy)
    },
    {
        "id": 3,
        "employee_code": "EMP003",
        "email": "employee@company.vn",
        "full_name": "Employee User",
        "password": "Employee@123",
        "role_id": 3,
        "department_id": 1,  # Engineering (same dept as manager for S2 testing)
        "manager_id": 2,     # manager as direct manager
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
    print("[seed] Done.")


if __name__ == "__main__":
    asyncio.run(seed_all())
