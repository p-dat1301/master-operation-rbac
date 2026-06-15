from __future__ import annotations

from datetime import date
from typing import Optional
from pydantic import BaseModel
from app.application.dtos.task import TaskCreateInput, TaskOutput


class TaskCreateRequest(TaskCreateInput):
    pass


class TaskResponse(TaskOutput):
    pass


class AssignTaskRequest(BaseModel):
    task_id: int
    assignee_id: int


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    department_id: Optional[int] = None
    priority: Optional[str] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None
