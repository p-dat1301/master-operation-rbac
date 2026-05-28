from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass
class Task:
    id: int
    task_code: str
    title: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    assigner_id: Optional[int] = None
    department_id: Optional[int] = None
    status: str = "backlog"
    priority: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    created_at: Optional[datetime] = None