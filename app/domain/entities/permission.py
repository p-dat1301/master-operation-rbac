from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Permission:
    id: int
    code: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None