from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, JSON, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base
from app.domain.entities.document import Document, DocumentStatus, DocumentVisibility, DocumentClassification

class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key = True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable = False)
    description: Mapped[Optional[str]] = mapped_column((String(1024)), nullable=True)

    store_bucket: Mapped[str] = mapped_column(String(100), nullable=False)
    store_object_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    path_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    size_byte: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.DRAFT)
    uploaded_by: Mapped[int] = mapped_column(Integer, nullable=False)
    visibility_scope: Mapped[DocumentVisibility] = mapped_column(Enum(DocumentVisibility), nullable=False)
    allowed_role_names: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    allowed_departments: Mapped[Optional[list[int]]] = mapped_column(JSON, nullable=True)
    class_document: Mapped[DocumentClassification] = mapped_column(Enum(DocumentClassification), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)