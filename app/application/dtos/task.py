from datetime import date
from typing import Optional

from pydantic import BaseModel

from app.domain.entities.task import Task


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
            status=task.status,
            priority=task.priority,
            start_date=task.start_date,
            due_date=task.due_date,
            estimated_hours=task.estimated_hours,
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
