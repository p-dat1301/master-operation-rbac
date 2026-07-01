from __future__ import annotations

from app.application.dtos.task import AssignTaskInput, TaskCreateInput, TaskOutput, TaskUpdateInput


class TaskCreateRequest(TaskCreateInput):
    pass


class TaskResponse(TaskOutput):
    pass


class AssignTaskRequest(AssignTaskInput):
    pass


class TaskUpdateRequest(TaskUpdateInput):
    pass
