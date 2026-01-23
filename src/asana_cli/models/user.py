"""User models for Asana."""

from asana_cli.models.base import AsanaBaseModel, AsanaCompactModel


class UserCompact(AsanaCompactModel):
    """Compact user representation."""

    pass


class Workspace(AsanaCompactModel):
    """Workspace representation."""

    pass


class User(AsanaBaseModel):
    """Full user representation."""

    gid: str
    name: str
    email: str | None = None
    resource_type: str | None = None
    workspaces: list[Workspace] = []
