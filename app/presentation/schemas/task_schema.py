from __future__ import annotations

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
