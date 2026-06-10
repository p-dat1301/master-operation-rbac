from __future__ import annotations

from pydantic import BaseModel


class I18nSyncRequest(BaseModel):
    dry_run: bool = False


class I18nSyncResponse(BaseModel):
    resource: str
    created: int
    updated: int
    skipped: int
    errors: list[str]
    dry_run: bool

    @classmethod
    def from_dto(cls, dto) -> "I18nSyncResponse":
        return cls(
            resource=dto.resource,
            created=dto.created,
            updated=dto.updated,
            skipped=dto.skipped,
            errors=dto.errors,
            dry_run=dto.dry_run,
        )
