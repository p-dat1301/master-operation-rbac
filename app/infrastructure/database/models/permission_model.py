"""ORM Model: permissions"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.role_model import RoleModel


class PermissionModel(Base):
    """Bảng ``permissions`` — lưu các mã quyền (permission codes).

    Ví dụ ``code``: ``"task:create"``, ``"leave:approve"``,
    ``"attendance:view_all"``.
    """

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # --- relationships ---
    roles: Mapped[List["RoleModel"]] = relationship(
        "RoleModel",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="noload",
    )
