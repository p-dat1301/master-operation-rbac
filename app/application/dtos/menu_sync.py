from __future__ import annotations

from pydantic import BaseModel


class MenuSyncSummary(BaseModel):
    resource: str
    created: int
    updated: int
    skipped: int
    errors: list[str]
    dry_run: bool
