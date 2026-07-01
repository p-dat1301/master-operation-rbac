from __future__ import annotations

from pydantic import BaseModel

from app.application.dtos.menu_sync import MenuSyncSummary


class MenuSyncRequest(BaseModel):
    dry_run: bool = False


class MenuSyncResponse(MenuSyncSummary):
    pass
