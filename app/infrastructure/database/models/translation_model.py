from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class TranslationModel(Base):
    __tablename__ = "translations"
    __table_args__ = (
        UniqueConstraint("locale", "key", name="uq_translation_locale_key"),
        Index("ix_translations_locale", "locale"),
        Index("ix_translations_namespace", "namespace"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    locale: Mapped[str] = mapped_column(String(16), nullable=False)
    key: Mapped[str] = mapped_column(String(180), nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    namespace: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
