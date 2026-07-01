from __future__ import annotations

from typing import Optional, List

from fastapi import Form

from app.application.dtos.document import (
    DocumentCreateInput,
    DocumentDetailOutput,
    DocumentListOutput,
    DocumentSearchParams,
    DocumentUpdateInput,
)
from app.domain.entities.document import DocumentVisibility, DocumentClassification


class DocumentCreateRequest(DocumentCreateInput):
    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: Optional[str] = Form(None),
        visibility_scope: DocumentVisibility = Form(...),
        allowed_role_names: List[str] | None = Form(None),
        allowed_departments: List[int] | None = Form(None),
        class_document: DocumentClassification = Form(...),
    ) -> DocumentCreateRequest:
        roles = [r.strip() for r in (allowed_role_names or []) if r and r.strip()]
        depts = [int(d) for d in (allowed_departments or []) if d]
        return cls(
            title=title,
            description=description,
            visibility_scope=visibility_scope,
            allowed_role_names=roles,
            allowed_departments=depts,
            class_document=class_document,
        )


class DocumentListResponse(DocumentListOutput):
    pass


class DocumentDetailResponse(DocumentDetailOutput):
    pass


DocumentResponse = DocumentDetailResponse


class DocumentUpdateRequest(DocumentUpdateInput):
    pass


class DocumentSearchQuery(DocumentSearchParams):
    pass

