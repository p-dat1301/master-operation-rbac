"""ORM Model: users — với Eager-Load role → permissions."""
from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.role_model import RoleModel
    from app.infrastructure.database.models.department_model import DepartmentModel


class UserModel(Base):
    """Bảng ``users``.

    Quan trọng: relationship ``role`` được load với ``lazy="selectin"`` để
    Repository có thể map sang Domain Entity ``User`` (bao gồm ``permissions``)
    chỉ trong 2 câu truy vấn (user + role_with_permissions) — tránh N+1.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    job_title: Mapped[Optional[str]] = mapped_column(String(100))
    contact_type: Mapped[Optional[str]] = mapped_column(String(50))
    hire_date: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    department_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL")
    )
    manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    # -----------------------------------------------------------------
    # Eager-Load chain: user → role → permissions
    # lazy="selectin" phát thêm 1 câu SELECT IN (không phải JOIN)
    # để tải RoleModel kèm theo permissions ngay khi UserModel được load.
    # -----------------------------------------------------------------
    role: Mapped["RoleModel"] = relationship(
        "RoleModel",
        back_populates="users",
        lazy="selectin",  # ← Eager-load role (và permissions qua RoleModel.permissions)
    )
    department: Mapped[Optional["DepartmentModel"]] = relationship(
        "DepartmentModel",
        back_populates="users",
        lazy="noload",
    )
    manager: Mapped[Optional["UserModel"]] = relationship(
        "UserModel",
        remote_side="UserModel.id",
        lazy="noload",
    )
