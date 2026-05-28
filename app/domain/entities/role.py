from dataclasses import dataclass
from datetime import datetime

@dataclass
class Role:
    id: int
    name: str
    display_name: str
    created_at: datetime | None = None