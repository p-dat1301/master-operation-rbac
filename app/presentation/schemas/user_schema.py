from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    employee_code: str
    email: str
    full_name: str
    role_name: str
    permissions: List[str]
    phone: Optional[str] = None
    job_title: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    is_active: bool = True

    @classmethod
    def from_entity(cls, user) -> "UserResponse":
        return cls(
            id=user.id,
            employee_code=user.employee_code,
            email=user.email,
            full_name=user.full_name,
            role_name=user.role_name,
            permissions=list(user.permissions) if hasattr(user, 'permissions') and user.permissions else [],
            phone=user.phone,
            job_title=user.job_title,
            department_id=user.department_id,
            manager_id=user.manager_id,
            is_active=user.is_active,
        )


class UserCreateRequest(BaseModel):
    employee_code: str
    email: str
    full_name: str
    password: str
    role_name: str
    department_id: Optional[int] = None


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    contact_type: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None
