from dataclasses import dataclass
from datetime import datetime


@dataclass
class Menu:
    id: int
    key: str
    parent_key: str | None
    title_key: str
    route: str | None
    icon: str | None
    order: int
    permission_key: str | None
    is_visible: bool
    is_external: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
