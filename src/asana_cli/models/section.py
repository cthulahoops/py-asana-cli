"""Section models for Asana."""

from asana_cli.models.base import AsanaBaseModel, AsanaCompactModel


class SectionCompact(AsanaCompactModel):
    """Compact section representation."""

    pass


class Section(AsanaBaseModel):
    """Full section representation."""

    gid: str
    name: str
    resource_type: str | None = None
    created_at: str | None = None
    project: AsanaCompactModel | None = None
