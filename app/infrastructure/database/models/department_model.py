"""ORM Model: departments"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.user_model import UserModel


class DepartmentModel(Base):
    """Bảng ``departments`` — cây phân cấp phòng ban tối đa 4 cấp."""

    __tablename__ = "departments"
    __table_args__ = (
        CheckConstraint("level BETWEEN 1 AND 4", name="ck_departments_level"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Self-referential
    children: Mapped[List["DepartmentModel"]] = relationship(
        "DepartmentModel",
        back_populates="parent",
        lazy="noload",
    )
    parent: Mapped[Optional["DepartmentModel"]] = relationship(
        "DepartmentModel",
        back_populates="children",
        remote_side="DepartmentModel.id",
        lazy="noload",
    )
    users: Mapped[List["UserModel"]] = relationship(
        "UserModel",
        back_populates="department",
        lazy="noload",
    )
