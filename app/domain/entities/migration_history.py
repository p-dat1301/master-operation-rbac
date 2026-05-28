from dataclasses import dataclass
from datetime import datetime

@dataclass
class MigrationHistory:
    id: int
    filename: str
    applied_at: datetime | None = None