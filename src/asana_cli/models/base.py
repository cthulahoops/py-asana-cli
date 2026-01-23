"""Base Pydantic models for Asana entities."""

from pydantic import BaseModel, ConfigDict


class AsanaBaseModel(BaseModel):
    """Base model for all Asana entities."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
    )


class AsanaCompactModel(AsanaBaseModel):
    """Compact representation of an Asana resource (gid + name)."""

    gid: str
    name: str


class AsanaResourceModel(AsanaBaseModel):
    """Base model for Asana resources with gid and resource_type."""

    gid: str
    resource_type: str | None = None
