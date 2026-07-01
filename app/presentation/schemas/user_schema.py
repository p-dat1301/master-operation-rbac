from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from app.application.dtos.user import UserCreateInput, UserOutput


class UserResponse(UserOutput):
    pass
    


class UserCreateRequest(UserCreateInput):
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
