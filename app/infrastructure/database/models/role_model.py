"""ORM Model: roles"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.permission_model import PermissionModel
    from app.infrastructure.database.models.user_model import UserModel


class RoleModel(Base):
    """Bảng ``roles`` — lưu các vai trò trong hệ thống."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # --- relationships ---
    permissions: Mapped[List["PermissionModel"]] = relationship(
        "PermissionModel",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin",  # Eager-load khi nạp RoleModel
    )
    users: Mapped[List["UserModel"]] = relationship(
        "UserModel",
        back_populates="role",
        lazy="noload",
    )
