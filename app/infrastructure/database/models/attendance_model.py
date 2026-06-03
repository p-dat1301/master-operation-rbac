"""ORM Model: attendances"""
from __future__ import annotations

from datetime import date, datetime, time
from typing import Optional

from sqlalchemy import Date, ForeignKey, String, Time, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class AttendanceModel(Base):
    """Bảng ``attendances`` — lịch sử chấm công."""

    __tablename__ = "attendances"
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_attendances_user_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    check_in: Mapped[Optional[time]] = mapped_column(Time)
    check_out: Mapped[Optional[time]] = mapped_column(Time)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(20), default="present", nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
