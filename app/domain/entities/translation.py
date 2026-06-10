from dataclasses import dataclass
from datetime import datetime


@dataclass
class Translation:
    id: int
    locale: str
    key: str
    value: str
    namespace: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
