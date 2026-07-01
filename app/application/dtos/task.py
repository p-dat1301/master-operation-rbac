from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.domain.entities.task import Task, TaskPriority


class TaskOutput(BaseModel):
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
    updated_at: Optional[datetime] = None

    @classmethod
    def from_entity(cls, task) -> "TaskOutput":
        
        if not isinstance(task, Task):
            raise TypeError("Expected Task entity")
        return cls(
            id=task.id,
            task_code=task.task_code,
            title=task.title,
            description=task.description,
            assignee_id=task.assignee_id,
            assigner_id=task.assigner_id,
            department_id=task.department_id,
            status=task.status.value,
            priority=task.priority.value if isinstance(task.priority, TaskPriority) else task.priority,
            start_date=task.start_date,
            due_date=task.due_date,
            estimated_hours=task.estimated_hours,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )


class TaskCreateInput(BaseModel):
    task_code: str
    title: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    department_id: Optional[int] = None
    priority: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None


class AssignTaskInput(BaseModel):
    task_id: int
    assignee_id: int


class CompleteTaskInput(BaseModel):
    task_id: int


class TaskUpdateInput(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    department_id: Optional[int] = None
    priority: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None
