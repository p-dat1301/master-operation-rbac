from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum

class DocumentStatus(str, Enum):
    DRAFT = "draft"
    UPLOADED = "uploaded"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"

class DocumentVisibility(str, Enum):
    PUBLIC = "public"
    COMPANY = "company"
    DEPARTMENT = "department"
    ROLE = "role"
    OWNER = "owner"
    MANAGER_SUBTREE = "manager_subtree"

class DocumentClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

@dataclass
class Document:
    id: int
    title: str
    store_bucket: str
    store_object_key: str
    path_filename: str
    size_byte: int
    status: DocumentStatus
    uploaded_by: int
    visibility_scope: DocumentVisibility
    class_document: DocumentClassification

    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    allowed_role_names: set[str] = field(default_factory=set)
    allowed_departments: set[int] = field(default_factory=set)