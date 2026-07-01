from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Task:
    id: int
    task_code: str
    title: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    assigner_id: Optional[int] = None
    department_id: Optional[int] = None
    status: TaskStatus = TaskStatus.TODO
    priority: Optional[TaskPriority] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
