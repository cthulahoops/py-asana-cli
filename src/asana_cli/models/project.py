"""Project models for Asana."""

from datetime import date

from asana_cli.models.base import AsanaBaseModel, AsanaCompactModel


class ProjectCompact(AsanaCompactModel):
    """Compact project representation."""

    pass


class ProjectOwner(AsanaCompactModel):
    """Project owner representation."""

    pass


class Project(AsanaBaseModel):
    """Full project representation."""

    gid: str
    name: str
    resource_type: str | None = None
    archived: bool = False
    color: str | None = None
    created_at: str | None = None
    current_status: dict | None = None
    due_date: date | None = None
    due_on: date | None = None
    notes: str = ""
    owner: ProjectOwner | None = None
    public: bool = False
    start_on: date | None = None
    workspace: AsanaCompactModel | None = None
