from dataclasses import dataclass
from datetime import datetime

@dataclass
class LeaveBalance:
    id: int
    user_id: int
    year: int
    total_days: float
    used_days: float
    pending_days: float
    remaining_days: float
    updated_at: datetime | None = None