"""Task models for Asana."""

from datetime import date, datetime

from asana_cli.models.base import AsanaBaseModel, AsanaCompactModel


class TaskCompact(AsanaCompactModel):
    """Compact task representation."""

    completed: bool = False
    resource_type: str | None = None


class Assignee(AsanaCompactModel):
    """Task assignee representation."""

    pass


class Task(AsanaBaseModel):
    """Full task representation."""

    gid: str
    name: str
    resource_type: str | None = None
    completed: bool = False
    completed_at: datetime | None = None
    created_at: datetime | None = None
    due_on: date | None = None
    due_at: datetime | None = None
    notes: str = ""
    assignee: Assignee | None = None
    parent: TaskCompact | None = None
    projects: list[AsanaCompactModel] = []
    memberships: list[dict] = []
    num_subtasks: int = 0
    permalink_url: str | None = None


class TaskCreateRequest(AsanaBaseModel):
    """Request model for creating a task."""

    name: str
    workspace: str | None = None
    projects: list[str] | None = None
    assignee: str | None = None
    due_on: date | None = None
    notes: str | None = None
    parent: str | None = None


class TaskUpdateRequest(AsanaBaseModel):
    """Request model for updating a task."""

    name: str | None = None
    completed: bool | None = None
    assignee: str | None = None
    due_on: date | None = None
    notes: str | None = None
