from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional 

@dataclass
class Attendance:
    id: int
    user_id: int
    date: date
    check_in: datetime
    check_out: Optional[datetime] = None
    total_minutes: Optional[int] = None
    ip_address: Optional[str] = None
    note: Optional[str] = None
    status: Optional[str] = None
    department_id: Optional[int] = None