from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.domain.entities.user import User


class UserOutput(BaseModel):
    id: int
    employee_code: str
    email: EmailStr
    full_name: str
    role_name: str
    permissions: list[str] = Field(default_factory=list)
    phone: Optional[str] = None
    job_title: Optional[str] = None
    contact_type: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    hire_date: Optional[date] = None
    is_active: bool = True

    @classmethod
    def from_entity(cls, user) -> "UserOutput":
        if not isinstance(user, User):
            raise TypeError("Expected User entity")
        return cls(
            id=user.id,
            employee_code=user.employee_code,
            email=user.email,
            full_name=user.full_name,
            role_name=user.role_name,
            permissions=sorted(user.permissions),
            phone=user.phone,
            job_title=user.job_title,
            contact_type=user.contact_type,
            department_id=user.department_id,
            manager_id=user.manager_id,
            hire_date=user.hire_date,
            is_active=user.is_active,
        )


class UserCreateInput(BaseModel):
    employee_code: str
    email: EmailStr
    full_name: str
    password: str
    role_name: str
    phone: Optional[str] = None
    job_title: Optional[str] = None
    contact_type: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    hire_date: Optional[date] = None
    is_active: bool = True
