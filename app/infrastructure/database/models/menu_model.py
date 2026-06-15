from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class MenuModel(Base):
    __tablename__ = "menus"
    __table_args__ = (
        UniqueConstraint("key", name="uq_menu_key"),
        UniqueConstraint("route", name="uq_menu_route"),
        Index("ix_menus_parent_key", "parent_key"),
        Index("ix_menus_permission_key", "permission_key"),
        Index("ix_menus_order", "order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(120), nullable=False)
    parent_key: Mapped[str | None] = mapped_column(ForeignKey("menus.key"), nullable=True)
    title_key: Mapped[str] = mapped_column(String(180), nullable=False)
    route: Mapped[str | None] = mapped_column(String(255), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(80), nullable=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    permission_key: Mapped[str | None] = mapped_column(ForeignKey("permissions.code"), nullable=True)
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_external: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
