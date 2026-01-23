"""API response models for Asana."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class NextPage(BaseModel):
    """Pagination info."""

    model_config = ConfigDict(extra="ignore")

    offset: str
    path: str
    uri: str


class AsanaResponse(BaseModel, Generic[T]):
    """Standard Asana API response wrapper."""

    model_config = ConfigDict(extra="ignore")

    data: T
    next_page: NextPage | None = None


class AsanaListResponse(BaseModel, Generic[T]):
    """Asana API response for list endpoints."""

    model_config = ConfigDict(extra="ignore")

    data: list[T]
    next_page: NextPage | None = None


class AsanaError(BaseModel):
    """Asana API error response."""

    model_config = ConfigDict(extra="ignore")

    message: str
    help: str | None = None
    phrase: str | None = None


class AsanaErrorResponse(BaseModel):
    """Asana API error wrapper."""

    model_config = ConfigDict(extra="ignore")

    errors: list[AsanaError]
